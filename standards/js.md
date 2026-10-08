# JavaScript standard

Plain, modern browser JavaScript. Where the code goes (code manager, never a
Bricks Code element) is in AGENTS.md › JavaScript & PHP.

## 1. Shape

Every script is wrapped in an **IIFE**. Nothing leaks to the global scope.

```js
(function () {
  document.addEventListener('bricks/ajax/end', function (event) {
    console.log(event)
  });
})();
```

- **ES6+**: `const` / `let` (never `var`), arrow functions, template literals,
  destructuring, optional chaining, `for…of`, modules-free (it runs as a
  classic script in the footer).
- **No jQuery**, no libraries unless the brief requires one. For GSAP, BRXProd
  bundles a `gsap-loader` snippet (`brxprod/list-snippets`) — check it before
  adding any other loader, and never inject a `<script>` tag from JS.
- If something genuinely must be shared, expose **one** namespaced object —
  never loose globals.

## 2. Browser APIs first

Reach for the platform before writing logic by hand:

| Need | Use |
|---|---|
| element enters/leaves the viewport | `IntersectionObserver` |
| element changes size | `ResizeObserver` |
| DOM nodes added/removed | `MutationObserver` (or a Bricks event, below) |
| user prefers less motion | `matchMedia('(prefers-reduced-motion: reduce)')` |
| many similar elements | **one delegated listener** + `event.target.closest('.block__element')` |
| remove listeners / cancel work | `AbortController` (`{ signal }`) |
| next paint | `requestAnimationFrame` |
| HTTP | `fetch` |
| toggling UI state | `aria-*` attributes / `hidden` / `<dialog>` / `popover` |

## 3. Events, not timers

**Never use `setTimeout` / `setInterval` to wait for something to happen.**
Find the event that says it has happened:

- page: `DOMContentLoaded`, `load`, `pageshow`;
- CSS: `transitionend`, `animationend`;
- scrolling: `scrollend`;
- Bricks (below).

Timers are only for behaviour that is genuinely about time — a debounce, an
auto-advance interval the design calls for.

### Bricks frontend events

Dispatched on `document` (verified in Bricks 2.4.2's frontend scripts). Listen
for these instead of polling for content Bricks loads:

| Event | Fires when |
|---|---|
| `bricks/ajax/start` · `bricks/ajax/end` | any Bricks AJAX request starts / ends |
| `bricks/ajax/query_result/displayed` | a query loop's new results are in the DOM (filters, load more, infinite scroll) |
| `bricks/ajax/query_result/completed` | a query loop request completes |
| `bricks/ajax/nodes_added` | Bricks has inserted new nodes |
| `bricks/ajax/pagination/completed` · `bricks/ajax/load_page/completed` | AJAX pagination / page load done |
| `bricks/filter/submit/start` · `bricks/filter/submit/end` | a query-filter submission |
| `bricks/ajax/popup/start` · `…/popup/loaded` · `…/popup/end` | an AJAX popup's content loading |
| `bricks/popup/open` · `bricks/popup/close` | a popup opens / closes |
| `bricks/accordion/open` · `bricks/accordion/close` | an accordion item toggles |
| `bricks/tabs/changed` | the active tab changes |
| `bricks/megamenu/repositioned` | a mega menu is repositioned |
| `bricks/form/submit` | a Bricks form is submitted |
| `bricks/woocommerce/cart-contents-changed` · `…/checkout-step-changed` · `…/fragments/refreshed` | WooCommerce cart / checkout updates |

`bricks/animation/end/…` and `bricks/map/markers/rendered/…` carry a suffix
per instance — inspect the event in the console before relying on the name.

## 4. Content that arrives later

Query loops, filters, pagination and popups replace DOM after load, so:

- prefer **event delegation** on a stable ancestor — it covers new nodes for
  free;
- otherwise make init **idempotent** and re-run it on the Bricks event:

```js
(function () {
  const init = (root = document) => {
    for (const card of root.querySelectorAll('.test-card:not([data-ready])')) {
      card.dataset.ready = '';
      // …set up this card
    }
  };

  document.addEventListener('DOMContentLoaded', () => init());
  document.addEventListener('bricks/ajax/query_result/displayed', () => init());
})();
```

## 5. Talking to CSS

- Select by the **BEM classes** of the CSS standard (`.test-card__media`).
- JS changes **state**, CSS decides **looks**: set attributes (`aria-expanded`,
  `data-state`, `hidden`) or a **custom property** the block's Settings already
  reads (`el.style.setProperty('--test-card__media-max-width', …)`). Never set
  individual style properties (`el.style.width = …`).
- Respect `prefers-reduced-motion` for anything that moves.

## 6. Before saving

- [ ] Wrapped in an IIFE; no globals (or one namespaced object)
- [ ] ES6+; no `var`, no jQuery
- [ ] No timer waits — an event or observer is used instead
- [ ] Works for AJAX-loaded content (delegation, or idempotent init on a Bricks event)
- [ ] State via attributes / custom properties, not inline styles
- [ ] Read `brxprod/get-site-js` first; stored with `brxprod/create-snippet`, activated if the page needs it, page checked for console errors
