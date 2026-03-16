# TODO.md

## Phase 1: Foundation

- [x] Create directory structure (`posts/`, `templates/`, `scripts/`)
- [x] Create HTML template (inline in `build.py`)
  - [x] Canonical URL
  - [x] Prism.js
  - [x] Mermaid CDN
  - [x] Copy button JS
  - [x] Navigation
- [x] Create CSS (`style.css`)
- [x] Create build script (`scripts/build.py`)
  - [x] Front matter parsing
  - [x] Article HTML generation via Pandoc
  - [x] Article index page (date desc)
  - [x] Tag pages
  - [x] search-index.json
  - [x] rss.xml
- [x] GitHub Actions config (`.github/workflows/build.yml`)
- [x] Verify with sample article

## Phase 2: Content

- [x] Top page (profile + recent posts + tags)
- [x] About page (`pages/about.md`)
- [x] Search page (Fuse.js)
- [x] Sample articles (hello-world, markdown-guide)

## Phase 3: Image Infrastructure (optional)

- [ ] S3 bucket
- [ ] CloudFront distribution
- [ ] Image upload workflow

## Phase 4: Future

- [ ] Custom domain setup
- [ ] img.example.com subdomain
- [ ] giscus comments
- [ ] Pagination (when articles > 100)
- [ ] OGP (Open Graph Protocol)
- [ ] sitemap.xml
