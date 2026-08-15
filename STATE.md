# Loop State — Fei Xiang Portfolio (feixiang.dev)

Last run: 2026-08-15 (L1 report-only triage — `index.html` optimization target)
Mode: L3 (source edits authorized by explicit human instruction for this batched loop run).

Repository context: single static page (`index.html`, ~37 KB). Served as-is via
Tailwind Play CDN, Font Awesome 6.7.2 CDN, Google Fonts, and an inline `<script>`.
No build step today.

## High Priority (index.html optimization — awaiting L2)

Each item is a candidate for one isolated fix (see constraint: one fix per run,
max 3 attempts). None touch `.env`/auth/secrets/payments.

- [x] 1. Replace blocking `alert('Resume preview coming soon!')` in `#showResumeBtn` with non-blocking inline `role="status"` (matches the Contact/Sign-In forms). **Why:** `alert()` blocks the main thread and is a confirmed a11y anti-pattern; trivial consistency win. Effort ~5 min. L2, in worktree.
- [x] 2. Add `<meta name="theme-color" content="#0f172a">` to `<head>`. **Why:** missing theme-color => mismatched mobile browser chrome on scroll (value matches the `#0f172a` hero-bg). Viewport meta is already correct — no revisit needed. Effort ~2 min. L2, in worktree.
- [x] 3. Preload Google Fonts stylesheet (currently render-blocking `<link>`). **Why:** FOUT + slower first paint. Use `rel="preload" as="style" onload="this.onload=null;this.rel='stylesheet'"`. `display=swap` already present. Effort ~10 min. L2, in worktree.
- [x] 4. Add JSON-LD `Person` structured data (name, url, sameAs, jobTitle). **Why:** helps Google understand/profile snippet; currently absent. Effort ~10 min. L2, in worktree.
- [ ] [OWNER-BLOCKED] 5. Replace `href="#"` social-link placeholders (Instagram, LinkedIn). **Why:** explicit `TODO(owner)` in markup; links are inert. **Cannot fix without real URLs** — needs owner input. Effort ~3 min once URLs provided. Blocked. *(skipped this L3 batch run — awaiting owner URLs; noted in PR.)*
- [ ] 6. Build Tailwind to a static CSS file and remove the Play CDN `<script src="cdn.tailwindcss.com">` + inline `tailwind.config`. **Why:** dominant perf issue — Play CDN compiles classes client-side via JS, so no CSS until JS runs (FOUC, slow LCP), and the full utility set isn't deterministic. Minimal fix: `npx tailwindcss -i ./src/input.css -o ./dist/style.css --minify`, add `tailwind.config.js`, keep current `extend` theme. Effort ~30–60 min incl. build setup + verifying every JIT class still resolves. L2, dedicated worktree, then dispatch verifier. *(Architectural — flag for review before attempting.)* *(skipped this L3 batch run — architectural; PR notes it as deferred.)*
- [x] 7. Subset Font Awesome to the 11 used icons (globe, bars, xmark, circle-info, code, check, file-pdf, instagram, linkedin, location-dot, envelope) instead of the full FA 6.7.2 CSS. **Why:** over-fetches unused icon CSS (~20 KB gzipped). Options: FA SVG sprite + `<svg>` (best), or `fontawesome-svg-core` subset. Effort ~15 min. L2, in worktree.
- [x] 8. Fix `autocomplete="tel"` on the free-form `#contactInfo` input ("Phone or other contact info"). **Why:** `tel` is misleading for a free-form field; better `autocomplete="off"` (or split into a dedicated phone field). Effort ~3 min. L2, in worktree.

## Watch List

- Contact form (`action="#"`) and Sign-In form (`action="#"`) have no backend wired — intentional per inline comments ("No backend is wired up yet"). Local validation only. Monitor; do not assume fixed.
- `#about-img` and `#contact-img` both reference `avatar.svg` (567 B, present). Fine for now; revisit next-gen/optimized if it ever becomes raster.
- `.nav-link` class is applied but has no custom CSS rule — relies on direct Tailwind classes. Not worth a triage fix.

## Recent Noise (ignored this run)

- Footer year is JS-driven (`new Date().getFullYear()`) — current and correct, no action.
- `prefers-reduced-motion` guard + `scroll-behavior: smooth` already present — good.
- Skip link, `aria-label`s, `role="status"`/`aria-live` usage already in place — pass a11y smell test.
- `.opencode/`, `__pycache__/`, `.pytest_cache/` are tooling artifacts, unrelated to the HTML page.

---
Run log: 2026-08-15T18:10:00Z — daily-triage L1 — index.html optimization analysis → 8 High-Priority todos recorded, 1 owner-blocked — tokens ~7k — outcome: report-only
Verified: 2026-08-15T18:20:00Z — L1 report-only re-triage — confirmed all 8 items match index.html ground truth; refined item #2 (viewport already correct) — no source edits — outcome: report-only

Run log: 2026-08-15T22:40:00Z — L3 batched implement (human-authorized; one-fix-per-run constraint overridden) in worktree `loop/index-optimize` on `index.html`.
- Implemented: #1 (alert→role=status live region + inline `<p id="resumeStatus">`), #2 (meta theme-color #0f172a), #3 (Google Fonts preload as=style + onload swap, noscript fallback, display=swap kept), #4 (JSON-LD Person: name/url/jobTitle; sameAs omitted — Instagram/LinkedIn are owner-blocked), #7 (removed FA 6.7.2 CSS + cdnjs preconnect; inlined the 11 used icons as `<svg fill="currentColor">` incl. the mobile bars/xmark toggle), #8 (autocomplete="tel"→"off").
- Skipped: #5 (OWNER-BLOCKED — needs real Instagram/LinkedIn URLs), #6 (architectural Tailwind Play CDN → static build; deferred per run instructions).
- Tests: no test runner is configured (static site; no package.json). Validated via Python: 0 leftover `fa-` classes, 0 `alert(` calls (only in comments), 0 `autocomplete="tel"`, JSON-LD `Person` parses, `role="status"` live regions = 3, inline `<svg>` = 17 (16 icons, bars toggle→2) each `focusable="false"`, structural tag balance OK (section/nav/form/button/footer balanced).
- Next: draft PR for human review before any main merge. Outcome: pending PR review.
