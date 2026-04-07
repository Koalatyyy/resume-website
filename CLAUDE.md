# Project Instructions

## Stack
Static single-page resume. No build step. HTML + CSS + vanilla JS only — no frameworks, no npm.

## Files
```
index.html     — content; placeholder sections marked with ↓ comments
style.css      — all styles; CSS custom properties in :root
script.js      — nav, mobile menu, scroll reveal, Formspree contact form
.htaccess      — security headers (CSP, HSTS, X-Frame), Cache-Control, redirects
sitemap.xml    — lastmod auto-updated by CI on deploy
resume.pdf     — linked by download buttons
```

## Repository
`Haggath/resume-website` on GitHub (main branch)

## Deployment
Push to `main` → GitHub Actions → FTP to OVH → Cloudflare cache purge → IndexNow ping.
No manual deploy. `.htaccess` IS deployed (not excluded). CI also validates HTML with vnu.jar.

## Security — linked constraints (change one, update the others)
- **CSP lives in `.htaccess`**. If you add/remove an external script or API endpoint, update `script-src`, `connect-src`, and/or `form-action` in `.htaccess` to match.
- **SRI hashes on external scripts** in `index.html`. If the Plausible script URL changes, recompute `integrity=` with `sha256-$(...)`.
- **Inline script hash**: The Plausible init `<script>` block has its SHA-256 in `.htaccess` `script-src`. If that inline block changes, recompute the hash — use **CRLF** line endings (Windows file), not LF.
- **Formspree endpoint**: `https://formspree.io/f/maqlarpj`. Referenced in `script.js` (fetch) and `.htaccess` (`connect-src`, `form-action`).

## Theming — two places for light mode
Light mode tokens live in **both**:
1. `@media (prefers-color-scheme: light) :root:not([data-theme="dark"])` 
2. `[data-theme="light"]`

Always update both. Dark mode tokens are in `:root` at the top of `style.css`.

## Hosting
OVH shared hosting (FTP). Cloudflare full-proxy in front — cache purged on every deploy. CRLF line endings on Windows.

## External services
| Service | Purpose |
|---|---|
| Formspree | Contact form submissions |
| Plausible | Analytics (SRI-hashed script) |
| Cloudflare | CDN, proxy, auto-injects Insights script server-side |
| IndexNow | Search engine ping on deploy |

## Web search / research
Be concise — don't narrate search results, just apply what's needed.

---

# Claude for Chrome
- Use `read_page` for element refs from the accessibility tree
- Use `find` to locate elements by description
- Interact via `ref`, not coordinates
- Never take screenshots unless explicitly requested
