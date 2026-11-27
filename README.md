The source for Kellen Donohue’s [personal homepage](https://kellend.com/).

The static site lives in `www/`. GitHub Actions validates and publishes it to GitHub Pages on pushes to `master`.

Preview it with `python3 -m http.server -d www 8000`. Run the site checks with
`python3 -m unittest discover -s tests`.
