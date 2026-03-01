# Academic website (Quarto)

Personal academic website built with [Quarto](https://quarto.org).

## Build locally

1. Install [Quarto](https://quarto.org/docs/get-started/) (e.g. `winget install Posit.Quarto` on Windows).
2. Add optional assets: put your profile photo at `assets/photo.jpg` (home page); optionally add `assets/favicon.ico` for the browser tab icon.
3. If `quarto render` fails with "file is being used by another process", close any app that may be using the project folder (e.g. File Explorer, Dropbox, IDE) or temporarily rename `site_libs` and `docs` if they exist, then run:
   ```bash
   quarto render
   ```
4. Output is in `docs/`. Open `docs/index.html` in a browser to preview.

## Publish (GitHub Pages)

- In the repo go to **Settings > Pages**. Set **Source** to "Deploy from a branch", branch **main**, folder **/docs**.
- The CI workflow (`.github/workflows/render-site.yml`) runs `quarto render` on every push to `main` and commits the updated `docs/` back to the repo, so the site stays up to date. No need to commit `docs/` manually after enabling this.
- After enabling Pages, set your live URL in `_quarto.yml` under `website: site-url:` (e.g. `https://YOUR-USERNAME.github.io/website_git`) so Open Graph and Twitter Card previews use the correct links.

## CI

The workflow runs on push to `main`: renders the site with Quarto, then commits and pushes the `docs/` folder so GitHub Pages serves the latest build.

## Structure

- `_quarto.yml` — site config, navbar, theme, output directory, footer, SEO
- `*.qmd` — source pages (index, about, pub, wp, data, media)
- `assets/css/custom.css` — shared styles; `assets/photo.jpg` (optional), `assets/cv.pdf`, `assets/favicon.ico` (optional)
- `content/publications.yml` — single source for publication and working paper metadata; rendered by pub.qmd and wp.qmd via R

The Publications and Working Papers pages use R. To build locally:

- **Option A:** Install into R's default library (may require running R as Administrator):  
  `install.packages(c("yaml", "knitr", "rmarkdown"), repos = "https://cloud.r-project.org")`
- **Option B:** Use a project library (no admin needed). From the project root, run once:  
  `Rscript -e "install.packages(c('yaml','knitr','rmarkdown'), lib='r_lib', repos='https://cloud.r-project.org')"`  
  Then before each `quarto render`, set the R library path, e.g. in PowerShell:  
  `$env:R_LIBS_USER = "e:\Dropbox\Github\website_git\r_lib"`
