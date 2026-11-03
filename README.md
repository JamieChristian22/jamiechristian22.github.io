# Jamie Christian II — Portfolio Website

A responsive, accessible, static landing page for the independent business, product, data, cloud, IT, and security portfolio.

**Site URL (when GitHub Pages publishing is enabled):** https://jamiechristian22.github.io/

## What is included

- HTML/CSS/JS site in [index.html](index.html)
- Eight self-hosted project images in [assets/](assets/) with [source inventory](ASSET_SOURCES.md)
- Responsive navigation and mobile layout
- Filterable featured GitHub projects
- Links to professional profile and GitHub Sponsors
- Accessibility features: skip link, labels, focus states, reduced-motion behavior, live filter status
- Explicit disclosure of synthetic and simulated portfolio work
- Offline HTML and asset integrity checker: [tools/check_site.py](tools/check_site.py)
- GitHub Actions validation: [.github/workflows/site-check.yml](.github/workflows/site-check.yml)

## Preview and local checks

Run the structural check with Python 3.11+:

```bash
python tools/check_site.py
```

To preview locally, open `index.html` in a browser, or serve the repository folder with:

```bash
python -m http.server 8000
```

Then open http://localhost:8000/ and test both desktop and mobile layout.

## Publishing

This repo's default branch contains a root `index.html`. If the site is not public, a repository administrator should confirm **Settings → Pages → Build and deployment** is configured to serve from the `main` branch root or an appropriate GitHub Actions deployment. Check the Pages deployment result and the public URL in a browser. **A successful Git commit or static check does not confirm that Pages hosting is enabled or that live deployment succeeded.**

## Evidence policy

Links point to project repositories, which may contain synthetic datasets, simulations, and project exercises. A live business outcome or production system is never implied solely by a portfolio card.

## License and third-party materials

See [LICENSE](LICENSE) for the repository license. Third-party code, datasets, images, and other assets retain their respective terms.
