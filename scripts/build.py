#!/usr/bin/env python3
"""Build script for the static blog."""

import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape, unescape
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "posts"
TEMPLATES_DIR = ROOT / "templates"
PUBLIC_DIR = ROOT / "public"

SITE_TITLE = os.environ.get("SITE_TITLE", "Blog")
SITE_URL = os.environ.get("SITE_URL", "")
SITE_LANG = os.environ.get("SITE_LANG", "ja")
SITE_DESCRIPTION = os.environ.get(
    "SITE_DESCRIPTION", "ソフトウェアエンジニアリングに関する技術ブログ"
)
PAGES_DIR = ROOT / "pages"
# TODO: カスタムドメイン設定後はBASE_PATHを空にできる
BASE_PATH = os.environ.get("BASE_PATH", "")  # e.g. "/blog" for project sites

INDEX_MAX_POSTS = 10
RSS_MAX_POSTS = 20
SEARCH_MAX_RESULTS = 20
SEARCH_THRESHOLD = 0.3
SEARCH_CONTENT_LIMIT = 5000

def _nav_items():
    return [
        ("home", f"{BASE_PATH}/"),
        ("posts", f"{BASE_PATH}/posts/"),
        ("tags", f"{BASE_PATH}/tags/"),
        ("search", f"{BASE_PATH}/search/"),
        ("about", f"{BASE_PATH}/about/"),
    ]

PRISM_HEAD = (
    '<link rel="stylesheet"'
    ' href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-tomorrow.min.css"'
    ' integrity="sha384-wFjoQjtV1y5jVHbt0p35Ui8aV8GVpEZkyF99OXWqP/eNJDU93D3Ugxkoyh6Y2I4A"'
    ' crossorigin="anonymous">'
)

PRISM_MERMAID_SCRIPTS = """\
<script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js"
  integrity="sha384-ZM8fDxYm+GXOWeJcxDetoRImNnEAS7XwVFH5kv0pT6RXNy92Nemw/Sj7NfciXpqg"
  crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/plugins/autoloader/prism-autoloader.min.js"
  integrity="sha384-Uq05+JLko69eOiPr39ta9bh7kld5PKZoU+fF7g0EXTAriEollhZ+DrN8Q/Oi8J2Q"
  crossorigin="anonymous"></script>
<script>
document.querySelectorAll('pre[class] > code').forEach(function(code) {
  var pre = code.parentElement;
  var lang = pre.className;
  if (!lang) return;
  if (lang === 'mermaid') {
    pre.textContent = code.textContent;
    pre.className = 'mermaid';
    return;
  }
  code.className = 'language-' + lang;
  pre.className = '';
  Prism.highlightElement(code);
});
document.querySelectorAll('pre > code[class*="language-"]').forEach(function(code) {
  var pre = code.parentElement;
  var btn = document.createElement('button');
  btn.className = 'copy-btn';
  btn.textContent = 'copy';
  btn.addEventListener('click', function() {
    navigator.clipboard.writeText(code.textContent);
    btn.textContent = 'copied!';
    setTimeout(function() { btn.textContent = 'copy'; }, 2000);
  });
  pre.appendChild(btn);
});
</script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js"
  integrity="sha384-rbtjAdnIQE/aQJGEgXrVUlMibdfTSa4PQju4HDhN3sR2PmaKFzhEafuePsl9H/9I"
  crossorigin="anonymous"></script>
<script>mermaid.initialize({ startOnLoad: true });</script>"""


# --- Front matter parsing ---


def parse_front_matter(text):
    """Parse YAML front matter. Returns (metadata dict, body text)."""
    if not text.startswith("---"):
        return {}, text
    try:
        end = text.index("\n---\n", 3)
    except ValueError:
        return {}, text
    header = text[4:end]
    body = text[end + 5:]
    meta = {}
    for line in header.split("\n"):
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if key == "tags" and val.startswith("[") and val.endswith("]"):
            val = [v.strip().strip("\"'") for v in val[1:-1].split(",") if v.strip()]
        else:
            val = val.strip("\"'")
        meta[key] = val
    return meta, body


# --- Post loading ---


def load_posts():
    """Load and sort all posts by date descending."""
    posts = []
    if not POSTS_DIR.exists():
        return posts
    for post_dir in POSTS_DIR.iterdir():
        if not post_dir.is_dir():
            continue
        index_md = post_dir / "index.md"
        if not index_md.exists():
            continue
        text = index_md.read_text(encoding="utf-8")
        meta, body = parse_front_matter(text)
        meta["slug"] = post_dir.name
        meta["url"] = f"{BASE_PATH}/posts/{post_dir.name}/"
        meta["source"] = str(index_md)
        meta["body"] = body
        posts.append(meta)
    posts.sort(key=lambda p: p.get("date", ""), reverse=True)
    return posts


# --- HTML page wrapper ---


def _nav_html():
    return " ".join(f'<a href="{href}">{label}</a>' for label, href in _nav_items())


def page_html(title, content, path="/", description="", extra_head="", extra_scripts=""):
    """Wrap content in the site HTML shell."""
    canonical = f"{SITE_URL}{path}"
    desc_tag = ""
    if description:
        desc_tag = f'\n<meta name="description" content="{escape(description)}">'
    head_extra = f"\n{extra_head}" if extra_head else ""
    scripts = f"\n{extra_scripts}" if extra_scripts else ""
    return f"""<!DOCTYPE html>
<html lang="{SITE_LANG}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>{desc_tag}
<link rel="canonical" href="{canonical}">
<link rel="stylesheet" href="{BASE_PATH}/style.css">
<link rel="alternate" type="application/rss+xml" title="RSS" href="{BASE_PATH}/rss.xml">{head_extra}
</head>
<body>
<nav>{_nav_html()}</nav>
<main>
{content}
</main>{scripts}
</body>
</html>"""


def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# --- Build steps ---


def _externalize_links(html):
    """Add target="_blank" rel="noopener noreferrer" to external links."""
    def _replace(m):
        tag = m.group(0)
        href_match = re.search(r'href="([^"]*)"', tag)
        if not href_match:
            return tag
        href = href_match.group(1)
        if href.startswith(("/", "#")) or (SITE_URL and href.startswith(SITE_URL)):
            return tag
        return tag[:-1] + ' target="_blank" rel="noopener noreferrer">'

    return re.sub(r"<a\s[^>]*>", _replace, html)


def build_post(post):
    """Convert a single post to HTML via Pandoc."""
    result = subprocess.run(
        ["pandoc", post["source"], "--no-highlight", "-t", "html"],
        capture_output=True,
        text=True,
        check=True,
    )
    body_html = _externalize_links(result.stdout)
    post["body_html"] = body_html

    title = escape(post.get("title", ""))
    date = escape(post.get("date", ""))
    header_parts = [f"<h1>{title}</h1>", f'<time datetime="{date}">{date}</time>']
    if post.get("updated"):
        header_parts.append(
            f'<span class="updated">updated: {escape(post["updated"])}</span>'
        )
    if post.get("tags"):
        tag_links = " ".join(
            f'<a href="{BASE_PATH}/tags/{escape(t)}/">{escape(t)}</a>' for t in post["tags"]
        )
        header_parts.append(f'<div class="tags">{tag_links}</div>')

    article = (
        "<article>\n<header>\n"
        + "\n".join(header_parts)
        + "\n</header>\n"
        + body_html
        + "\n</article>"
    )

    desc = ""
    for line in post.get("body", "").strip().split("\n"):
        line = line.strip()
        if not line:
            if desc:
                break
            continue
        if line.startswith("#") or line.startswith("```"):
            break
        desc += " " + line if desc else line
    desc = desc[:160]

    html = page_html(
        title=post.get("title", ""),
        content=article,
        path=post["url"],
        description=desc,
        extra_head=PRISM_HEAD,
        extra_scripts=PRISM_MERMAID_SCRIPTS,
    )
    write_file(PUBLIC_DIR / "posts" / post["slug"] / "index.html", html)


def build_index(posts):
    """Generate top page with profile, recent posts, and tags."""
    items = "\n".join(
        f'<li><time>{escape(p.get("date", ""))}</time>'
        f' <a href="{p["url"]}">{escape(p.get("title", ""))}</a></li>'
        for p in posts[:INDEX_MAX_POSTS]
    )
    tags = {}
    for p in posts:
        for t in p.get("tags", []):
            tags[t] = tags.get(t, 0) + 1
    tag_links = " ".join(
        f'<a href="{BASE_PATH}/tags/{escape(t)}/">{escape(t)} ({c})</a>'
        for t, c in sorted(tags.items())
    )
    content = f"<h1>{escape(SITE_TITLE)}</h1>\n"
    content += f'<p class="site-description">{escape(SITE_DESCRIPTION)}</p>\n'
    content += f'<h2>Recent Posts</h2>\n<ul class="post-list">\n{items}\n</ul>\n'
    if len(posts) > INDEX_MAX_POSTS:
        content += f'<p><a href="{BASE_PATH}/posts/">View all posts &rarr;</a></p>\n'
    if tag_links:
        content += f'<h2>Tags</h2>\n<div class="tag-list">{tag_links}</div>\n'
    write_file(
        PUBLIC_DIR / "index.html",
        page_html(SITE_TITLE, content, f"{BASE_PATH}/", description=SITE_DESCRIPTION),
    )


def build_posts_index(posts):
    """Generate /posts/ listing all articles."""
    items = "\n".join(
        f'<li><time>{escape(p.get("date", ""))}</time>'
        f' <a href="{p["url"]}">{escape(p.get("title", ""))}</a></li>'
        for p in posts
    )
    content = f'<h1>All Posts</h1>\n<ul class="post-list">\n{items}\n</ul>'
    write_file(
        PUBLIC_DIR / "posts" / "index.html",
        page_html("All Posts", content, f"{BASE_PATH}/posts/"),
    )


def build_tag_pages(posts):
    """Generate /tags/ and /tags/<tag>/ pages."""
    tags = {}
    for p in posts:
        for t in p.get("tags", []):
            tags.setdefault(t, []).append(p)
    tag_links = " ".join(
        f'<a href="{BASE_PATH}/tags/{escape(t)}/">{escape(t)} ({len(ps)})</a>'
        for t, ps in sorted(tags.items())
    )
    write_file(
        PUBLIC_DIR / "tags" / "index.html",
        page_html(
            "Tags",
            f'<h1>Tags</h1>\n<div class="tag-list">{tag_links}</div>',
            f"{BASE_PATH}/tags/",
        ),
    )
    for tag, tag_posts in tags.items():
        items = "\n".join(
            f'<li><time>{escape(p.get("date", ""))}</time>'
            f' <a href="{p["url"]}">{escape(p.get("title", ""))}</a></li>'
            for p in tag_posts
        )
        write_file(
            PUBLIC_DIR / "tags" / tag / "index.html",
            page_html(
                f"Tag: {tag}",
                f'<h1>Tag: {escape(tag)}</h1>\n<ul class="post-list">\n{items}\n</ul>',
                f"{BASE_PATH}/tags/{tag}/",
            ),
        )


def build_about_page():
    """Generate /about/ page from pages/about.md or fallback."""
    about_md = PAGES_DIR / "about.md"
    if about_md.exists():
        text = about_md.read_text(encoding="utf-8")
        meta, body = parse_front_matter(text)
        title = meta.get("title", "About")
        result = subprocess.run(
            ["pandoc", "--no-highlight", "-t", "html"],
            input=body,
            capture_output=True,
            text=True,
            check=True,
        )
        body_html = _externalize_links(result.stdout)
        content = f"<h1>{escape(title)}</h1>\n{body_html}"
    else:
        title = "About"
        content = "<h1>About</h1>\n<p>Coming soon.</p>"
    write_file(
        PUBLIC_DIR / "about" / "index.html",
        page_html(
            title,
            content,
            f"{BASE_PATH}/about/",
            extra_head=PRISM_HEAD,
            extra_scripts=PRISM_MERMAID_SCRIPTS,
        ),
    )


def build_search_page():
    """Generate /search/ page with Fuse.js."""
    content = """<h1>Search</h1>
<input type="text" id="search-input" placeholder="Search articles..." autofocus>
<ul id="search-results" class="post-list"></ul>
<script src="https://cdn.jsdelivr.net/npm/fuse.js@7.0.0/dist/fuse.min.js"
  integrity="sha384-PCSoOZTpbkikBEtd/+uV3WNdc676i9KUf01KOA8CnJotvlx8rRrETbDuwdjqTYvt"
  crossorigin="anonymous"></script>
<script>
var fuse;
fetch('%s/search-index.json')
  .then(function(r) { return r.json(); })
  .then(function(data) {
    fuse = new Fuse(data, { keys: ['title', 'tags', 'content'], threshold: %s, ignoreLocation: true });
  });
document.getElementById('search-input').addEventListener('input', function(e) {
  var q = e.target.value.trim();
  var el = document.getElementById('search-results');
  if (!q || !fuse) { el.innerHTML = ''; return; }
  var hits = fuse.search(q).slice(0, %s);
  el.innerHTML = '';
  hits.forEach(function(h) {
    var li = document.createElement('li');
    var a = document.createElement('a');
    a.setAttribute('href', h.item.url);
    a.textContent = h.item.title;
    li.appendChild(a);
    el.appendChild(li);
  });
});
</script>""" % (BASE_PATH, SEARCH_THRESHOLD, SEARCH_MAX_RESULTS)
    write_file(
        PUBLIC_DIR / "search" / "index.html",
        page_html("Search", content, f"{BASE_PATH}/search/"),
    )


def _strip_html(html):
    """Remove HTML tags and decode entities to plain text."""
    return unescape(re.sub(r"<[^>]+>", "", html))


def build_search_index(posts):
    """Generate search-index.json."""
    index = []
    for p in posts:
        plain = _strip_html(p.get("body_html", ""))
        index.append(
            {
                "title": p.get("title", ""),
                "url": p["url"],
                "tags": p.get("tags", []),
                "content": plain[:SEARCH_CONTENT_LIMIT],
            }
        )
    write_file(
        PUBLIC_DIR / "search-index.json",
        json.dumps(index, ensure_ascii=False),
    )


def build_rss(posts):
    """Generate rss.xml."""
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = SITE_TITLE
    SubElement(channel, "link").text = f"{SITE_URL}{BASE_PATH}/"
    SubElement(channel, "description").text = SITE_DESCRIPTION
    for p in posts[:RSS_MAX_POSTS]:
        date_str = p.get("date", "")
        if not date_str:
            continue
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            print(f"Warning: invalid date '{date_str}' in '{p.get('title', p['slug'])}', skipping RSS entry")
            continue
        item = SubElement(channel, "item")
        SubElement(item, "title").text = p.get("title", "")
        SubElement(item, "link").text = f"{SITE_URL}{p['url']}"
        guid = SubElement(item, "guid", isPermaLink="true")
        guid.text = f"{SITE_URL}{p['url']}"
        SubElement(item, "pubDate").text = format_datetime(dt)
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_str += tostring(rss, encoding="unicode")
    write_file(PUBLIC_DIR / "rss.xml", xml_str)


def copy_static():
    """Copy static assets to public."""
    for name in ("style.css",):
        src = TEMPLATES_DIR / name
        shutil.copy2(src, PUBLIC_DIR / name)


def main():
    if PUBLIC_DIR.exists():
        shutil.rmtree(PUBLIC_DIR)
    PUBLIC_DIR.mkdir()
    copy_static()
    posts = load_posts()
    for post in posts:
        build_post(post)
    build_index(posts)
    build_posts_index(posts)
    build_tag_pages(posts)
    build_about_page()
    build_search_page()
    build_search_index(posts)
    build_rss(posts)
    print(f"Built {len(posts)} posts")


if __name__ == "__main__":
    main()
