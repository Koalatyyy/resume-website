# SEO & Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve recruiter first-impression quality on haggath.re and its blog by adding a hero credibility bar, fixing a stale schema date, adding blog syntax highlighting and prev/next navigation, and auto-syncing the Writing section from blog post frontmatter via CI.

**Architecture:** Main site (`index.html` + `style.css`) is plain HTML/CSS with no build step. The blog is Eleventy (Nunjucks templates, markdown posts, built to `blog/_site/`). A new Node.js script (`scripts/sync-writing.js`) regenerates the Writing section cards in `index.html` from post frontmatter; it runs as a CI step before the HTML validator and FTP deploy. Syntax highlighting uses `@11ty/eleventy-plugin-syntaxhighlight` (Prism.js) added to the blog's Eleventy config.

**Tech Stack:** HTML, CSS, Nunjucks (Eleventy), Node.js (script), GitHub Actions (CI)

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `index.html` | Modify | Add hero credibility bar; add writing-posts sentinel comments; fix stale schema date |
| `style.css` | Modify | Style `.hero-creds` credibility bar |
| `blog/package.json` | Modify | Add `@11ty/eleventy-plugin-syntaxhighlight` dependency |
| `blog/eleventy.config.js` | Modify | Register syntax highlight plugin; add `cssclasses` passthrough |
| `blog/src/_includes/base.njk` | Modify | Add Prism CSS link; add post-nav styles |
| `blog/src/_includes/post.njk` | Modify | Add `<time>` wrapper on date; add prev/next post navigation |
| `blog/src/index.njk` | Modify | Add `<time>` wrappers on post list dates |
| `blog/src/posts/guardduty-suppression-rules.md` | Modify | Add language annotations to fenced code blocks |
| `blog/src/posts/macie-suppression-rules.md` | Modify | Add language annotations to fenced code blocks |
| `scripts/sync-writing.js` | Create | Reads post frontmatter, regenerates Writing cards in `index.html` |
| `.github/workflows/deploy.yml` | Modify | Add sync-writing step before HTML validation |

---

## Task 1: Hero Credibility Bar (HTML + CSS)

**Files:**
- Modify: `index.html` (around line 342, between `<p class="hero-bio">` and `<div class="hero-actions">`)
- Modify: `style.css` (after `.hero-bio` styles)

- [ ] **Step 1: Add the credibility bar HTML**

In `index.html`, insert the following between the closing `</p>` of `.hero-bio` (line 342) and `<div class="hero-actions">` (line 343):

```html
          <div class="hero-creds" aria-label="Key credentials">
            <span>Amazon Web Services</span>
            <span aria-hidden="true">·</span>
            <span>7 Years</span>
            <span aria-hidden="true">·</span>
            <span>GuardDuty</span>
            <span aria-hidden="true">·</span>
            <span>CloudTrail</span>
            <span aria-hidden="true">·</span>
            <span>NIST 800-61</span>
          </div>
```

- [ ] **Step 2: Add CSS for `.hero-creds`**

In `style.css`, find the `.hero-bio` block and add after it:

```css
.hero-creds {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.375rem 0.5rem;
  margin-bottom: 1.75rem;
  font-size: 0.8125rem;
  color: var(--text-muted);
  letter-spacing: 0.01em;
}
```

- [ ] **Step 3: Verify visually**

Open `index.html` in a browser (or live server). Confirm the credibility bar appears between the bio and the CTA buttons, is single-line on desktop, and wraps gracefully on a narrow viewport (< 480px).

- [ ] **Step 4: Commit**

```bash
git add index.html style.css
git commit -m "feat: add hero credibility bar"
```

---

## Task 2: Fix Stale Schema Date

**Files:**
- Modify: `index.html` (the `Demand` JSON-LD block, around line 179)

- [ ] **Step 1: Update `availabilityStarts`**

In `index.html`, find the `Demand` JSON-LD block. Change:

```json
"availabilityStarts": "2026-05-02",
```

to:

```json
"availabilityStarts": "2026-05-10",
```

Note: the CI step at line 44 of `deploy.yml` already auto-updates `dateModified` on every deploy — `availabilityStarts` is a separate field that represents when you became available and should be set to today's date manually when it changes.

- [ ] **Step 2: Commit**

```bash
git add index.html
git commit -m "fix: update Demand schema availabilityStarts to current date"
```

---

## Task 3: Add Writing-Posts Sentinel Comments to `index.html`

The sync script (Task 6) needs two HTML comments as anchors to replace the Writing cards block. Add them now so the structure is clear, and verify the section looks unchanged after adding them.

**Files:**
- Modify: `index.html` (the `#writing` section, around lines 918–950)

- [ ] **Step 1: Wrap the existing writing cards with sentinel comments**

In `index.html`, find the `#writing` section. The cards currently start after the `<div class="edu-list">` opening tag. Wrap only the post cards (not the dev.to card) like this:

```html
    <section id="writing">
      <div class="container">
        <h2 class="section-title">Writing</h2>
        <div class="edu-list">
          <!-- writing-posts:start -->
          <article class="edu-card">
            <div class="edu-header">
              <div>
                <h3 class="edu-degree">Leveraging GuardDuty suppression rules to eliminate noise</h3>
                <p class="edu-institution">May 2026 &middot; AWS Security</p>
              </div>
              <a href="/blog/guardduty-suppression-rules/" class="btn btn-outline btn-sm">Read</a>
            </div>
            <p class="edu-detail">How to use suppression rules, trusted IP lists, and threat intel lists to reduce GuardDuty alert noise without losing the audit trail.</p>
          </article>
          <article class="edu-card">
            <div class="edu-header">
              <div>
                <h3 class="edu-degree">Leveraging Macie suppression rules to eliminate noise</h3>
                <p class="edu-institution">May 2026 &middot; AWS Security</p>
              </div>
              <a href="/blog/macie-suppression-rules/" class="btn btn-outline btn-sm">Read</a>
            </div>
            <p class="edu-detail">How to use suppression rules, allow lists, and finding filters to reduce Amazon Macie alert noise across your S3 data estate.</p>
          </article>
          <!-- writing-posts:end -->
          <article class="edu-card">
            <div class="edu-header">
              <div>
                <h3 class="edu-degree">dev.to/haggath</h3>
                <p class="edu-institution">AWS Security &amp; Detection Engineering</p>
              </div>
              <a href="https://dev.to/haggath" target="_blank" rel="noopener noreferrer" class="btn btn-outline btn-sm">Read</a>
            </div>
            <p class="edu-detail">Writing about AWS security, threat detection, and cloud defence. Topics include GuardDuty, CloudTrail analysis, detection engineering workflows, and CTF writeups.</p>
          </article>
        </div>
        <div style="margin-top:1.5rem;text-align:center">
          <a href="/blog/" class="btn btn-outline btn-sm">Blog Posts &rarr;</a>
        </div>
      </div>
    </section>
```

- [ ] **Step 2: Verify the page still renders correctly**

Open `index.html` in browser. The Writing section should look identical to before — the comments are invisible.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "chore: add sentinel comments for writing-posts sync script"
```

---

## Task 4: Blog — Syntax Highlighting

**Files:**
- Modify: `blog/package.json`
- Modify: `blog/eleventy.config.js`
- Modify: `blog/src/_includes/base.njk`
- Modify: `blog/src/posts/guardduty-suppression-rules.md`
- Modify: `blog/src/posts/macie-suppression-rules.md`

- [ ] **Step 1: Install the Eleventy syntax highlight plugin**

```bash
cd blog && npm install --save-dev @11ty/eleventy-plugin-syntaxhighlight
```

Expected: `blog/package.json` now lists `@11ty/eleventy-plugin-syntaxhighlight` under `devDependencies`, and `blog/node_modules/` is updated.

- [ ] **Step 2: Register the plugin in `eleventy.config.js`**

In `blog/eleventy.config.js`, add at the top:

```js
const syntaxHighlight = require("@11ty/eleventy-plugin-syntaxhighlight");
```

Then inside `module.exports = function (eleventyConfig) {`, add as the first line:

```js
  eleventyConfig.addPlugin(syntaxHighlight);
```

- [ ] **Step 3: Add the Prism CSS theme to `base.njk`**

In `blog/src/_includes/base.njk`, add the following `<link>` inside `<head>`, after the existing `<link rel="stylesheet" href="/blog/style.css">` line:

```html
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1/themes/prism-tomorrow.css">
```

Then add a `<style>` override block right after that link to match the site's existing code block padding and font size, and to prevent the Prism theme from overriding the border-radius:

```html
  <style>
    pre[class*="language-"] {
      border-radius: var(--radius);
      border: 1px solid var(--border);
      font-size: 0.875rem;
      margin-bottom: 1.25rem;
      overflow-x: auto;
      white-space: pre-wrap;
      word-break: break-all;
    }
    code[class*="language-"] {
      font-size: 0.875rem;
    }
  </style>
```

- [ ] **Step 4: Add language annotations to the GuardDuty post**

In `blog/src/posts/guardduty-suppression-rules.md`, find the JSON code block (around line 159). Change the opening fence from:

````
```json
````

to ensure it reads exactly:

````
```json
````

(It should already say `json` — verify it does. If the fence has no language tag, add `json`. The plugin uses the tag to apply highlighting.)

- [ ] **Step 5: Check the Macie post for code blocks**

Open `blog/src/posts/macie-suppression-rules.md`. If it contains any fenced code blocks, ensure each has an appropriate language tag (`json`, `python`, `bash`, etc.). If there are none, skip.

- [ ] **Step 6: Build and verify**

```bash
cd blog && npx @11ty/eleventy
```

Expected: builds without errors. Open `blog/_site/guardduty-suppression-rules/index.html` in a browser and confirm the JSON block has syntax colouring (keywords in one colour, strings in another).

- [ ] **Step 7: Commit**

```bash
cd ..
git add blog/package.json blog/eleventy.config.js blog/src/_includes/base.njk blog/src/posts/
git commit -m "feat: add Prism.js syntax highlighting to blog posts"
```

---

## Task 5: Blog — `<time>` Elements and Prev/Next Navigation

**Files:**
- Modify: `blog/src/_includes/post.njk`
- Modify: `blog/src/index.njk`

- [ ] **Step 1: Wrap the post date in `post.njk` with `<time>`**

In `blog/src/_includes/post.njk`, find line 43:

```html
  <p class="post-meta">{{ date | readableDate }} &middot; {{ content | readingTime }} min read</p>
```

Replace with:

```html
  <p class="post-meta"><time datetime="{{ date | htmlDateString }}">{{ date | readableDate }}</time> &middot; {{ content | readingTime }} min read</p>
```

- [ ] **Step 2: Add prev/next navigation to `post.njk`**

In `blog/src/_includes/post.njk`, after `{{ content | safe }}` and before the closing `</div>`, add:

```html
  {% set postList = collections.posts %}
  {% set currentIndex = 0 %}
  {% for p in postList %}
    {% if p.url == page.url %}{% set currentIndex = loop.index0 %}{% endif %}
  {% endfor %}
  {% set prevPost = postList[currentIndex + 1] %}
  {% set nextPost = postList[currentIndex - 1] if currentIndex > 0 else null %}
  {% if prevPost or nextPost %}
  <nav class="post-nav" aria-label="Post navigation">
    <div class="post-nav-inner">
      {% if prevPost %}
      <a href="/blog{{ prevPost.url }}" class="post-nav-link post-nav-prev">
        <span class="post-nav-dir">← Older</span>
        <span class="post-nav-title">{{ prevPost.data.title }}</span>
      </a>
      {% else %}<div></div>{% endif %}
      {% if nextPost %}
      <a href="/blog{{ nextPost.url }}" class="post-nav-link post-nav-next">
        <span class="post-nav-dir">Newer →</span>
        <span class="post-nav-title">{{ nextPost.data.title }}</span>
      </a>
      {% else %}<div></div>{% endif %}
    </div>
  </nav>
  {% endif %}
```

- [ ] **Step 3: Add post-nav styles to `base.njk`**

In `blog/src/_includes/base.njk`, inside the existing `<style>` block (after the `.back-link:hover` rule), add:

```css
    .post-nav { margin-top: 3rem; border-top: 1px solid var(--border); padding-top: 1.5rem; }
    .post-nav-inner { display: flex; justify-content: space-between; gap: 1rem; }
    .post-nav-link { display: flex; flex-direction: column; gap: 0.25rem; text-decoration: none; max-width: 45%; }
    .post-nav-link:hover .post-nav-title { color: var(--accent); }
    .post-nav-dir { font-size: 0.8125rem; color: var(--text-muted); }
    .post-nav-title { font-size: 0.9375rem; font-weight: 600; color: var(--text); line-height: 1.35; }
    .post-nav-next { text-align: right; margin-left: auto; }
```

- [ ] **Step 4: Wrap dates in `index.njk` with `<time>`**

In `blog/src/index.njk`, find:

```html
      <div class="post-date">{{ post.date | readableDate }}</div>
```

Replace with:

```html
      <time class="post-date" datetime="{{ post.date | htmlDateString }}">{{ post.date | readableDate }}</time>
```

- [ ] **Step 5: Build and verify**

```bash
cd blog && npx @11ty/eleventy
```

Open `blog/_site/guardduty-suppression-rules/index.html` in a browser. Confirm:
- The date line reads e.g. `May 10, 2026 · 8 min read` (date is now a `<time>` element, invisible to eye)
- A prev/next bar appears at the bottom with a link to the other post

- [ ] **Step 6: Commit**

```bash
cd ..
git add blog/src/_includes/post.njk blog/src/_includes/base.njk blog/src/index.njk
git commit -m "feat: add time elements and prev/next post navigation to blog"
```

---

## Task 6: Writing Section Sync Script

**Files:**
- Create: `scripts/sync-writing.js`

- [ ] **Step 1: Create the `scripts/` directory and sync script**

Create `scripts/sync-writing.js` with the following content:

```js
#!/usr/bin/env node
// Reads blog post frontmatter and regenerates the writing cards in index.html
// between <!-- writing-posts:start --> and <!-- writing-posts:end --> sentinels.
// Run: node scripts/sync-writing.js

const fs = require("fs");
const path = require("path");

const POSTS_DIR = path.join(__dirname, "../blog/src/posts");
const INDEX_FILE = path.join(__dirname, "../index.html");
const MAX_POSTS = 3;

function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return {};
  const raw = match[1];
  const result = {};
  for (const line of raw.split("\n")) {
    const colonIdx = line.indexOf(":");
    if (colonIdx === -1) continue;
    const key = line.slice(0, colonIdx).trim();
    const val = line.slice(colonIdx + 1).trim().replace(/^["']|["']$/g, "");
    result[key] = val;
  }
  return result;
}

function slugFromFilename(filename) {
  return filename.replace(/\.md$/, "");
}

function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-US", { month: "long", year: "numeric" });
}

function buildCard(post) {
  const date = formatDate(post.date);
  return `          <article class="edu-card">
            <div class="edu-header">
              <div>
                <h3 class="edu-degree">${post.title}</h3>
                <p class="edu-institution">${date} &middot; AWS Security</p>
              </div>
              <a href="/blog/${post.slug}/" class="btn btn-outline btn-sm">Read</a>
            </div>
            <p class="edu-detail">${post.excerpt}</p>
          </article>`;
}

function run() {
  const files = fs.readdirSync(POSTS_DIR).filter((f) => f.endsWith(".md"));

  const posts = files
    .map((f) => {
      const content = fs.readFileSync(path.join(POSTS_DIR, f), "utf8");
      const fm = parseFrontmatter(content);
      return { ...fm, slug: slugFromFilename(f) };
    })
    .filter((p) => p.title && p.date && !p.draft)
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .slice(0, MAX_POSTS);

  const cards = posts.map(buildCard).join("\n");

  const html = fs.readFileSync(INDEX_FILE, "utf8");
  const START = "<!-- writing-posts:start -->";
  const END = "<!-- writing-posts:end -->";
  const startIdx = html.indexOf(START);
  const endIdx = html.indexOf(END);

  if (startIdx === -1 || endIdx === -1) {
    console.error("Sentinel comments not found in index.html");
    process.exit(1);
  }

  const updated =
    html.slice(0, startIdx + START.length) +
    "\n" +
    cards +
    "\n          " +
    html.slice(endIdx);

  fs.writeFileSync(INDEX_FILE, updated, "utf8");
  console.log(`sync-writing: wrote ${posts.length} post card(s) to index.html`);
}

run();
```

- [ ] **Step 2: Test the script locally**

```bash
node scripts/sync-writing.js
```

Expected output:
```
sync-writing: wrote 2 post card(s) to index.html
```

Open `index.html` in a browser. The Writing section should show the same 2 cards as before (content unchanged, just regenerated). The dev.to card below the sentinel should be untouched.

- [ ] **Step 3: Verify sentinel idempotency**

Run the script a second time:

```bash
node scripts/sync-writing.js
```

Confirm the output is identical to the first run and `index.html` diff is clean (no duplicate content added).

- [ ] **Step 4: Commit**

```bash
git add scripts/sync-writing.js index.html
git commit -m "feat: add writing-posts sync script for CI auto-update"
```

---

## Task 7: Wire Sync Script into CI

**Files:**
- Modify: `.github/workflows/deploy.yml`

- [ ] **Step 1: Add the sync step to the deploy job**

In `.github/workflows/deploy.yml`, find the `deploy` job steps. After the "Update sitemap lastmod" `run:` step and before the "Setup Node" step, add:

```yaml
      - name: Sync writing posts to index.html
        run: node scripts/sync-writing.js
```

The full sequence in the deploy job should now read:

```yaml
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683

      - name: Update sitemap lastmod
        run: |
          TODAY=$(date -u +%Y-%m-%d)
          sed -i "s/\"dateModified\": \"[0-9-]*\"/\"dateModified\": \"$TODAY\"/" index.html
          sed -i "s|<lastmod>[0-9-]*</lastmod>|<lastmod>$TODAY</lastmod>|" sitemap.xml

      - name: Sync writing posts to index.html
        run: node scripts/sync-writing.js

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Build blog
        run: cd blog && npx @11ty/eleventy
```

Note: the sync script uses only Node.js built-ins (`fs`, `path`) — no `npm install` needed for it.

- [ ] **Step 2: Verify the validate job still passes**

The `validate` job runs `java -jar /tmp/vnu.jar --errors-only index.html`. Since the sync script only replaces content between the sentinel comments (same HTML structure), validation should still pass. No action needed — this is confirmed at deploy time.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/deploy.yml
git commit -m "ci: run sync-writing script before deploy to keep Writing section current"
```

---

## Self-Review

**Spec coverage:**
- [x] Hero credibility bar — Task 1
- [x] Stale `availabilityStarts` date — Task 2
- [x] Writing sentinel setup — Task 3
- [x] Syntax highlighting — Task 4
- [x] `<time>` elements on post and index dates — Task 5
- [x] Prev/next post navigation — Task 5
- [x] Sync script — Task 6
- [x] CI integration — Task 7

**Placeholder scan:** No TBDs, TODOs, or vague steps. All code blocks are complete.

**Type consistency:** `parseFrontmatter`, `slugFromFilename`, `formatDate`, `buildCard`, `run` are all defined and used consistently within `sync-writing.js`. Nunjucks variable names (`postList`, `currentIndex`, `prevPost`, `nextPost`) are consistent between definition and use in `post.njk`.

**Note on reading time (3b):** Already implemented in `post.njk` line 43 — no task needed.
