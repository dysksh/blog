# TODO.md

## Phase 1: Foundation

- [ ] Create directory structure (`posts/`, `templates/`, `scripts/`)
- [ ] Create HTML template (`templates/post.html`)
  - [ ] Pandoc template variables ($title$, $body$)
  - [ ] Canonical URL
  - [ ] Prism.js
  - [ ] Mermaid CDN
  - [ ] Copy button JS
  - [ ] Navigation
- [ ] Create CSS (`style.css`)
- [ ] Create build script (`scripts/build.py`)
  - [ ] Front matter parsing
  - [ ] Article HTML generation via Pandoc
  - [ ] Article index page (date desc)
  - [ ] Tag pages
  - [ ] search-index.json
  - [ ] rss.xml
- [ ] GitHub Actions config (`.github/workflows/build.yml`)
- [ ] Verify with sample article

## Phase 2: Content

- [ ] Top page (profile + recent posts + tags)
- [ ] About page
- [ ] Search page (Fuse.js)

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
