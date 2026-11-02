# Project brief — _TODO_ site name

> What the agent writes from. Anything still `_TODO_` is unknown: the agent asks
> rather than inventing content, contact details, prices or claims. Fill it in
> yourself, or answer the questions in chat and let the agent write the answers
> in. Delete sections that don't apply.
>
> If this is a test/demo site with invented content, say so here — the agent
> then marks fictional details as fictional and uses reserved values (e.g.
> example.com e-mail, ACMA/Ofcom/NANP fictional phone ranges).

## Business

| | |
|---|---|
| Name | _TODO_ |
| Tagline | _TODO_ |
| What it does | _TODO_ — one or two sentences |
| Location / service area | _TODO_ |
| Founded / key facts | _TODO_ |
| Currency, pricing basis | _TODO_ (e.g. AUD, per person, inc. GST) |

### Products / services

_TODO_ — a table of what is sold or offered, with the facts pages will need
(name, price, duration, key features). If this data will live in a custom post
type, say so: the agent builds it as Meta Box data + Bricks query loops.

### People

_TODO_ — names and roles the site may mention (or "none").

## Audience

- **Who:** _TODO_
- **Want:** _TODO_
- **Worry about:** _TODO_
- **Decide by:** _TODO_

## Voice

- _TODO_ — tone in three or four words (e.g. warm, direct, expert)
- _TODO_ — spelling (e.g. Australian English) and person ("you", "we")
- Avoid: _TODO_ — words, clichés or tones that are off-brand

## Pages

| Page | Purpose | Main sections |
|---|---|---|
| Home | _TODO_ | _TODO_ |
| _TODO_ | _TODO_ | _TODO_ |

Header and footer are Bricks templates; navigation follows
`standards/navigation.md` (a WordPress menu by default).

## Calls to action & forms

- **Primary CTA:** _TODO_ (label → destination)
- **Secondary CTA:** _TODO_
- **Forms:** _TODO_ — fields, and where submissions are e-mailed

## Contact details

| | |
|---|---|
| Email | _TODO_ |
| Phone | _TODO_ |
| Address | _TODO_ |
| Hours | _TODO_ |
| Social | _TODO_ |

## Proof

_TODO_ — testimonials, reviews, awards, logos, stats (with permission to
publish). Never invented for a real business.

## Colour scheme

**Theme:** _TODO_ — **Light** (light page, dark text) or **Dark** (dark page,
light text). `init-brxprod` asks whether to set this now or here in the brief;
it decides the Surfaces and the page colours, which are set after Primary and
Secondary below. If you fill this section in later, re-run `/init-brxprod` (or
ask the agent to apply the brief's colours) to write them to the site.

_TODO_ — the root colours, or "agent to propose". Per AGENTS.md › Changing
colours: only root values are set (variants are generated); only the neutral
`base` / `surface` sits at 50% HSL lightness; text uses the
`--brxp-a11y-*-text` tokens.

| Role | Name | Value | Use |
|---|---|---|---|
| Primary | _TODO_ | _TODO_ | _TODO_ |
| Secondary | _TODO_ | _TODO_ | _TODO_ |
| Surface / base | _TODO_ | _TODO_ | _TODO_ |
| Extra `brxp-…` (if any) | _TODO_ | _TODO_ | _TODO_ |

More spec colours than roles? Map them per the `design-system` skill ›
*Mapping a brief's colours to the roles*.

## Typography

- **Headings:** _TODO_ (or "agent to propose")
- **Body:** _TODO_

## Visual language

The shapes and surfaces that make the site look like the design. Fill from the
mood board or screenshots, not from guesses — `init-brxprod` and the agent read
this before building (AGENTS.md › Design fidelity).

- **Button shape:** _TODO_ — pill (fully rounded), rounded (say how much) or
  square. Set once in the theme style, never per button.
- **Card / panel / image corners:** _TODO_ — none, small, large or fully rounded.
- **Borders and shadows:** _TODO_ — e.g. hairline borders, no shadows.
- **Backgrounds:** _TODO_ — flat colour, full-bleed photo with an overlay, patterns.
- **Image treatment:** _TODO_ — rounded, cropped tight, black and white, duotone.
- **Distinctive details:** _TODO_ — anything a reader of the mood board would
  call a signature (a line motif, tag chips, a glow around the main button).

## Motion

_TODO_ — **GSAP** or **Bricks Interactions** (asked by `init-brxprod`; see
AGENTS.md › Motion). Note any effects the design calls for.

## Imagery

- **Style:** _TODO_
- **Source:** _TODO_ — client photos, stock (which library), or placeholders.
  The agent asks before downloading each batch and records credits.

## Design inspiration

_TODO_ — screenshots or URLs, and whether they are inspiration only or a
design to match.

## Content sources

_TODO_ — existing site, documents, or "write from this brief".
