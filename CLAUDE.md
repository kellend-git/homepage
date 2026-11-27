# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Kellen Donohue's personal homepage: a hand-written static site. No build step, no
package manager, no third-party dependencies. Everything served lives in `www/`;
files at the repo root are deployment config or tests.

The homepage lives in `www/index.html` and `www/css/homepage.css`. Shared navigation uses `www/js/site-header.js`.

## Local preview

```sh
python3 -m http.server -d www 8000   # then open http://localhost:8000
```

Check both breakpoints, the sticky header, the `#work`/`#education`/`#research`
anchor scrolling, and the `.skip-link` on keyboard focus.

Careful with headless screenshots: Chrome clamps its window to a ~500px minimum,
so `--window-size=390` lays out at 500px and then crops the PNG to 390, which
fakes a horizontal overflow that isn't there. Measure `scrollWidth` against
`clientWidth` if you need to know.

## Tests

```sh
python3 -m unittest discover -s tests                   # all checks
python3 -m unittest tests.test_site.TestMetadata -v     # one class
python3 -m unittest tests.test_site.TestReferences.test_no_absolute_local_paths
```

`tests/test_site.py` uses only `unittest` and `html.parser`. No pytest, so the
repo stays free of a package manager. It parses `www/index.html` once at import
and asserts on the result.

The `validate` job in `.github/workflows/pages.yml` runs it and gates `deploy`,
so a broken reference fails the workflow instead of shipping. What it covers:

- Every relative `href`/`src` resolves to a real file in `www/`, and no local
  reference is absolute.
- `<title>`, `og:title`, and `twitter:title` agree; `canonical` matches `og:url`;
  social images are absolute URLs on the canonical host that exist on disk;
  `meta theme-color` matches `site.webmanifest`.
- a11y invariants: one `.skip-link` pointing at a real `id`, non-empty `alt` on
  every image, `aria-hidden` on spans holding only decorative glyphs, and
  `rel=noopener` on every `target="_blank"`.
- Every class used in the HTML exists in `homepage.css`. One dormant check
  validates `www/CNAME` and skips while that file is absent.

Two omissions on purpose. `name="description"` is longer than `og:description` by
design, so only the two social variants get compared. External links aren't
checked at all: LinkedIn and lens.org return 403 to CI, which would make the gate
flaky without adding signal.

When you add a check, mutation-test it. Break the thing in a scratch copy and
confirm the suite goes red. A check that can't fail is worse than no check.

## Hosting

`.github/workflows/pages.yml` validates pull requests and pushes to `master`. Successful runs on `master` publish `www/` to GitHub Pages. The workflow also supports manual runs.

The deploy job copies `www/KellenDonohueResume.pdf` to `www/Resume.pdf` before upload so the legacy URL always serves the current PDF. Use relative paths for local assets.

Cloudflare handles DNS for `kellend.com` and `kellendonohue.com`. GitHub Pages uses `kellend.com` as its custom domain. The other three hostnames redirect to `https://kellend.com/`.

Keep the canonical URL and social metadata in `www/index.html` aligned with `https://kellend.com`, and regenerate `www/og.png` if the tagline changes.

## CSS conventions

`www/css/homepage.css` is hand-maintained in a compressed style. Each logical
section (header, hero, portrait, metrics, timeline, education, research,
contact/footer, then media queries) is a single long line with no spaces after `:`
or `;`. Match that format. A prettified rewrite makes every future diff
unreadable.

- All color, `--shell` width, and `--radius` values come from the `:root` custom
  properties. Add a variable instead of hardcoding a new hex.
- Two breakpoints only: `max-width:900px` (drops the nav links, tightens the hero
  grid) and `max-width:700px` (single column throughout). A third
  `prefers-reduced-motion` block disables smooth scroll and transitions.
- The layout is CSS grid with matched column ratios across `.section-heading`,
  `.role-card`, and `.education-grid`. Changing one column ratio usually means
  changing its siblings in the same breakpoint.

## Accessibility

Already in place: `.skip-link`, `aria-label` on every nav/list region,
`aria-hidden="true"` on decorative glyphs (`↗`, `↓`, `•`, the status dot, the `KD`
mark), explicit `width`/`height` on the portrait image, and `:focus-visible`
outlines. Preserve these when you add markup.

## Legacy files

`www/code.html` is a meta-refresh to a long-dead code.google.com URL. `www/images/`
holds artifacts from earlier versions of the site (`RL_*.png`,
`value iteration.png`, `valid-css.png`, `valid-xhtml11.png`) that `index.html` no
longer references. Leave them unless asked. Some may still be hot-linked
externally.

## Importing other agent configs

An OpenAI Codex config exists at `~/.codex/config.toml`. To bring it into Claude
Code, reply `/import` to see what's importable, then `/import --yes=<digest>`
using the digest from the scan output.
