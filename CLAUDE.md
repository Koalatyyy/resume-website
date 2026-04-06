# Project Instructions

## Overview
Static resume website — plain HTML, CSS, and vanilla JS. No build step required.

## Structure
```
index.html   — single-page resume site
style.css    — all styles (CSS custom properties for easy theming)
script.js    — nav active state, mobile menu, footer year
resume.pdf   — drop your CV here (referenced by download buttons)
```

## Conventions
- No frameworks or dependencies; open index.html directly in a browser
- All placeholder content is marked with `↓` comments in index.html
- Color tokens live in `:root` in style.css — change `--accent` to retheme
- Do not be overly verbose when searching via the web for suggestions, reduce token usage


# Claude for Chrome

- Use `read_page` to get element refs from the accessibility tree
- Use `find` to locate elements by description
- Click/interact using `ref`, not coordinates
- NEVER take screenshots unless explicitly requested by the user
