# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Kellen Donohue's personal homepage: a hand-written static site. No build step, no
package manager, no third-party dependencies. Everything served lives in `www/`;
files at the repo root are deployment config or tests.

`www/index.html` and `www/css/homepage.css` are the entire site. There's no
JavaScript on the page. (The README still mentions Google Analytics JS. The
redesign dropped it.)

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
  reference is absolute (the App Engine / Pages split below).
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

## Two deploy targets, one `www/`

The same directory gets published two ways, so a change to routing or asset paths
has to work under both.

1. **Google App Engine.** `app.yaml` plus `./deploy.sh` (`gcloud app deploy`).
   This is what currently serves both live domains. Routing: `/` →
   `www/index.html`, `/Resume.pdf` → `www/KellenDonohueResume.pdf` (an alias that
   exists *only* here), `/(.*)` → `www/\1`. The `php84` runtime is vestigial; no
   PHP runs.
2. **GitHub Pages.** `.github/workflows/pages.yml` uploads `./www` verbatim on
   push to `homepage-redesign-preview` (or `workflow_dispatch`). No `app.yaml`
   routing, no `/Resume.pdf` alias, no `CNAME`, so Pages serves from
   `kellend-git.github.io/homepage`. Read the domain notes below before adding
   one.

So link assets with plain relative paths (`KellenDonohueResume.pdf`,
`css/homepage.css`). Never `/Resume.pdf` or another App-Engine-only route.

The canonical URL and all `og:`/`twitter:` metadata in `www/index.html` point at
`https://kellend.com`. Keep the title/description/OG triplet consistent when you
edit any of them, and regenerate `www/og.png` if the tagline changes.

### Domain state

Both `kellend.com` and `kellendonohue.com` are Squarespace-registered domains that
serve this site off App Engine. Verified Aug 2026:

- Both apexes have A records to `216.239.32-38.21` (App Engine) and return 200
  directly. `www.kellend.com` is a CNAME to `ghs.googlehosted.com`.
- `www.kellendonohue.com` is a CNAME to `ext-sq.squarespace.com`, which 301s to
  `http://kellendonohue.com/`. That's Squarespace forwarding, on that one
  hostname only.
- Authoritative nameservers for both are `ns-cloud-*.googledomains.com`, so
  records get edited in **Google Cloud DNS**. Squarespace's DNS panel won't have
  them. Squarespace is the registrar (it acquired Google Domains in 2023); DNS
  hosting stayed with Google.

There's **no `www/CNAME`**, on purpose. Adding one declares a Pages custom domain,
but Pages can't serve it until those apex A records point at GitHub
(`185.199.108-111.153`). Worse, setting a custom domain makes GitHub redirect
`kellend-git.github.io/homepage` to it, which breaks the preview URL before the
cutover. So: repoint DNS first, add `CNAME` second. `tests/test_site.py`
validates the file once it exists.

## Branch layout

`master` is the App Engine version. `homepage-redesign-preview` carries the
redesign and is the branch the Pages workflow watches, so pushing to it publishes
immediately. The redesign diff is confined to `.github/workflows/pages.yml`,
`www/index.html`, `www/css/homepage.css`, `www/site.webmanifest`, and
`www/og.png`.

The tests can't run against `master`: it has no `og.png` and only 2 of the
metadata tags they assert on. They're coupled to the redesign and belong on this
branch until it merges.

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
