# Navigation standard

Which Bricks navigation element to use, how to build it, and how to make its
mobile menu usable. Read with [css.md](css.md) (class CSS, no button/link CSS)
and [html.md](html.md) (named `nav`, links vs buttons).

**This overrides Bricks' skill default.** `bricks:bricks-mega-menus` defaults new
headers to Nav (Nestable) and keeps WordPress menus for when they are asked for.
In our projects the default is the other way round: **Nav Menu bound to a
WordPress menu**, and Nav (Nestable) only when the nav needs something a
WordPress menu can't hold.

## 1. Choose the element

| | **Nav Menu** (`nav-menu`) | **Nav (Nestable)** (`nav-nested`) |
|---|---|---|
| Items come from | A WordPress menu (Appearance → Menus) | Elements in the header template |
| Who edits links | Any editor, in WordPress | Only in Bricks |
| Sub-menus, current page | Automatic (`aria-current`, `current-menu-*`) | Built by hand (Dropdown elements); current page per link |
| Mega menus | Yes — a Bricks section template attached to a menu item | Yes — Dropdown with `megaMenu: true`, content built in place |
| Mobile menu | Bricks drawer + animated burger → X | Bricks full-screen panel; close toggle must be configured |

### Use Nav Menu (default) when

- the nav is **links an editor should be able to change** — main menus, simple
  dropdowns, footer menus that change with the site;
- a mega panel is needed but the **items are still plain menu links**: keep the
  WordPress menu and attach the panel as a Bricks section template to the item.

### Use Nav (Nestable) when the nav is designed UI, not a list of links

- **Mixed content in the bar** — a CTA button, search, phone number, language
  switcher, account/cart icons *inside* the nav (same list, same keyboard order,
  same mobile panel).
- **The mobile drawer carries more than links** — CTA, contact details, social
  links, a featured item.
- **Content-heavy dropdowns** — panels with cards, images, prices, buttons,
  especially when **data-driven** (a query loop of featured posts/CPT items).
- **Bespoke dropdown behaviour** — click-to-open, slide-in multilevel, accordion
  sub-menus.
- **Fixed, structural links nobody edits in WordPress** — legal footer links,
  one-page jump links (`#section`), step indicators.
- **Labels from data** — e.g. "Trips (6)", via dynamic data on the link text.

When you choose Nestable, **tell the user** its links are edited in Bricks, not
in Appearance → Menus.

**Rule of thumb:** links an editor manages → Nav Menu (plus a mega template if
needed). Navigation as designed UI with mixed content, rich panels or data →
Nav (Nestable).

Elements next to the nav that aren't menu items (a "Plan my trip" button beside
the menu) stay **outside** the nav element in both cases — they don't need
Nestable.

## 2. Build it

### Nav Menu

1. `bricks/list-nav-menus` → reuse an existing menu if it fits; otherwise create
   one with `bricks/save-nav-menu`. **Link pages as page objects**, never typed
   URLs, so renamed slugs keep working. Read the tree back with
   `bricks/get-nav-menu`.
2. Assign a theme location only if the theme/site uses one; the Nav Menu
   element selects the menu directly (`menu` setting = menu ID).
3. Add the `nav-menu` element in the header template (load
   `bricks:bricks-headers-footers` first). Give it the header block's element
   class (e.g. `site-header__nav`) and an accessible name.
4. Mega panel (optional): build a **section** template and attach it to the
   menu item per `bricks:bricks-mega-menus` › *Reusing an existing WordPress
   menu*. Confirm with the user before attaching it.

### Nav (Nestable)

1. Read `nestableChildren` from `bricks/get-element-schema` (`nav-nested`) and
   keep both required wrappers: the `ul` block with `brx-nav-nested-items`, and
   the close toggle (`brx-toggle-div`) inside it, plus the open toggle as the
   nav's last child.
2. Set `ariaLabel` on the nav ("Main", "Footer"…) — every `nav` on a page needs
   a distinct name.
3. Links are Text Link elements with page links (`link.type: internal`), not
   typed URLs. Dropdowns per `bricks:bricks-mega-menus`.
4. Non-link items (buttons, search) inside the list follow the normal rules —
   a Button element styled only with its own controls.

## 3. Mobile menu — always fix it

Bricks' mobile defaults are a bare scaffold: no edge padding, generic colours,
and (Nestable) a close toggle that draws burger bars at the bottom of the list.
Every nav we ship gets:

- [ ] a visible **X close control at the top right**, in line with the open toggle;
- [ ] **accessible names** on both toggles ("Open menu" / "Close menu");
- [ ] **edge padding** (`--brxp-page-gutter` inline, section-scale block padding),
      an item **gap**, and a readable **font size**;
- [ ] **background and text colour** from the design system — a dark brand shade
      plus its `--brxp-a11y-*-text` token;
- [ ] verified **at phone width**: opens, closes from the X, focus order is
      sensible, Escape closes, no horizontal scroll.

**How:** in the header block's global class CSS (Settings variables, wrapped in
`@supports`, per [css.md](css.md)), targeting the **open state** and Bricks'
markup. Never style the toggle button itself — position its wrapper; use the
toggle's own `icon` / `ariaLabel` settings for content.

### Nav (Nestable) — tested

Close toggle: set `icon` (e.g. `{"library":"themify","icon":"ti-close"}`) and
`ariaLabel: "Close menu"`; open toggle `ariaLabel: "Open menu"`.

```css
.site-header__nav{
  &.brx-open .site-header__menu{            /* .brx-nav-nested-items */
    justify-content: center;
    align-items: flex-start;
    gap: var(--_site-header__menu-gap--open);
    padding-block: var(--_site-header__menu-padding-block--open);
    padding-inline: var(--_site-header__menu-padding-inline--open);
    background: var(--_site-header__menu-background--open);
    color: var(--_site-header__menu-color--open);
    font-size: var(--_site-header__menu-font-size--open);
  }

  /* Bricks wraps the close toggle in an li — pin the wrapper, not the button */
  &.brx-open .site-header__menu > li:has(> .brx-toggle-div){
    position: absolute;
    inset-block-start: var(--_site-header-padding-block);
    inset-inline-end: var(--_site-header__menu-padding-inline--open);
    font-size: var(--_site-header__close-font-size);
    line-height: 1;
  }
}
```

Specificity: Bricks' open rule is `.brxe-nav-nested.brx-open .brx-nav-nested-items`
(0,3,0); `.nav-class.brx-open .menu-class` matches it and wins on order — don't
drop a class.

### Nav Menu — tested

Element settings (content, not styling): `menu` (WordPress menu ID),
`ariaLabel` ("Main"), `mobileMenuAriaLabel` ("Main (mobile)" — Bricks renders
the desktop and mobile menus as **two** `nav` landmarks, so both need distinct
names), `mobileMenuToggleAriaLabel` ("Open menu"; Bricks switches it to "Close
mobile menu" when open), `mobileMenu` (breakpoint, default
`mobile_landscape`), `mobileMenuPosition: "right"`.

Bricks markup:

| Part | Selector |
|---|---|
| Desktop list | `.bricks-nav-menu` (`> li > a`, `.current-menu-item`, `[aria-current="page"]`) |
| Open state | `.brxe-nav-menu.show-mobile-menu` |
| Drawer | `.bricks-mobile-menu-wrapper` (fixed, slides from `left`/`right`) |
| Drawer background | painted on `.bricks-mobile-menu-wrapper::before` (default `#23282d`) — set it there |
| Drawer list | `.bricks-mobile-menu` |
| Toggle | `.bricks-mobile-menu-toggle` — the **same button** animates burger → X and becomes `position: fixed` where it was |
| Overlay | `.bricks-mobile-menu-overlay` |

**The X lands wherever the burger was.** To get it top right inside the
drawer: open the drawer from the **right** and make the nav the **last item**
in the header row on phones. Do that with `order` on the nav element (layout on
our element — never position the toggle button), so a CTA button next to the
nav moves to its left.

```css
:has(> .site-header__inner){ container-type: inline-size; }

.site-header__brand{
  /* … */
  @container (inline-size <= 767px){ margin-inline-end: auto; }
}

.site-header__nav{                          /* the Nav Menu element */
  margin-inline-start: auto;

  .bricks-nav-menu{
    gap: var(--_site-header__nav-gap);
    font-size: var(--_site-header__nav-font-size);
  }

  .bricks-mobile-menu-wrapper{
    justify-content: center;
    width: var(--_site-header__drawer-width);          /* min(100vw, 36rem) */
    padding-block: var(--_site-header__drawer-padding-block);
    padding-inline: var(--_site-header__drawer-padding-inline);
    color: var(--_site-header__drawer-color);          /* a11y token */
  }

  .bricks-mobile-menu-wrapper::before{
    background: var(--_site-header__drawer-background); /* brand dark shade */
  }

  .bricks-mobile-menu{
    display: flex;
    flex-direction: column;
    gap: var(--_site-header__drawer-gap);
    font-size: var(--_site-header__drawer-font-size);
  }

  .bricks-mobile-menu-overlay{
    background: var(--_site-header__overlay-background);
  }

  /* Phones: nav (burger → X) last, so the X sits top right */
  @container (inline-size <= 767px){
    order: 1;
    margin-inline-start: 0;
  }
}
```

Gotchas found on the first build:

- **rem is 10px on Bricks Wireframes** (62.5% root) — Bricks' default drawer is
  300px; a "22rem" width is only 220px and clips long items. Size the drawer
  with `min(100vw, 36rem)` or tokens, and check the longest item fits.
- The container query width (`767px`) should match the element's `mobileMenu`
  breakpoint so the reorder and the burger switch together.
- Specificity: Bricks' drawer rules are `.brxe-nav-menu .bricks-mobile-menu-wrapper`
  (0,2,0) and `…::before`; `.site-header__nav .bricks-mobile-menu-wrapper` ties
  and wins on order.
- Bricks handles Escape, focus and `aria-expanded`; current page is marked with
  `aria-current="page"` in both menus.
