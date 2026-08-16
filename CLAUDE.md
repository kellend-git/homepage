# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Kellen Donohue's personal homepage: a hand-written static site. No build step, no
package manager, no dependencies, no tests. Everything served lives in `www/`;
files at the repo root are deployment config only.

`www/index.html` and `www/css/homepage.css` are the entire site. There is no
JavaScript on the page (the README's mention of Google Analytics JS is stale —
the redesign dropped it).

## Local preview

```sh
python3 -m http.server -d www 8000   # then open http://localhost:8000
```

Verify at both breakpoints (see CSS section) and check the sticky header, the
`#work`/`#education`/`#research` anchor scrolling, and the `.skip-link` on
keyboard focus.

## Two deploy targets, one `www/`

The same directory is published two different ways, so a change to routing or
asset paths must work under both:

1. **Google App Engine** — `app.yaml` + `./deploy.sh` (`gcloud app deploy`),
   serving www.kellendonohue.com. Routing: `/` → `www/index.html`,
   `/Resume.pdf` → `www/KellenDonohueResume.pdf` (an alias that exists *only*
   here), `/(.*)` → `www/\1`. The `php84` runtime is vestigial — no PHP is
   executed.
2. **GitHub Pages** — `.github/workflows/pages.yml` uploads `./www` verbatim on
   push to `homepage-redesign-preview` (or `workflow_dispatch`). No `app.yaml`
   routing, no `/Resume.pdf` alias, no `CNAME`.

Consequence: link assets with plain relative paths (`KellenDonohueResume.pdf`,
`css/homepage.css`), never `/Resume.pdf` or other App-Engine-only routes.

The canonical URL and all `og:`/`twitter:` metadata in `www/index.html` point at
`https://kellend.com`. Keep the title/description/OG triplet consistent when
editing any of them, and regenerate `www/og.png` if the tagline changes.

## Branch layout

`master` is the App Engine version. `homepage-redesign-preview` carries the
redesign and is the branch the Pages workflow watches — pushing to it publishes
immediately. The redesign diff is confined to `.github/workflows/pages.yml`,
`www/index.html`, `www/css/homepage.css`, `www/site.webmanifest`, and
`www/og.png`.

## CSS conventions

`www/css/homepage.css` is hand-maintained in a compressed style: each logical
section (header, hero, portrait, metrics, timeline, education, research,
contact/footer, then media queries) is a single long line with no spaces after
`:` or `;`. Match that format rather than reformatting — a prettified rewrite
makes every future diff unreadable.

- All color, `--shell` width, and `--radius` values come from the `:root` custom
  properties. Add a variable instead of hardcoding a new hex.
- Two breakpoints only: `max-width:900px` (drops the nav links, tightens the
  hero grid) and `max-width:700px` (single column throughout). A third
  `prefers-reduced-motion` block disables smooth scroll and transitions.
- The layout is CSS grid with matched column ratios across `.section-heading`,
  `.role-card`, and `.education-grid`; changing one column ratio usually means
  changing its siblings in the same breakpoint.

## Accessibility expectations already in place

`.skip-link`, `aria-label` on every nav/list region, `aria-hidden="true"` on
decorative glyphs (`↗`, `↓`, `•`, the status dot, `KD` mark), explicit
`width`/`height` on the portrait image, and `:focus-visible` outlines. Preserve
these when adding markup.

## Legacy files

`www/code.html` is a meta-refresh to a long-dead code.google.com URL.
`www/images/` holds artifacts from earlier versions of the site
(`RL_*.png`, `value iteration.png`, `valid-css.png`, `valid-xhtml11.png`) that
`index.html` no longer references. Leave them unless asked — some may still be
hot-linked externally.

## Importing other agent configs

An OpenAI Codex config exists at `~/.codex/config.toml`. To bring it into Claude
Code, reply `/import` to see what's importable, then
`/import --yes=<digest>` using the digest from the scan output.
