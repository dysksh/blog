# PLAN.md

## Phase 1: Foundation

1. **Create directory structure** — `posts/`, `templates/`, `scripts/`, `.github/workflows/`

2. **HTML template** (`templates/post.html`)
   - Pandoc template variables (`$title$`, `$body$`)
   - meta charset, canonical URL
   - Prism.js CSS/JS
   - Mermaid CDN
   - Copy button JS
   - Navigation (home, tags, search, about)

3. **Build script** (`scripts/build.py`)
   - Markdown → HTML via Pandoc
   - Article index page (sorted by date desc)
   - Tag pages
   - RSS (`rss.xml`)
   - Search index (`search-index.json`)
   - Pretty URLs (`posts/<slug>/index.html`)

4. **GitHub Actions** (`.github/workflows/build.yml`)
   - Trigger on push to main
   - Install Pandoc
   - Run `python scripts/build.py`
   - Deploy via `peaceiris/actions-gh-pages`

## Phase 2: Content & Style

5. **CSS** (`templates/style.css`) — simple layout, code block styling, responsive

6. **Static pages** — top page (profile + recent posts + tags), about, search

7. **Sample article** — one test post with front matter, code blocks, Mermaid diagram

## Phase 3: Image Infrastructure (optional)

8. **AWS setup** — S3 bucket, CloudFront distribution, `img.example.com` subdomain

## Phase 4: Future

9. Comments — giscus
10. Custom domain — DNS + GitHub Pages config
11. Pagination — when articles exceed 100
