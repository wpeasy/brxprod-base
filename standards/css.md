# CSS standard

How we structure classes, labels and CSS on a BRXProd site. Applies to every
framework: token names in examples are **Core Framework** (the reference
example was built on one) — on any site, resolve each token through the
*Concept map* in `DESIGN_SYSTEM.md` and never copy a name the site doesn't have.

Bricks' own skills and abilities decide *how* CSS and classes are written to
the site; the site's live `brxprod/get-design-instructions` outrank this file
where they conflict, **except where this file says it overrides them** (label
case).

Reference example: [examples/test-card.bricks.json](examples/test-card.bricks.json)
(Bricks copied-elements JSON — a section holding a card component with a
modifier).

**Never produce this through Bricks' copy/paste or HTML/CSS import** — the
converter writes CSS into element settings instead of class CSS. Build the
element tree with Bricks' element abilities and write the CSS into the block's
global class (AGENTS.md › Building content).

## 1. BEM everywhere

- Every class is BEM: `block`, `block__element`, `block--modifier`. Lowercase,
  hyphenated words.
- Element classes are flat — `test-card__media`, never
  `test-card__content__media`. An element belongs to its block, not to its
  parent element.
- Style a child through a **BEM element class**, not a tag selector, whenever
  the child is an element we place. Tag paths (`> ul > li`) are for markup we
  don't control (rich text, WordPress output).
- BRXProd utility classes compose alongside BEM classes on the same element —
  e.g. `test-card__media` + `brxp-has-bg-media`, `test-card__image` +
  `brxp-has-bg-media__media`. Never restyle a `brxp-*` class.

### Nested blocks

A block inside another block (a card inside a section) is a **new block**, not
an element of the outer one: `test-card`, not `main-section__test-card`.
`"_abpBemMeta": {"bemAction": "skip"}` on the nested block's root element makes
BRXProd's BEM tool keep it atomic instead of renaming it into the parent — but
Bricks 2.4.2 rejects that setting on ability writes (AGENTS.md › Known issues),
so leave it out, note the omission, and set it in the builder if the BEM tool
will be run on the page.

### Atomic components are generic

Reusable building blocks — cards, button groups, lists, badges, media
objects — are named for their **structure**, never their content:

- **One generic block per structure:** `card`, `button-group`, `media-object`
  — never `product-card`, `feature-card`, `person-card` when they share a
  structure. What a card *shows* is content, not a new component.
- **Visual differences → a modifier** (Settings-only, §5): `card--feature`,
  `card--compact`, `button-group--stacked`.
- **Structural differences → a version:** when the element tree genuinely
  differs (different elements, order that can't be a variable), create a new
  versioned block — the first is `card`, the next `card-v2`, then `card-v3` —
  each with its own elements (`card-v2__body`). Never rename an existing block.
- **Purpose goes in the label comment**, not the class: label `Card (Product)`,
  `Card [Team member]` (bracket comments are ignored for BEM matching, §2).
- **Check before creating:** look for an existing generic block in
  `DESIGN_SYSTEM.md` › Global classes (or `bricks/list-global-classes`) and
  reuse it — add a modifier or a version only if it really doesn't fit.

## 2. Labels

**Every element's label matches its BEM name, in Title Case** — this overrides
the sentence-case rule in the site's default instructions.

| Class | Label |
|---|---|
| `main-section` | Main Section |
| `test-card` | Test Card |
| `test-card__content` | Content |
| `test-card__media` | Media |

- Block → the block name; element → the part after `__`; modifiers never
  appear.
- Text in brackets is a comment and ignored when matching: `Title (H1)`,
  `Media [decorative]`, `Price {loop}`.
- Bricks' default label is fine when it already matches (an element
  `__heading` on a Heading element is labelled "Heading" by default).
- An element with no BEM class still gets a meaningful label (role: Paragraph,
  Item, Link, Icon) — never a mismatched default.

## 3. Where CSS lives

- **All of a component's CSS goes in the block's global class.** Element
  classes (`test-card__content` …) carry no CSS of their own — their rules are
  written in the block class's CSS.
- **Wrappers are Div elements, never Block.** Block comes with default CSS
  (flex, width) and media queries that would have to be found and overridden;
  a Div has none, so the class CSS is the whole story.
- Global-class CSS uses the **literal class selector** (`.test-card`).
  `%root%` is only for element-level (ID) CSS, such as an asymmetric rail span.
- Simple Bricks UI settings are fine for what they are designed for — a
  heading `tag`, an image `size`. Visual styling (spacing, colour, type,
  layout) is CSS.
- **Text colour is always the a11y token for the background it sits on:**
  `--brxp-a11y-{colour}[-{l|d}-N]-text` — e.g. `--brxp-a11y-surface-d-7-text`
  on the page, `--brxp-a11y-surface-d-6-text` on a card. That covers body,
  headings, muted text, labels and prices. Brand colours (primary, secondary,
  surface shades) are for backgrounds, borders and decoration, never text; no
  hand-picked "muted" shade — use size and weight for hierarchy.

### Typography

- **Theme style first.** Body and heading typography — font family, sizes,
  weights, line height, per-level `h1`–`h6` — is set in the active theme
  style's Typography settings (`bricks/update-theme-style`). Use those defaults
  wherever they fit; change a theme setting only when the design needs it
  site-wide, and report which keys changed.
- **Variations go in CSS.** When an element needs a different size, style or
  weight from the theme default (a kicker, a large lead paragraph, a card
  title), set `font-size` / `font-weight` / `font-style` (and `line-height`,
  `letter-spacing`, `text-transform` if needed) in the block's class CSS, using
  the framework's type tokens via the Settings block.
- **Never set `font-family` in CSS** — not in a class, `%root%`, or a modifier.
  Families come only from the theme style, so they stay consistent site-wide.
  If the design needs another family, it's a theme-style change: ask first.

### Buttons, links and element defaults

- **Never write CSS that targets a button or a link** — no `.x__button {…}`,
  `.x__link {…}`, nor hover, colour, padding or radius rules for them.
- A button is styled only with the Button element's own controls: `size`
  (sm/md/lg/xl), `style` (primary/secondary/…), `circle`, `outline`. Anything
  that looks like a button is a Button element, never a styled Text Link.
- Layout around a button (alignment, spacing, pushing it to the bottom of a
  card) goes in the parent's CSS — `align-items` / `align-self` on the card and
  its other elements — not on the button.
- Links take their look from the theme style's `links` defaults. Typography
  that only needs to reach a link (a wordmark) goes on a wrapping element (`p`
  containing the `a`); a nav's font size can go on its list.
- Element defaults — button colours in every state, sizes, borders, radius;
  link colours; site background; body and heading text colour — live in the
  active theme style, not component CSS (AGENTS.md › Building content).

### Wrap everything in `@supports (display: grid)`

**Every `_cssCustom` written through an ability — global class or element
(`%root%`) CSS — is wrapped, in full, in one `@supports (display: grid)`
block.** Bricks 2.4.2's normaliser leaves an at-rule's contents alone, so this
stops it moving root declarations into style controls and mangling nesting
(AGENTS.md › Known issues). Every browser supports grid, so the wrapper never
changes what renders.

```css
@supports (display: grid) {
/* Settings */
.test-card{
  --_test-card-background: var(--test-card-background, var(--light));
}

.test-card{
  background: var(--_test-card-background);
  &:hover{ /* … */ }
}
}
```

- One wrapper around **all** the code — the Settings block, the rules, nested
  states and `@container` queries alike. Nothing outside it.
- The examples in this file omit the wrapper for readability; add it when you
  save.
- Still **read the CSS back** after saving and compare it with what you sent.

## 4. The Settings block

Any value a modifier (or a caller) may need to change is a variable, declared
once at the top of the block class:

```css
/* Settings */
.test-card{
  --_test-card__content-padding: var(--test-card__content-padding, var(--space-s));
  --_test-card__media-max-width: var(--test-card__media-max-width, 200px);
  --_test-card-background: var(--test-card-background, var(--light));
  --_test-card-border-radius: var(--test-card-border-radius, var(--radius-m));
  --_test-card-border: var(--test-card-border, none);
}
```

- **One Settings block per block class**, first in the CSS, under a
  `/* Settings */` comment, containing only variable declarations.
- Each is `--_private: var(--public, default)`. The public name is the private
  name without the leading underscore.
- **Default** = a design token where one exists (resolved via the concept map),
  otherwise a literal (`200px`, `none`). A raw colour or spacing value where a
  token exists is a token that wasn't looked up. **Text colour variables default
  to the a11y token** for the block's background
  (`--_card-color: var(--card-color, var(--brxp-a11y-surface-d-6-text))`).
- **Rules read only the private `--_` variables**; the public names are the
  override handles.
- Values nothing will ever override can be written directly (`main-section`
  sets `background` with no Settings block). If in doubt, variablise.
- The builder's CSS panel can do this for you (right-click → *Variablize*);
  when writing through abilities, produce the same shape by hand.

### Variable names

`--_` + block + **path to the property** + `-` + property.

| Declaration | Variable |
|---|---|
| `.test-card { background }` | `--_test-card-background` |
| `.test-card__content { padding }` | `--_test-card__content-padding` |
| `.test-card__media { max-width }` | `--_test-card__media-max-width` |
| `.test-card ul li { padding }` (markup we don't control) | `--_test-card-ul-li-padding` |
| `.test-card:hover { box-shadow }` | `--_test-card-box-shadow--hover` |

BEM elements keep their `__`; tag/selector steps are joined with `-`; a state
appends `--{state}`.

## 5. Modifiers are Settings-only

A modifier class sets **public** variables and nothing else, and is applied
together with the block class:

```css
/* Settings */
.test-card--style2{
  --test-card-box-shadow: var(--shadow-l);
  --test-card__media-max-width: 250px;
  --test-card-border: 2px solid var(--base-l-2);
}
```

If a variant needs a structural change (media on the right, column layout),
expose it as a variable in the block's Settings
(`--_test-card-flex-direction`) and set that in the modifier — modifiers never
carry rules.

## 6. Nesting

Inside a block's rule, nest only:

- states and pseudo-elements: `&:hover`, `&::before`;
- `@container` queries;
- contextual overrides of the block's own elements (inside a query).

Element rules are **flat top-level selectors** (`.test-card__content { … }`),
never `&__content`, so every element stays at single-class specificity.

## 7. Responsive: container queries only

- **Never `@media`. Never Bricks' breakpoints.**
- The block makes its parent the query container, in its own CSS:

  ```css
  :has(> .test-card) {
    container-type: inline-size;
  }
  ```

- Queries are nested in the rule they change, as ranges with a **literal px**
  width measured against that parent's inline size:

  ```css
  .test-card {
    display: flex;
    flex-direction: row;

    @container (inline-size <= 562px) {
      flex-direction: column;

      .test-card__media {
        flex: auto;
        max-width: 100%;
      }
    }
  }
  ```

- Several queries: **widest first, narrowest last** — they are ranges, and the
  later match wins.
- A narrower query **restates** every property it changes; omitting one doesn't
  reset it.

## 8. Layout rails

`brxp-rails` places **its direct children**, whatever they are, on the content
rail; use the `brxp-rail-*` classes on those children for symmetric spans and
ID-level `%root%` CSS for asymmetric ones (see AGENTS.md › Rails). Put
`brxp-rails` on whichever element's children should sit on the rails.

## 9. BRXProd CSS Patterns

BRXProd's CSS panel ships **CSS Patterns** — typeahead templates for recurring
rules. When one fits, use it verbatim rather than writing your own version.

### Sticky header (`sticky-header`)

A Bricks sticky header (`#brx-header.brx-sticky`) is `position: fixed`, so the
first section slides under it. The pattern pads the first section by the
section padding plus the measured header height.

**Where:** whenever a header template is set to sticky, put the pattern in the
custom CSS of that template's **top element** — it travels with the header and
disappears with it. Not in the theme style, a page, or a section.

```css
#brx-header.brx-sticky ~ #brx-content > section:first-child {
  padding-block-start: calc(
    var(--brxw-section-space-vertical, var(--section-padding-block, 0px)) +
    var(--brxp-header-height, 130px)
  );
}
```

- Works unchanged on Bricks Wireframes and Core Framework (the fallback chain
  picks whichever section-padding variable exists). On another framework,
  replace both with its section padding-block token from the concept map.
- **Requires** BRXProd's "Header & Footer Heights → CSS Variables" snippet
  (`header-height`), which sets `--brxp-header-height` on `<html>`. The init
  status check reports whether it is installed and active.
- Bricks' `.on-scroll` sticky variant is `position: sticky` (in flow) and
  needs no offset.

## 10. Images

- Content images rely on the media library's alt text (Bricks falls back to
  the attachment's alt when `altText` is empty) — make sure the attachment has
  one.
- Decorative images — `brxp-has-bg-media__media`, pattern art — are hidden from
  assistive technology (`aria-hidden="true"`); an empty `altText` is not enough.

## Checklist before saving

- [ ] Every class BEM; nested blocks marked `bemAction: skip` in the builder, or the omission reported
- [ ] Components generic (no content-named blocks); reused existing block, modifier for visuals, `-v2` only for a different structure
- [ ] Every label = Title Case BEM segment (bracket comments allowed)
- [ ] Wrappers are Div elements — no Block elements
- [ ] All component CSS in the block class; element classes empty
- [ ] One `/* Settings */` block; rules use only `--_` variables; defaults are tokens
- [ ] Modifiers only set public variables
- [ ] No `@media`; containment declared via `:has(> .block)`; queries widest → narrowest
- [ ] Every token name exists on this site (`DESIGN_SYSTEM.md`)
- [ ] Every text colour is the `--brxp-a11y-*-text` token for its background; brand colours only on backgrounds, borders, decoration
- [ ] Typography from the theme style; only size / weight / style variations in CSS; no `font-family` anywhere in CSS
- [ ] No CSS targets a button or a link; buttons use only Size / Style / Circle / Outline
- [ ] Element-default changes made in the theme style, only where the design needs them, and each changed key reported
- [ ] All CSS wrapped in one `@supports (display: grid) { … }` block
- [ ] After saving: `_cssCustom` read back matches what was sent, no style-control keys added (Bricks 2.4.2 normaliser bug — AGENTS.md › Known issues)
