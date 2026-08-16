"""Validation tests for the static site in www/.

This repo has no package manager and no build step on purpose, so these tests
use the standard library only:

    python3 -m unittest discover -s tests

Every failure mode here is silent in a browser -- a renamed image or a stale
canonical URL renders without an error -- so the checks lean toward asserting
that references actually resolve on disk.
"""

import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parent.parent
WWW = REPO / "www"
INDEX = WWW / "index.html"
CSS = WWW / "css" / "homepage.css"
MANIFEST = WWW / "site.webmanifest"
CNAME = WWW / "CNAME"

# Glyphs used purely as visual affordances. A <span> holding nothing but these
# is decoration and must be hidden from assistive tech.
DECORATIVE_GLYPHS = set("↗↘↖↙↑↓←→•·|—")


class SiteParser(HTMLParser):
    """Collects the handful of things the tests below assert on."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = []  # (tag, attr, value)
        self.ids = set()
        self.classes = set()
        self.images = []
        self.anchors = []
        self.metas = []
        self.spans = []  # (attrs, text)
        self.title = ""
        self._span_stack = []
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        self.classes.update((a.get("class") or "").split())
        for attr in ("href", "src"):
            if attr in a:
                self.refs.append((tag, attr, a[attr]))
        if tag == "img":
            self.images.append(a)
        elif tag == "a":
            self.anchors.append(a)
        elif tag == "meta":
            self.metas.append(a)
        elif tag == "title":
            self._in_title = True
        elif tag == "span":
            self._span_stack.append([a, ""])

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "span" and self._span_stack:
            attrs, text = self._span_stack.pop()
            self.spans.append((attrs, text))

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._span_stack:
            self._span_stack[-1][1] += data


def parse_index():
    parser = SiteParser()
    parser.feed(INDEX.read_text(encoding="utf-8"))
    parser.close()
    return parser


def is_local(value):
    """True if the reference points at a file this repo ships."""
    if not value or value.startswith("#"):
        return False
    return not urlparse(value).scheme


def local_path(value):
    """Strip fragment/query so the remainder can be resolved on disk."""
    return value.split("#")[0].split("?")[0]


PAGE = parse_index()
META_BY_NAME = {m["name"]: m.get("content", "") for m in PAGE.metas if "name" in m}
META_BY_PROP = {m["property"]: m.get("content", "") for m in PAGE.metas if "property" in m}


class TestReferences(unittest.TestCase):
    """Assets and anchors referenced by index.html must actually resolve."""

    def test_local_references_exist(self):
        for tag, attr, value in PAGE.refs:
            if not is_local(value):
                continue
            path = local_path(value)
            if not path:
                continue
            with self.subTest(ref=value):
                self.assertTrue(
                    (WWW / path).exists(),
                    f"<{tag} {attr}=\"{value}\"> does not resolve to a file in www/",
                )

    def test_no_absolute_local_paths(self):
        """`/Resume.pdf` works on App Engine and 404s on GitHub Pages.

        The same www/ directory is published both ways, so local references
        have to be relative to survive on both. See CLAUDE.md.
        """
        for tag, attr, value in PAGE.refs:
            if is_local(value):
                with self.subTest(ref=value):
                    self.assertFalse(
                        value.startswith("/"),
                        f"<{tag} {attr}=\"{value}\"> is an absolute path; "
                        "App Engine resolves it but GitHub Pages will not",
                    )

    def test_fragment_links_resolve(self):
        for value in (v for _, attr, v in PAGE.refs if attr == "href" for v in [v]):
            if value.startswith("#") and len(value) > 1:
                with self.subTest(fragment=value):
                    self.assertIn(
                        value[1:], PAGE.ids, f"{value} has no matching id in index.html"
                    )

    def test_blank_targets_have_noopener(self):
        for a in PAGE.anchors:
            if a.get("target") == "_blank":
                with self.subTest(href=a.get("href")):
                    self.assertIn(
                        "noopener",
                        a.get("rel", ""),
                        f"target=_blank on {a.get('href')} needs rel=noopener",
                    )


class TestMetadata(unittest.TestCase):
    """CLAUDE.md asks editors to keep these in sync by hand; assert it instead."""

    def canonical(self):
        for tag, attr, value in PAGE.refs:
            if tag == "link" and attr == "href" and value.startswith("http"):
                return value
        self.fail("no canonical link found")

    def test_titles_agree(self):
        title = PAGE.title.strip()
        self.assertTrue(title, "index.html has an empty <title>")
        self.assertEqual(title, META_BY_PROP.get("og:title"), "og:title differs from <title>")
        self.assertEqual(title, META_BY_NAME.get("twitter:title"), "twitter:title differs from <title>")

    def test_canonical_matches_og_url(self):
        self.assertEqual(self.canonical(), META_BY_PROP.get("og:url"))

    def test_social_descriptions_agree(self):
        # The name=description meta is intentionally longer for search results,
        # so only the two social variants are compared.
        self.assertEqual(
            META_BY_PROP.get("og:description"), META_BY_NAME.get("twitter:description")
        )
        self.assertTrue(META_BY_NAME.get("description", "").strip(), "empty meta description")

    def test_social_images_are_absolute_and_present(self):
        canonical_host = urlparse(self.canonical()).netloc
        for key, value in (
            ("og:image", META_BY_PROP.get("og:image")),
            ("twitter:image", META_BY_NAME.get("twitter:image")),
        ):
            with self.subTest(meta=key):
                self.assertTrue(value, f"{key} is missing")
                parts = urlparse(value)
                self.assertEqual(parts.scheme, "https", f"{key} must be an absolute https URL")
                self.assertEqual(parts.netloc, canonical_host, f"{key} host differs from canonical")
                self.assertTrue(
                    (WWW / parts.path.lstrip("/")).exists(),
                    f"{key} points at {parts.path}, which is not in www/",
                )

    def test_theme_color_matches_manifest(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(
            META_BY_NAME.get("theme-color"),
            manifest.get("theme_color"),
            "meta theme-color and site.webmanifest theme_color disagree",
        )

    def test_manifest_icons_exist(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        icons = manifest.get("icons", [])
        self.assertTrue(icons, "site.webmanifest declares no icons")
        for icon in icons:
            with self.subTest(icon=icon.get("src")):
                self.assertTrue(
                    (WWW / icon["src"]).exists(), f"manifest icon {icon['src']} missing from www/"
                )


class TestAccessibility(unittest.TestCase):
    """Guards the a11y scaffolding CLAUDE.md tells future editors to preserve."""

    def test_skip_link_targets_real_id(self):
        targets = [
            a["href"]
            for a in PAGE.anchors
            if "skip-link" in (a.get("class") or "") and "href" in a
        ]
        self.assertEqual(len(targets), 1, "expected exactly one .skip-link")
        self.assertTrue(targets[0].startswith("#"))
        self.assertIn(targets[0][1:], PAGE.ids)

    def test_images_have_alt_text(self):
        self.assertTrue(PAGE.images, "no images found; parser may be broken")
        for img in PAGE.images:
            with self.subTest(src=img.get("src")):
                self.assertTrue(
                    img.get("alt", "").strip(), f"{img.get('src')} is missing alt text"
                )

    def test_decorative_spans_are_hidden(self):
        for attrs, text in PAGE.spans:
            stripped = text.strip()
            if stripped and set(stripped) <= DECORATIVE_GLYPHS:
                with self.subTest(glyph=stripped):
                    self.assertEqual(
                        attrs.get("aria-hidden"),
                        "true",
                        f'decorative span "{stripped}" needs aria-hidden="true"',
                    )


class TestStyles(unittest.TestCase):
    def test_html_classes_are_defined_in_css(self):
        css = CSS.read_text(encoding="utf-8")
        # Leading [_a-zA-Z] keeps this from matching decimals like `.8fr`.
        defined = set(re.findall(r"\.(-?[_a-zA-Z][\w-]*)", css))
        for name in sorted(PAGE.classes):
            with self.subTest(css_class=name):
                self.assertIn(name, defined, f'class "{name}" is used in HTML but absent from CSS')


class TestPagesConfig(unittest.TestCase):
    # www/CNAME is absent until the apex DNS is repointed at GitHub, so this
    # check lies dormant rather than failing. It activates when the file lands.
    @unittest.skipUnless(CNAME.exists(), "www/CNAME not present; no Pages custom domain")
    def test_cname_is_a_bare_hostname_matching_canonical(self):
        raw = CNAME.read_text(encoding="utf-8")
        lines = [line for line in raw.splitlines() if line.strip()]
        self.assertEqual(len(lines), 1, "CNAME must contain exactly one hostname")
        host = lines[0].strip()
        self.assertNotIn("/", host, "CNAME must be a bare hostname, not a URL")
        self.assertNotIn(":", host, "CNAME must not include a scheme or port")

        canonical_host = None
        for tag, attr, value in PAGE.refs:
            if tag == "link" and attr == "href" and value.startswith("http"):
                canonical_host = urlparse(value).netloc
                break
        self.assertEqual(
            host, canonical_host, "CNAME hostname differs from the canonical URL in index.html"
        )


if __name__ == "__main__":
    unittest.main()
