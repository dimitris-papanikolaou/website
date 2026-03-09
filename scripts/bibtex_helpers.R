# Shared BibTeX helpers for pub.qmd and wp.qmd
# Site author included in every BibTeX entry (YAML lists coauthors only)
SITE_AUTHOR <- "Dimitris Papanikolaou"

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

# Parse venue string into journal, volume, number (issue) for separate BibTeX fields
parse_venue <- function(venue) {
  if (is.null(venue) || !nzchar(trimws(venue))) {
    return(list(journal = "", volume = "", number = "", year = NA_character_))
  }
  v <- trimws(venue)
  year <- year_from_venue(v)
  journal <- v
  volume <- ""
  number <- ""

  # Trailing volume(issue) or volume: e.g. ", 11(2)" or ", 87"
  vol_iss_match <- regmatches(v, regexec(",\\s*(\\d+)(?:\\(([^)]+)\\))?\\s*$", v, perl = TRUE))[[1]]
  if (length(vol_iss_match) >= 2) {
    volume <- vol_iss_match[2]
    if (length(vol_iss_match) >= 3 && nzchar(vol_iss_match[3])) number <- vol_iss_match[3]
    journal <- trimws(sub(",\\s*\\d+(?:\\([^)]+\\))?\\s*$", "", v, perl = TRUE))
  }

  # Remove year from journal (at end or ", YEAR, " in middle)
  journal <- trimws(sub(",\\s*(19|20)\\d{2}\\s*$", "", journal, perl = TRUE))
  journal <- trimws(gsub(",\\s*(19|20)\\d{2}\\s*,?\\s*", ", ", journal, perl = TRUE))
  journal <- trimws(gsub(",\\s*,", ",", journal, perl = TRUE))

  # ", VOL, PAGES" at end (e.g. ", 11, 221–242") -> extract volume if not already set
  if (!nzchar(volume)) {
    vol_pages_match <- regmatches(journal, regexec(",\\s*(\\d+)\\s*,\\s*[\\d\\s\u2013-]+\\s*$", journal, perl = TRUE))[[1]]
    if (length(vol_pages_match) >= 2) {
      volume <- vol_pages_match[2]
      journal <- trimws(sub(",\\s*\\d+\\s*,\\s*[\\d\\s\u2013-]+\\s*$", "", journal, perl = TRUE))
    }
  }

  # ", Volume 18" in journal -> extract volume if not already set
  if (!nzchar(volume)) {
    vol_match <- regmatches(journal, regexec(",\\s*Volume\\s+(\\d+)\\s*$", journal, perl = TRUE))[[1]]
    if (length(vol_match) >= 2) {
      volume <- vol_match[2]
      journal <- trimws(sub(",\\s*Volume\\s+\\d+\\s*$", "", journal, perl = TRUE))
    }
  }

  # Remove any remaining trailing ", PAGES" (e.g. ", 221–242") from journal
  journal <- trimws(sub(",\\s*\\d+[\\s\u2013-]+\\d+\\s*$", "", journal, perl = TRUE))

  list(journal = journal, volume = volume, number = number, year = year)
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

last_name_for_sort <- function(full_name) {
  words <- strsplit(trimws(full_name), "\\s+")[[1]]
  if (length(words) == 0) return("")
  tolower(words[length(words)])
}

# Remove prize/award text from notes so BibTeX does not include it
strip_prizes_from_note <- function(s) {
  if (is.null(s) || !nzchar(trimws(s))) return("")
  s <- trimws(s)
  s <- gsub("[, ]*Winner of[^.]*\\.?", "", s)
  s <- gsub("[, ]*Winner of.*$", "", s)
  s <- trimws(gsub("\\s+", " ", s))
  gsub("^[,.\\. ]+|[,. ]+$", "", s)
}

paper_to_bibtex <- function(p, slug, is_working_paper = FALSE) {
  auths <- p$authors %||% list()
  coauthor_names <- vapply(auths, function(a) trimws(a$name %||% ""), character(1))
  all_names <- c(SITE_AUTHOR, coauthor_names[nzchar(coauthor_names)])
  all_names <- all_names[order(vapply(all_names, last_name_for_sort, character(1)))]
  author_str <- paste(vapply(all_names, function(n) bib_escape(n), character(1)), collapse = " and ")
  title_str <- bib_escape(p$title %||% "")
  parsed_venue <- parse_venue(p$venue %||% "")
  journal_str <- bib_escape(parsed_venue$journal)
  volume_str <- bib_escape(parsed_venue$volume)
  number_str <- bib_escape(parsed_venue$number)
  year <- p$year %||% parsed_venue$year
  year_str <- if (!is.na(year) && nzchar(year)) year else ""
  url_str <- bib_escape(p$title_url %||% "")
  if (!nzchar(url_str) && length(p$links %||% list()) > 0) url_str <- bib_escape(p$links[[1]]$url %||% "")
  raw_notes <- strip_prizes_from_note(p$notes %||% "")
  note_str <- bib_escape(raw_notes)
  if (is_working_paper) note_str <- "Working paper."
  if (!is_working_paper && !nzchar(note_str)) note_str <- ""

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
      if (nzchar(journal_str)) sprintf("  journal = {%s},", journal_str),
      if (nzchar(volume_str)) sprintf("  volume = {%s},", volume_str),
      if (nzchar(number_str)) sprintf("  number = {%s},", number_str),
      if (nzchar(year_str)) sprintf("  year = {%s},", year_str),
      if (nzchar(note_str)) sprintf("  note = {%s},", note_str),
      if (nzchar(url_str)) sprintf("  url = {%s}", url_str)
    )
  }
  lines <- lines[nzchar(lines)]
  if (length(lines) > 1) lines[length(lines)] <- sub(",$", "", lines[length(lines)])
  paste(lines, collapse = "\n")
}
