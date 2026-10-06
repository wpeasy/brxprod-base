# PHP standard

**Follow the [WordPress PHP Coding Standards](https://developer.wordpress.org/coding-standards/wordpress-coding-standards/php/)**
and WordPress's [security guidance](https://developer.wordpress.org/apis/security/).
Nothing here replaces them; this page only records where PHP goes and the
rules the site's own `code` instructions add.

For Bricks extension points — custom elements, controls, dynamic data tags,
query hooks, child themes — Bricks' skills are authoritative
(`bricks:bricks-hooks-reference`, `bricks:bricks-custom-elements`,
`bricks:bricks-custom-dynamic-data-providers`, `bricks:bricks-child-theme-patterns`).

## Where it goes

- In a **code manager**, written with `brxprod/create-snippet`
  (`language: "php"`; the opening `<?php` is added if omitted). It lands as a
  **draft** in the BRXProd group.
- **Never activate a PHP snippet, and never say you have.** PHP runs on every
  request and a mistake takes the site down; enabling it is the user's
  decision. Tell them where it is and what it does.
- **Never** in a Bricks Code element. There is no fallback location — if the
  site has no code manager, stop and offer to install one.

## Rules the site adds

- Prefix every global function, class, constant and hook name.
- Escape on output, sanitise on input, and check a capability (and a nonce for
  requests) before acting.
- Never use `eval`, and never fetch code at runtime to execute it.
- Enqueue scripts and styles (`wp_enqueue_script` / `wp_enqueue_style`) — never
  echo `<script>` or `<link>` tags.
- `novamira/execute-php` runs one-off PHP on the site. Use an ability when one
  exists; when none does, execute-php is allowed for reads and writes
  (AGENTS.md › Order of authority › Abilities first). It's not a place for
  code that must keep running — that is a snippet.

## Before saving

- [ ] Passes WordPress Coding Standards (WPCS) conventions
- [ ] Every global name prefixed
- [ ] Output escaped, input sanitised, capability/nonce checked
- [ ] No `eval`, no runtime code fetch, assets enqueued
- [ ] Stored via `brxprod/create-snippet` as a draft — and reported as a draft
