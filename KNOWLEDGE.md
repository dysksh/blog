# KNOWLEDGE.md

## Architecture

### Build Flow

```
Markdown → git push → GitHub Actions → Python build (Pandoc)
→ HTML / index / tags / RSS / search-index.json → GitHub Pages (gh-pages branch)
```

### Image Delivery

```
Image → S3 (manual upload) → CloudFront → img.example.com
```

## Design Principles

- **Platform-independent**: no vendor lock-in, easy to switch hosting
- **Markdown as asset**: portable to Hugo/Astro/Next.js/Zenn etc.
- **Minimal dependencies**: only Pandoc + Python, no frameworks or themes
- **Unbreakable**: no DB, no CMS, no plugins — static HTML only
- **Git-managed**: full diff/history/blame for all articles

## URL Design Rationale

### kebab-case

- Google treats `-` as word separator (de facto standard)
- Human-readable in URLs
- Consistent with UNIX conventions

### Trailing slash

- Matches directory structure (`posts/<slug>/index.html`)
- Static site standard
- Stable relative path resolution

### No date/category in URL

- Articles don't look outdated on rewrite
- Category changes don't break URLs
- URL stability is top priority

## Front Matter

| Field | Required | Purpose |
|-------|----------|---------|
| title | yes | title, search index, RSS |
| date | yes | sort order for article list |
| updated | no | display update date, SEO |
| tags | no | tag pages, search filter |

## Search

- `search-index.json` generated at build (title, url, tags, content)
- Client-side fuzzy search via Fuse.js
- Full-text search works fine up to ~200 articles (~500KB JSON)
- Can switch to excerpt-only later if needed

## Code Blocks

- Prism.js for syntax highlighting
- Copy button (~10 lines JS)
- Line numbers / line highlight available
- Language specification required in Markdown

## Diagrams (Mermaid)

- Loaded via CDN (no framework dependency)
- Natively supported in GitHub Markdown
- Can be exported to PNG as fallback
- Supports flowcharts, sequence diagrams, architecture diagrams

## Comments

- No comments initially
- Add giscus (GitHub Discussions based) when needed
- Just add a script tag to HTML template
- GitHub-dependent, but data exportable via GitHub API

## Cost

| Service | Monthly |
|---------|---------|
| GitHub Pages | $0 |
| S3 | ~$0.02 |
| CloudFront | $0–0.10 |
| Custom domain (optional) | ~$1 |
| **Total** | **~$1** |

## Custom Domain

- Start with `username.github.io`
- Add custom domain later if needed
- Use Cloudflare (free) for DNS
