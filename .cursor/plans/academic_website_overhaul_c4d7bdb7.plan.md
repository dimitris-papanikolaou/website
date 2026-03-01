---
name: Academic Website Overhaul
overview: A phased plan to migrate your academic site to Quarto and then improve content, design, automation, SEO, and journalist-facing features. Quarto is the primary stack; all subsequent phases build on it.
todos: []
isProject: false
---

# Academic Website Overhaul Plan

Your site is currently an **R Markdown website** (Bootstrap 3 + Cosmo) built with `rmarkdown::render_site()`. The plan **migrates it to Quarto** first, then applies the rest of the improvements. Content will move from `.Rmd` to `.qmd`; config from [_site.yml](_site.yml) to `_quarto.yml`; build from `rmarkdown::render_site()` to `quarto render`.

---

## 1. Fix critical issues (during or right after Quarto migration)

- **CSS bug**: In the current [pub.Rmd](pub.Rmd), [wp.Rmd](wp.Rmd), and [data.Rmd](data.Rmd), `body { font-size: 190%; }` makes body text huge—almost certainly a typo. When converting to Quarto, use normal body font size (remove or set to `100%`). In Quarto, custom CSS goes in `assets/css/custom.css` or in `_quarto.yml` under `website/css`.
- **Single source for Working Papers**: You have both [wp.Rmd](wp.Rmd) and [newwp.Rmd](newwp.Rmd) with different orderings/versions. Pick one as canonical, merge content into a single Working Papers page, and remove the other. In `_quarto.yml` there will be only one “Working Papers” nav item.
- **Shared styles**: In Quarto, put `.pub-title`, `details.abstract`, and other publication styles in a single file (e.g. `assets/css/custom.css`) and include it via `_quarto.yml` → `website/css`, so pub/wp/data pages don’t duplicate CSS.

---

## 2. Content and information architecture

- **About page**: [about.Rmd](about.Rmd) is a placeholder and not in the nav. Add a real “About” with the bio below, add it to the site navbar in `_quarto.yml`, and optionally include a local copy of your profile photo.
  - **Bio content to use** (from Kellogg/NBER/web; can be shortened for the site):
    - *Short version:* Dimitris Papanikolaou is the John L. and Helen Kellogg Professor of Finance at the Kellogg School of Management, Northwestern University, and a Research Associate of the NBER. His research examines the interaction between technological innovation and financial markets, including intangible capital, economic growth, innovation, macroeconomics, and asset pricing. He has published in the *Quarterly Journal of Economics*, *Journal of Political Economy*, *Journal of Finance*, *Review of Financial Studies*, and *Journal of Financial Economics*, and has won the Amundi Smith Breeden Prize twice (Journal of Finance). He is Co-Editor of the *Journal of Financial Economics* and teaches asset pricing. He holds a Ph.D. in Financial Economics from MIT (2007), an M.Sc. from LSE (2001), and a B.A. from the University of Piraeus (2000).
    - *Optional “Impact” line:* From his [Google Scholar](https://scholar.google.com/citations?user=WUoGJWoAAAAJ&hl=en) profile (update periodically): e.g. “Over 9,000 citations, h-index 25, i10-index 32” (or “Since 2020: over 6,350 citations, h-index 23”). Link the text “Google Scholar” to his profile. *Note:* Direct fetch of the Scholar page timed out; these figures came from web search and should be verified/updated by you.
- **Home page**: [index.Rmd](index.Rmd) is minimal (photo, title, affiliation, address). Consider:
  - A short “Research” or “Focus” paragraph.
  - A “Selected work” or “Featured publications” section (3–5 items with links to pub/wp).
  - Optional: “News” or “Recent” (e.g. new paper, award, talk) for freshness.
- **Data-driven publications**: Replace hand-written HTML in pub/wp (and optionally data) with **structured data + template** (committed).
  - **Papers in the repo**: Store all paper PDFs, slides, and (where desired) code/data zips under `**assets/papers/`** (e.g. `assets/papers/risk-premia-labor.pdf`). Use a consistent slug-based naming scheme. Migrate existing Dropbox/journal links by downloading files into `assets/papers/` and pointing the data file at these local paths.
  - **Single source of truth**: `**content/publications.yml`** with fields: title, authors, venue, year, status, type (publication | working_paper), links (paper, slides, code, data — paths under `assets/papers/` or external URLs), abstract, optional plain_language_summary, optional topics.
  - **Rendering**: `pub.qmd` and `wp.qmd` read this data, filter by type, and render the list with expandable abstracts and links.
- **CV**: Host the CV PDF in the repo at `**assets/cv.pdf`** and link from the navbar. Keep “Download CV” in nav.
- **Google Scholar**: Your navbar already links to [your Scholar profile](https://scholar.google.com/citations?user=WUoGJWoAAAAJ&hl=en). Checked via web search (direct page fetch timed out). Current metrics from search: ~9,000 total citations, h-index 25, i10-index 32; since 2020: 6,350+ citations, h-index 23. Optionally add a short “Impact” line on the About page with these (and link to Scholar), updating periodically.

---

## 3. Design overhaul (Quarto)

- **Theme and typography**: In `_quarto.yml`, set a **Quarto theme** (e.g. `theme: cosmo`, `flatly`, or `minimal`) and optionally add `css: assets/css/custom.css` for overrides. Quarto ships consistent, modern typography and a single set of assets (no version drift).
- **Home page layout**: Move from “image + block of text” to a clearer hierarchy: e.g. hero section (name, title, affiliation), then 2–3 columns or sections (Research focus, Selected work, Contact). Use Quarto’s layout options (columns, callouts) or custom HTML/CSS.
- **Consistent assets**: Profile photo in `assets/photo.jpg`; papers and slides in `**assets/papers/`** (see data-driven publications above). No reliance on Dropbox for core site assets.

---

## 4. Technical foundation (Quarto)

- **Output directory**: In `_quarto.yml`, set `output-dir: docs` (or `_site`) so HTML and assets go into a single folder. Configure GitHub Pages to “Deploy from branch” → `main` → `/docs` (or `/ (root)` if using `_site` and a deploy step). Keeps repo root source-only (`.qmd`, `_quarto.yml`, `assets/`).
- **Automated build**: Add a **GitHub Actions** workflow that runs `quarto render` on push to `main`, so the site always reflects the latest content. If output is `docs/`, commit the rendered files or use a branch; if using `_site`, the workflow can publish to `gh-pages` or push to `main`/`docs` as needed.
- **Dependencies**: Document that the site uses **Quarto** (install from [quarto.org](https://quarto.org)); if any page uses R, list `quarto` and R packages (e.g. in README or `requirements.txt` for CI). Quarto handles Pandoc, Bootstrap, and JS/CSS; no need for `rmarkdown::render_site()` or `_site.yml`.

---

## 5. SEO, accessibility, performance (Quarto)

- **SEO**: Quarto supports per-page **meta description** and **Open Graph** via YAML front matter (`description:`, `image:`) and project-level defaults in `_quarto.yml`. Add title, description, and image so search and social previews look correct.
- **Accessibility**: Quarto sets `<html lang="en">` by default; add a **skip link** in a custom layout or `includes/` if needed. Ensure navbar links (Contact, Google Scholar) have **aria-label** or visible text so screen readers and keyboard users get context.
- **Performance**: Quarto serves a single, consistent set of CSS/JS. Optional: use `format: html: minimal: true` where you don’t need TOC/sidebar, and lazy-load or conditionally load MathJax only on pages that use math.

---

## 6. Quarto migration (Phase A)

- **Why**: Quarto is the modern successor to R Markdown for docs and websites: same R/Markdown workflow, but better default themes, built-in SEO options, and a cleaner project structure. Your existing `.Rmd` content can move over with limited changes.
- **How**: Create a `_quarto.yml` with project type `website`, same navbar structure, and move pages to `.qmd` (or keep `.Rmd`). Use Quarto’s `page` metadata for layout and custom CSS. Render with `quarto render` and hook that into GitHub Actions.
- **Scope**: This is a moderate refactor (config, asset paths, maybe one shared layout). It pairs well with the “data-driven publications” idea: Quarto can render from R and YAML easily.

---

## 7. Suggested phasing


| Phase | Focus                | Outcome                                                                                                                 |
| ----- | -------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **A** | **Quarto migration** | `_quarto.yml`, all pages as `.qmd`, output to `docs/`, single WP page, shared CSS, no 190% bug, CI with `quarto render` |
| **B** | Content & IA         | Real About, improved home (focus + featured work), CV in repo                                                           |
| **C** | Tech & deploy        | GitHub Pages from `docs/`, document Quarto (+ R if used)                                                                |
| **D** | Design refresh       | Quarto theme, home layout, local profile image                                                                          |
| **E** | Data-driven pubs     | `content/publications.yml`, papers/slides in `assets/papers/`, pub.qmd + wp.qmd render from data                        |
| **F** | Polish               | SEO meta, OG tags, accessibility, favicon, footer, print CSS                                                            |
| **G** | Media & press        | Media page, media kit, plain-language takeaways, topic tags                                                             |


Phase **A** (Quarto migration) is the foundation; do it first. Phases B–C give you correct content and automated deploy. D–E improve look and scalability. F–G add polish and journalist-facing features.“” 

## 8. Journalists and press

Make the site the obvious place for **journalists** (story ideas, quotes, fact-checking) to find you and understand your research quickly.

### For journalists

- **Dedicated "Media" or "For press" page**: One place that says you're available for comment and how to reach you (email or link to Kellogg media team if you prefer). Add it to the navbar (e.g. "Media" or "Press").
- **Plain-language research summaries**: Beyond academic abstracts, add 1–3 sentence **non-technical takeaways** for key papers—e.g. "What we find," "Why it matters," "One headline." Optionally a "Key findings" or "In plain English" line under each abstract (in [pub.Rmd](pub.Rmd) / [wp.Rmd](wp.Rmd) or in the data-driven template). This helps reporters quickly see story angles.
- **Media kit**: A single **download** or linked section with: (1) high-resolution **headshot** (e.g. `assets/photo-highres.jpg`), (2) **short bio** (2–3 sentences, copy-paste ready), (3) **one-page research highlights** (optional). Link from the Media page as "Download media kit" or "Press resources."
- **"In the news" or "Media coverage"**: A short list of prior coverage (Kellogg Insight, Brookings, podcasts, major outlets) with links and dates. Include the **Brookings podcast** on technology and labor / AI and jobs: [What jobs will be most affected by AI?](https://www.brookings.edu/articles/what-jobs-will-be-most-affected-by-ai/). Can live on the Media page or a separate subsection.
- **Topic or theme navigation**: Group or tag research by **theme** (e.g. "AI & labor," "Intangibles & valuation," "Innovation & patents," "COVID & remote work") so a journalist searching for "AI jobs" can land on the right papers and summaries quickly. Can be filters on Publications/Working Papers or a simple "Research by topic" page.
- **Contact prominence**: Ensure "Contact" in the navbar uses a clear label and that the About and Media pages repeat the same email so reporters have one obvious path.

### Cross-cutting

- **SEO for your name and topics**: Meta descriptions and page titles that include your name, "Kellogg," and key phrases ("innovation and labor," "AI labor market," "intangible capital") so search and news alerts surface your site when reporters look for experts.
- **Mobile and speed**: Many first touches happen on a phone; fast load and readable layout (already in the plan) matter for busy reporters.
- **No dead ends**: Every audience (press, academics) should reach a clear next step (email, media kit, or Kellogg link) within one or two clicks from the home page.

### Suggested implementation

- Add **Media** (or **Press**) to the navbar in `_quarto.yml`; create `media.qmd` with: contact for press, link to media kit, optional "In the news," and link to plain-language research (or "Key papers" with takeaways).
- Extend publication entries (or the future YAML + template) with optional fields: `plain_language_summary`, `topics` (tags), and later `media_mentions`. Render "Key findings" and topic tags on the site; use topics for filtering or a "Research by topic" view.
- Add `assets/photo-highres.jpg` and a "Media kit" zip or a single "Press resources" page that links to high-res photo + short bio (and optionally one-pager).

---

## 9. Additional professionalism

Extra polish that reinforces credibility and consistency without changing the core plan.

### Branding and identity

- **Favicon**: Add a favicon (e.g. `favicon.ico` or `assets/favicon.ico`) so the tab shows a Kellogg/Northwestern mark or your initial instead of a generic icon. Reference it in the site header or `_quarto.yml` includes.
- **Footer**: A simple footer on every page: copyright (e.g. “© 2025 Dimitris Papanikolaou”), optional “Kellogg School of Management, Northwestern University,” and optionally “Site source: [GitHub](repo link).” Keeps the site from feeling abruptly cut off and signals affiliation.
- **Affiliation in footer**: Repeating “John L. and Helen Kellogg Professor of Finance, Kellogg School of Management, Northwestern University” (or a short line) in the footer reinforces credibility on long pages. Optional: small Kellogg or Northwestern logo (with permission) for visual consistency.

### Consistency and correctness

- **Citation and terminology**: Use one style for publications (e.g. “Forthcoming,” “Revise and Resubmit,” “2025”) and consistent labels (“Paper,” “Slides,” “Code,” “Data”) across [pub.Rmd](pub.Rmd) and [wp.Rmd](wp.Rmd). Reduces the chance of looking sloppy when someone scans the list.
- **No placeholders or broken content**: Remove or complete any “Say more about you here”–style text (already flagged in [about.Rmd](about.Rmd)); ensure no “TBD” or dead links in Data Library or publication links. A quick manual pass or an optional **link checker** in CI (e.g. `linkchecker` or `lychee`) can catch broken URLs after build.
- **Dates on data/code**: Where you link to data or code, optionally add “(Updated March 2025)” or similar so visitors know the snapshot is current. Especially helpful for replications and professional use.

### Technical polish

- **Valid HTML**: After fixing the theme and shared CSS, run the built site through the [W3C Validator](https://validator.w3.org/) (or a CI step) and fix critical errors. Reduces layout quirks and improves accessibility.
- **Print-friendly**: A small **print stylesheet** (hide navbar, expand abstracts if desired, clean margins) so “Print” or “Save as PDF” produces a readable document for papers or your CV page. Quarto allows a custom `css` for `print` media in `_quarto.yml` or page YAML.
- **HTTPS**: GitHub Pages serves over HTTPS by default; ensure the repo Settings → Pages uses HTTPS and that any custom domain (if added later) is configured correctly.

### Optional

- **Analytics**: If you want to see traffic (e.g. from media or hiring), add a lightweight analytics snippet (e.g. Plausible, Fathom, or Google Analytics). Include a one-line **privacy notice** in the footer (“This site uses [analytics] for aggregate traffic. No personal data is sold.”) for transparency.
- **“As featured in”**: If you have notable media coverage, a short “As featured in” row (logos or names: Kellogg Insight, Brookings, etc.) on the home or Media page adds social proof. Can be added when the “In the news” list is in place.

These can be folded into **Phase F (Polish)** or done as a final pass after the main overhaul; favicon and footer are quick wins.

---

## Key files to touch

- `**_quarto.yml`**: Primary config: `project: type: website`, navbar, `output-dir: docs`, theme, `website/css`, optional `includes` for header/footer.
- **Source pages** (as `.qmd`): `index.qmd`, `about.qmd`, `pub.qmd`, `wp.qmd`, `data.qmd`, `media.qmd`. Pub and wp render from `content/publications.yml` (data-driven).
- **Data and assets**: `**content/publications.yml`** (single source for all publications and working papers). `**assets/papers/`** (all paper PDFs, slides, and optional code/data zips; links in YAML point here). `**assets/css/custom.css`**, `**assets/photo.jpg`**, `**assets/cv.pdf**`, `**assets/photo-highres.jpg**` (media kit). `**_quarto.yml**`, `**.github/workflows/render-site.yml**` (runs `quarto render`).
- For journalists: `media.qmd`, `assets/photo-highres.jpg`, and optional fields in publications data (`plain_language_summary`, `topics`).
- Professionalism (Section 9): `favicon.ico` or `assets/favicon.ico`, shared footer (e.g. in `_quarto.yml` includes), optional print CSS.

Execution starts with **Phase A (Quarto migration)**; once that is in place, we can work through B–G in order or by priority. If you want to adjust scope (e.g. “fix only,” “design + automation,” or “full overhaul including Quarto”), I can turn this into a step-by-step implementation checklist next.