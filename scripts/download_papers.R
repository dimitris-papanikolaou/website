#!/usr/bin/env Rscript
# Download all Dropbox-linked files from content/publications.yml into assets/papers/,
# then update the YAML to use local paths.
# Run from project root: Rscript scripts/download_papers.R

suppressWarnings(suppressPackageStartupMessages(library(yaml)))

args <- commandArgs(trailingOnly = FALSE)
script <- sub("^--file=", "", args[grep("^--file=", args)])
project_root <- if (length(script)) normalizePath(dirname(dirname(script)), winslash = "/", mustWork = FALSE) else getwd()
if (!dir.exists(project_root)) project_root <- getwd()
setwd(project_root)

yaml_path <- file.path(project_root, "content", "publications.yml")
papers_dir <- file.path(project_root, "assets", "papers")
dir.create(papers_dir, recursive = TRUE, showWarnings = FALSE)

pubs <- read_yaml(yaml_path)
url_to_local <- character(0)
seen_names <- character(0)

for (entry in pubs) {
  links <- entry$links %||% list()
  for (i in seq_along(links)) {
    url <- links[[i]]$url
    if (is.null(url) || !startsWith(url, "https://www.dropbox.com/")) next
    path_part <- sub("\\?.*$", "", url)
    parts <- strsplit(path_part, "/", fixed = TRUE)[[1]]
    base_name <- utils::URLdecode(parts[length(parts)])
    if (!nzchar(base_name)) next
    name <- base_name
    k <- 0
    while (name %in% names(seen_names) && seen_names[name] != url) {
      k <- k + 1
      if (grepl("\\.", name)) {
        name <- sub("(.*)\\.([^.]+)$", paste0("\\1_", k, ".\\2"), base_name)
      } else {
        name <- paste0(base_name, "_", k)
      }
    }
    seen_names[name] <- url
    dest <- file.path(papers_dir, name)
    local_path <- file.path("assets", "papers", name)
    local_path <- gsub("\\\\", "/", local_path)
    if (file.exists(dest)) {
      message("Already exists: ", name)
      url_to_local[url] <- local_path
      next
    }
    message("Downloading: ", name, " ...")
    tryCatch({
      utils::download.file(url, dest, mode = "wb", quiet = TRUE)
      if (file.exists(dest) && file.info(dest)$size > 0) {
        url_to_local[url] <- local_path
        message("  OK -> ", local_path)
      }
    }, error = function(e) message("  Failed: ", conditionMessage(e)))
    Sys.sleep(0.5)
  }
}

# Update YAML by text replacement to preserve structure
txt <- readLines(yaml_path, encoding = "UTF-8", warn = FALSE)
for (i in seq_along(url_to_local)) {
  old_url <- names(url_to_local)[i]
  new_path <- url_to_local[i]
  old_line <- paste0("url: ", old_url)
  new_line <- paste0("url: ", new_path)
  txt <- sub(old_line, new_line, txt, fixed = TRUE)
}
writeLines(txt, yaml_path, useBytes = FALSE)
message("\nUpdated ", yaml_path, " with ", length(url_to_local), " local paths.")
