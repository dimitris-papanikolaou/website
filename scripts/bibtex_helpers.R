# Shared BibTeX helpers for pub.qmd and wp.qmd

bib_escape <- function(x) {
  if (is.null(x) || !nzchar(trimws(x))) return("")
  x <- trimws(x)
  x <- gsub("\\", "\\\\", x, fixed = TRUE)
  x <- gsub("{", "\\{", x, fixed = TRUE)
  x <- gsub("}", "\\}", x, fixed = TRUE)
  x
}

year_from_venue <- function(venue) {
  if (is.null(venue) || !nzchar(trimws(venue))) return(NA_character_)
  m <- regmatches(venue, regexpr("\\b(19|20)[0-9]{2}\\b", venue, perl = TRUE))
  if (length(m) > 0) m[1] else NA_character_
}

paper_to_slug <- function(p, used_slugs, is_working_paper = FALSE) {
  if (nzchar(p$bib_key %||% "")) {
    base <- tolower(gsub("[^a-zA-Z0-9]+", "_", trimws(p$bib_key)))
    base <- gsub("^_|_$", "", base)
  } else {
    auths <- p$authors %||% list()
    lastname <- if (length(auths) > 0) {
      parts <- strsplit(trimws(auths[[1]]$name), "\\s+")[[1]]
      tolower(parts[length(parts)])
    } else "author"
    year <- p$year %||% year_from_venue(p$venue %||% "")
    year <- if (is.na(year) || !nzchar(year)) "nodate" else year
    title_words <- strsplit(gsub("[^a-zA-Z0-9\\s]", " ", p$title %||% ""), "\\s+")[[1]]
    title_part <- paste(head(title_words[title_words != ""], 3), collapse = "_")
    title_part <- tolower(gsub("_+", "_", gsub("[^a-zA-Z0-9]+", "_", title_part)))
    if (!nzchar(title_part)) title_part <- "paper"
    base <- paste0(lastname, year, "_", title_part)
  }
  if (is_working_paper) base <- paste0(base, "_wp")
  slug <- base
  k <- 1
  while (slug %in% used_slugs) {
    k <- k + 1
    slug <- paste0(base, "_", k)
  }
  slug
}

paper_to_bibtex <- function(p, slug, is_working_paper = FALSE) {
  auths <- p$authors %||% list()
  author_str <- if (length(auths) > 0) {
    paste(vapply(auths, function(a) bib_escape(a$name %||% ""), character(1)), collapse = " and ")
  } else ""
  title_str <- bib_escape(p$title %||% "")
  venue_str <- bib_escape(p$venue %||% "")
  year <- p$year %||% year_from_venue(p$venue %||% "")
  year_str <- if (!is.na(year) && nzchar(year)) year else ""
  url_str <- bib_escape(p$title_url %||% "")
  if (!nzchar(url_str) && length(p$links %||% list()) > 0) url_str <- bib_escape(p$links[[1]]$url %||% "")
  note_str <- bib_escape(p$notes %||% "")
  if (is_working_paper && nzchar(venue_str)) note_str <- trimws(paste("Working paper.", if (nzchar(note_str)) paste(venue_str, note_str, sep = ". ") else venue_str))
  if (!is_working_paper && nzchar(note_str)) note_str <- note_str else if (is_working_paper && !nzchar(note_str)) note_str <- "Working paper."

  if (is_working_paper) {
    lines <- c(
      sprintf("@unpublished{%s,", slug),
      sprintf("  author = {%s},", author_str),
      sprintf("  title = {%s},", title_str),
      if (nzchar(year_str)) sprintf("  year = {%s},", year_str),
      sprintf("  note = {%s},", note_str),
      if (nzchar(url_str)) sprintf("  url = {%s}", url_str)
    )
  } else {
    lines <- c(
      sprintf("@article{%s,", slug),
      sprintf("  author = {%s},", author_str),
      sprintf("  title = {%s},", title_str),
      if (nzchar(venue_str)) sprintf("  journal = {%s},", venue_str),
      if (nzchar(year_str)) sprintf("  year = {%s},", year_str),
      if (nzchar(note_str)) sprintf("  note = {%s},", note_str),
      if (nzchar(url_str)) sprintf("  url = {%s}", url_str)
    )
  }
  lines <- lines[nzchar(lines)]
  if (length(lines) > 1) lines[length(lines)] <- sub(",$", "", lines[length(lines)])
  paste(lines, collapse = "\n")
}
