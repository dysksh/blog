# SPEC.md

## Articles

- Managed as Markdown files
- One article = one directory (`posts/<slug>/index.md`)
- YAML front matter for metadata
  - `title` (required): article title
  - `date` (required): publish date (YYYY-MM-DD)
  - `updated` (optional): update date (YYYY-MM-DD)
  - `tags` (optional): list of tags

## URL Design

| Page | URL | HTML File |
|------|-----|-----------|
| Top | `/` | `public/index.html` |
| Article | `/posts/<slug>/` | `public/posts/<slug>/index.html` |
| Tag list | `/tags/` | `public/tags/index.html` |
| Tag page | `/tags/<tag>/` | `public/tags/<tag>/index.html` |
| Search | `/search/` | `public/search/index.html` |
| About | `/about/` | `public/about/index.html` |
| RSS | `/rss.xml` | `public/rss.xml` |
| Search index | `/search-index.json` | `public/search-index.json` |

- Slug: English, kebab-case, short
- Trailing slash required
- Canonical URL in HTML

## Build Process

1. Read all `posts/*/index.md`
2. Parse front matter
3. Convert each article to HTML via Pandoc (`templates/post.html`)
4. Generate article index page (date desc)
5. Generate tag pages (article list per tag)
6. Generate tag index page
7. Generate `search-index.json` (title, url, tags, content as plain text)
8. Generate `rss.xml`
9. Output everything to `public/`

## HTML Template

Pandoc template format. Required elements:

- `<meta charset="utf-8">`
- `<title>$title$</title>`
- `<link rel="canonical" href="...">`
- `<link rel="stylesheet" href="/style.css">`
- Prism.js CSS/JS
- Mermaid CDN
- Copy button JS
- Navigation (home, tags, search, about)

## Code Highlight

- Prism.js
- Language specification required in Markdown code blocks
- Copy button on each block
- Output as `<pre><code class="language-xxx">`

## Diagrams (Mermaid)

- Loaded from CDN
- Use ` ```mermaid ` blocks in Markdown
- Output as `<pre class="mermaid">` in HTML
- Rendered client-side

## Search

- `search-index.json` generated at build time
- Contains title, url, tags, content (plain text) per article
- Client-side fuzzy search via Fuse.js
- Search page (`/search/`) with input form and results area

## RSS

- `rss.xml` generated at build time
- Contains title, link, description per article

## Images

- Served via S3 + CloudFront
- Subdomain `img.example.com` (after custom domain setup)
- Referenced as full absolute URL: `![](https://img.example.com/blog/<slug>/xxx.png)`
- Image directory mirrors article slug
- Manual upload

## Top Page

- Brief profile
- Recent articles list
- Tag list
- Link to all articles

## Comments (future)

- giscus (GitHub Discussions based)
- Add script tag to HTML template
- No comments initially

## CI/CD

- GitHub Actions triggered on push to main
- Install Pandoc → build → deploy to gh-pages branch
- Uses `peaceiris/actions-gh-pages@v4`
- Generated HTML never committed to main
