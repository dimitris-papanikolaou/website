# Full plan: BibTeX citations and title links

## Overview

Two changes to the academic website:

1. **BibTeX citations** – For each paper (publications and working papers), add a downloadable BibTeX entry. The link is labeled **Bibtex Citation** and points to a generated `.bib` file so visitors can cite the paper easily.
2. **Title links removed** – Paper titles are shown as plain text only; they are no longer clickable links (even when `title_url` is set in the YAML). Other links (Paper, Slides, Data, etc.) are unchanged.

---

## 1. BibTeX citations

### Behavior

- On **Publications** (`pub.html`) and **Working Papers** (`wp.html`), each entry shows an extra link: **Bibtex Citation**.
- Clicking it opens/downloads a single-entry `.bib` file (e.g. `meeuwis2025time_varying_risk.bib` for a publication, or `meeuwis2026time_wp.bib` for a working paper).
- Content is generated from [website/content/publications.yml](website/content/publications.yml) (title, authors, venue, year when available, url, notes).

### Where .bib files live

- **Location:** `docs/assets/bib/<slug>.bib` (e.g. `website/docs/assets/bib/schmidt2023_measuring_document.bib`).
- **When created:** When you run `quarto render`. The R code in [website/pub.qmd](website/pub.qmd) and [website/wp.qmd](website/wp.qmd) writes one `.bib` file per paper into `docs/assets/bib/`. They are **not** generated when a user clicks the link; they are static files created at build time.
- **Deployment:** Whatever deploys `docs/` (e.g. GitHub Pages) will serve `docs/assets/bib/*.bib` like any other asset.

### How it’s implemented

| Piece | Role |
|-------|------|
| [website/scripts/bibtex_helpers.R](website/scripts/bibtex_helpers.R) | Shared R helpers: `bib_escape`, `year_from_venue`, `paper_to_slug`, `paper_to_bibtex`. Used by both pub and wp. |
| [website/pub.qmd](website/pub.qmd) | Loads helpers, ensures `docs/assets/bib` exists, and in `render_pub_entry()`: (1) compute slug, (2) write `paper_to_bibtex(..., is_working_paper = FALSE)` to `docs/assets/bib/<slug>.bib`, (3) output existing links plus `[[Bibtex Citation](assets/bib/<slug>.bib)]`. |
| [website/wp.qmd](website/wp.qmd) | Same idea: in `render_entry()` use `paper_to_slug(..., is_working_paper = TRUE)` and `paper_to_bibtex(..., is_working_paper = TRUE)`, write `.bib`, then add the **Bibtex Citation** link. |
| [website/content/publications.yml](website/content/publications.yml) | No required change. Optional: add `year` and/or `bib_key` per entry for better citation keys and accuracy. |

### BibTeX details

- **Publications:** `@article` with `author`, `title`, `journal` (from venue), `year` (from venue or optional `year`), `note` (from notes), `url` (from `title_url` or first link).
- **Working papers:** `@unpublished` with `author`, `title`, `year`, `note` (e.g. “Working paper. &lt;venue&gt;”), `url`.
- **Slug (citation key / filename):** If YAML has `bib_key`, use it (sanitized). Otherwise: first author’s last name + year (or `nodate`) + first 3 words of title, sanitized; working papers get a `_wp` suffix. Uniqueness within each page is enforced by appending `_2`, `_3`, … if needed.

---

## 2. Title links removed

### Behavior

- Paper titles are always rendered as plain text inside `<span class="pub-title">...</span>`.
- They are **never** wrapped in `<a href="...">`, even when the YAML entry has `title_url`.
- `title_url` is still used when generating the BibTeX `url` field, so the downloadable citation keeps the link.

### Where it’s implemented

- [website/pub.qmd](website/pub.qmd): `render_pub_entry()` now uses  
  `title_html <- sprintf('<span class="pub-title">%s</span>', html_escape(p$title))`  
  (no branch on `p$title_url`).
- [website/wp.qmd](website/wp.qmd): Same in `render_entry()`.

---

## 3. Files touched (summary)

| File | Changes |
|------|--------|
| [website/scripts/bibtex_helpers.R](website/scripts/bibtex_helpers.R) | **New.** Shared BibTeX helpers. |
| [website/pub.qmd](website/pub.qmd) | Source helpers; create `docs/assets/bib`; in `render_pub_entry`: write `.bib`, add “Bibtex Citation” link; title as plain text only. |
| [website/wp.qmd](website/wp.qmd) | Source helpers; create `docs/assets/bib`; in `render_entry`: write `.bib`, add “Bibtex Citation” link; title as plain text only. |
| [website/content/publications.yml](website/content/publications.yml) | Optional: add `year` and/or `bib_key` for any entry. |

---

## 4. What you need to do

- **Build:** Run `quarto render` from the `website` directory so that `docs/assets/bib/` is populated and the site (including Bibtex Citation links) is up to date.
- **Optional:** In `content/publications.yml`, add `year` and/or `bib_key` where you want a specific citation key or a more accurate year.

I have everything needed to implement and describe this; the code is already in place as above.
