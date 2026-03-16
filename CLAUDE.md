# CLAUDE.md

## Overview

Static tech blog powered by Markdown. No frameworks, themes, or CMS.

## Tech Stack

- Articles: Markdown (YAML front matter)
- Build: Python script (Pandoc)
- CI/CD: GitHub Actions
- Hosting: GitHub Pages
- Images: S3 + CloudFront (img.example.com)
- Code highlight: Prism.js (+ copy button)
- Diagrams: Mermaid
- Search: JSON index + Fuse.js (client-side full-text)
- Feed: rss.xml (generated at build)
- Comments: none (giscus later if needed)

## Directory Structure

```
blog/
  posts/
    <slug>/
      index.md
  templates/
    post.html
  scripts/
    build.py
  public/          # build output (not committed)
```

## Branches

- `main`: Markdown articles, scripts, templates
- `gh-pages`: generated HTML (managed by GitHub Actions)

## Article Format

```markdown
---
title: Article Title
date: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
---

Body
```

## URL Design

- Articles: `/posts/<slug>/` (trailing slash)
- Tags: `/tags/<tag>/`
- Search: `/search/`
- About: `/about/`
- Slug: English, kebab-case, short
- Internal links: root-absolute paths (`/posts/<slug>/`)
- Images: full absolute URL (`https://img.example.com/blog/<slug>/xxx.png`)
- Canonical URL required in HTML

## Conventions

- Build script in Python
- Code blocks must specify language
- Images uploaded to S3 manually, referenced via full absolute URL in Markdown
- Generated HTML is never committed to main branch
