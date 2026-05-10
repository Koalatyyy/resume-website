# SEO & Polish — Design Spec
**Date:** 2026-05-10  
**Goal:** Make haggath.re more attractive to recruiters arriving via LinkedIn referral. Primary actions: contact form submission and LinkedIn message. No content removed; additions and fixes only.

---

## 1. Hero Credibility Bar

**What:** A single row of text badges inserted between the hero bio paragraph and the CTA buttons, communicating seniority and toolset at a glance before the recruiter scrolls.

**Content:** `Amazon Web Services · 7 years · GuardDuty · CloudTrail · NIST 800-61`

**How:** A `<div class="hero-creds">` with `<span>` items separated by `·` middots. Styled in `style.css` — small font size (~0.8125rem), muted colour (`var(--text-muted)`), no wrapping on desktop, wraps gracefully on mobile. No new dependencies.

---

## 2. Stale Schema Date Fix

**What:** `availabilityStarts` in the `Demand` JSON-LD block is `2026-05-02`, which is in the past.

**Fix:** Update to today's date (`2026-05-10`) and add a comment noting it should be kept current. Not recruiter-visible but affects structured data accuracy.

---

## 3. Blog Reading Experience

All changes are in the Eleventy blog (`blog/src/`). The built output in `blog/_site/` is regenerated on deploy via CI — no manual edits to `_site/`.

### 3a. Syntax Highlighting

**What:** Code blocks in posts (e.g. the GuardDuty JSON example) render as unstyled monospace. Add Prism.js for syntax highlighting.

**How:** 
- Add `eleventy-plugin-syntaxhighlight` (wraps Prism) to `blog/package.json`
- Register the plugin in `eleventy.config.js`
- Add the Prism CSS theme (one of the dark variants matching the site palette — `prism-tomorrow` or similar) inlined into the blog's shared stylesheet or injected via a `<link>` in the post template
- Fenced code blocks in markdown get `language-json`, `language-python`, etc. annotations in existing posts

### 3b. Reading Time

**What:** The `readingTime` filter already exists in `eleventy.config.js` but isn't rendered on post pages.

**How:** Wire it into the post layout template (`blog/src/_includes/post.njk` or equivalent). Display as `X min read` next to the post date in the post meta line.

### 3c. Previous / Next Post Navigation

**What:** Post pages end with no onward journey. Add a simple prev/next bar at the bottom of each post.

**How:** In the post layout, use Eleventy's `collections.posts` to find adjacent items by index. Render a `<nav class="post-nav">` with two links: `← Previous post title` and `Next post title →`. If at the start or end of the collection, the missing direction is omitted. Styled to match the existing `.back-link` pattern.

### 3d. Semantic Date Elements

**What:** Post dates are currently rendered as plain text strings.

**Fix:** Wrap in `<time datetime="YYYY-MM-DD">` in the post layout and blog index template, using the `htmlDateString` filter (already defined) for the `datetime` attribute and `readableDate` for the display text.

---

## 4. Writing Section Auto-Sync (CI)

**Problem:** The Writing cards in `index.html` are hardcoded. As posts are added to the blog, `index.html` must be manually updated — it will go stale.

**Approach:** Add a Node.js script (`scripts/sync-writing.js`) that:
1. Reads all markdown files in `blog/src/posts/` 
2. Parses frontmatter (`title`, `date`, `excerpt`, `slug`)
3. Excludes posts with `draft: true` in frontmatter (so hello-world stays hidden)
4. Regenerates the writing cards HTML block between two sentinel comments in `index.html`:
   ```html
   <!-- writing-posts:start -->
   ...cards...
   <!-- writing-posts:end -->
   ```
5. Writes the updated `index.html` in-place

**CI integration:** Add a step to `.github/workflows/deploy.yml` that runs `node scripts/sync-writing.js` before the HTML validation and FTP deploy steps. This means every push regenerates the Writing section from the actual post list.

**Ordering:** Posts sorted newest-first by `date` frontmatter, matching the blog index order.

**Limit:** Show the 3 most recent posts as cards (same as current). The dev.to card is hardcoded and remains unchanged — it is not managed by the sync script.

---

## Out of Scope

- New blog post content
- Restructuring any existing sections
- Adding new dependencies to the main site (no npm, no build step on root)
- OG card (already exists and looks good)
