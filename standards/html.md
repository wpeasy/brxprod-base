# HTML semantics & accessibility standard

Every element's tag is chosen for **what the content is**, never how it looks,
and every page meets WCAG 2.2 AA. Styling never decides markup: a semantic tag
is reset in the block's class CSS ([css.md](css.md)) if its defaults are
unwanted.

## 1. Setting tags and attributes in Bricks

Verified against Bricks 2.4.2's element schemas (`bricks/get-element-schema`
is authoritative — check it for any element not listed here):

| Setting | Use |
|---|---|
| `tag` | Div / Block: `div`, `section`, `a`, `article`, `nav`, `ol`, `ul`, `li`, `aside`, `address`, `figure`, `custom`. Heading: `h1`–`h6`. Basic Text: `div`, `p`, `span`, `figcaption`, `address`, `figure`. Image: `figure`, `div`. |
| `tag: "custom"` + `customTag` | any other element: `dl`, `dt`, `dd`, `time`, `blockquote`, `cite`, `header`, `footer`, `hgroup`, `menu`, `small`, `mark`, `abbr`, `strong`… |
| `_attributes` | repeater of `{ "name": …, "value": … }` rows — `aria-*`, `role`, `datetime`, `lang`, `data-*` |
| `_cssId` | the element's id, e.g. the target of `aria-labelledby` |
| `altText` (Image) | the image's alternative text |

Defaults to override deliberately: **Basic Text renders a `div`** (use `p` for
a paragraph); **Heading defaults to `h3`** (set the level the outline needs).

## 2. Page structure and landmarks

- Bricks wraps page content in `<main id="brx-content">` (verified) — **never
  add another `main`**. Header and footer templates render inside
  `#brx-header` / `#brx-footer`; check the rendered tag of those wrappers on
  the first build (`brxprod/render-frontend-html` or the front end) and don't
  duplicate a `header` / `footer` landmark Bricks already outputs.
- Navigation is `nav` with an `aria-label` ("Main", "Footer", "Breadcrumb") —
  every `nav` on a page needs a distinct name.
- Tangential content is `aside`; a self-contained piece is `article`.
- Every `section` is named: `aria-labelledby` → its heading's `_cssId`, or
  `aria-label` when it has no visible heading. An unnamed section is just a
  `div` to assistive tech.

## 3. Headings

- Exactly **one `h1`** per page; never skip a level going down.
- Levels follow the outline, not the font size — the size comes from class CSS.
- A group of tiles whose titles are `h3` sits under an `h2` — visually hidden
  (§6) if the design has no room for it.
- A heading with a kicker/subtitle: `hgroup` with the heading and a `p`.

## 4. Content types → elements

| Content | Markup |
|---|---|
| a collection of items (cards, features, logos, links) | `ul` > `li` — `ol` > `li` when order matters (steps, rankings) |
| term + description pairs (specs, FAQ facts, key/value data, contact details as labels) | `dl` > `dt` + `dd` (custom tags). `dt`/`dd` are direct children of `dl`, optionally grouped in a `div` per pair |
| a self-contained item (post, product, event, testimonial, profile) | `article`, with its own heading |
| a card in a collection | `ul` > `li` > `article.card` (or `li.card` when the card isn't self-contained) |
| a quote | `figure` > `blockquote` + `figcaption` (attribution, with `cite` for a work title) |
| a dated item | `time` with `datetime` (ISO 8601) in `_attributes` |
| contact details | `address` |
| an image with a caption | `figure` > image + `figcaption` |
| tabular data | a real `table` with `th` + `scope` — never a grid of divs. If no element can produce it, stop and ask |
| navigation (menu, breadcrumb, pagination, prev/next) | `nav` (named) > `ul`/`ol` > `li` > `a`; current item `aria-current="page"` |
| emphasis / importance | `em` / `strong` — not `b` / `i` for meaning |
| abbreviation | `abbr` with `title` the first time |

**Never fake a structure with Divs:** a list is a list, a table is a table, a
button is a button.

## 5. Links and buttons

- **`a` navigates** (has an `href`); **`button` acts** (opens, toggles,
  submits). Never a clickable `div`, never `href="#"` for an action.
- Link text makes sense out of context — no "click here" / "read more" alone;
  add context (visually hidden text or `aria-label` matching the visible text's
  start) when the design forces a short label.
- A link opening a new tab says so ("(opens in new tab)", visually hidden).
- Phone numbers: `tel:` links with the trunk "(0)" stripped; e-mail: `mailto:`.
- A whole-card link: one real link on the card's heading, stretched over the
  card with CSS — not the whole `article` wrapped in `a`.

## 6. ARIA and accessibility rules

1. **Native first.** Use the semantic element; add `role` only when no element
   exists for it. Never repeat a native role (`role="list"` on a `ul`) — except
   to restore list semantics Safari drops when `list-style: none` is set
   (`role="list"` on a styled `ul` is then correct).
2. **Name every control and region:** `aria-labelledby` (preferred, points at
   visible text) → `aria-label` → visually hidden text.
3. **Decorative is hidden:** decorative images, icons next to text, pattern
   art, `brxp-has-bg-media__media` → `aria-hidden="true"` (and empty `alt` on
   images). An empty `altText` alone is not enough — Bricks falls back to the
   attachment's alt.
4. **Informative images** have meaningful `altText`; icons that replace text
   get an accessible name.
5. **State is exposed** — `aria-expanded`, `aria-controls`, `aria-selected`,
   `aria-current`, `aria-pressed` — and kept in sync by the JS
   ([js.md](js.md)), never by CSS alone.
6. **Visually hidden text** uses a visually-hidden utility class — the
   framework's if `DESIGN_SYSTEM.md` lists one, otherwise a `visually-hidden`
   block class — never `display: none` (which hides it from screen readers too).
7. **Keyboard:** everything interactive is reachable and operable by keyboard
   in DOM order; never remove focus outlines without a visible replacement;
   no positive `tabindex`.
8. **Contrast:** text meets 4.5:1 (3:1 for large text and UI parts). Text on a
   brand or image background uses the `--brxp-a11y-*-text` tokens or a scrim.
9. **Never rely on colour alone** to convey meaning (errors, required fields,
   links in body text).
10. **Motion** respects `prefers-reduced-motion` (BRXProd's animation overrides
    handle Bricks animations; custom motion must too).
11. **Forms:** every field has a visible `label`; errors are announced
    (`aria-describedby` / `aria-live`) and identify the field.

## 7. Labels

Element labels follow the CSS standard (Title Case BEM segment). An element
with no BEM class is labelled by its role: `Item` (`li`), `Term` (`dt`),
`Description` (`dd`), `Paragraph`, `Link`, `Icon`, `Media (decorative)`.

## 8. Verify

Read the saved tree back and render it with `brxprod/render-frontend-html`
(Bricks' own render can't show children of nestable elements). It needs an
`elementId` and reads only a post's content area — render header/footer
templates with `bricks/render-elements` (`postId` = the template). For the
whole page, fetch the live URL — and first confirm the page renders with
Bricks at all (AGENTS.md › Known issues › render mode). Check:

- [ ] one `h1`, no skipped heading levels
- [ ] collections are `ul`/`ol` > `li`; pairs are `dl` > `dt`/`dd`; self-contained items are `article`
- [ ] every `section` and `nav` has an accessible name
- [ ] no second `main`; no `header` / `footer` landmark duplicating Bricks' wrappers
- [ ] links navigate, buttons act; link text makes sense alone
- [ ] decorative media/icons `aria-hidden`; informative images have alt text
- [ ] interactive state exposed via `aria-*`; keyboard-operable; focus visible
- [ ] say plainly what you could not check (contrast against images, real
      screen-reader output)
