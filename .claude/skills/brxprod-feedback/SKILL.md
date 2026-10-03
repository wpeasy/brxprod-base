---
name: brxprod-feedback
description: Run the client-feedback desk on a Bricks site running the Bricks Productivity plugin (BRXProd) — list, read, create, edit and delete client feedback, change its status, assign it, reply (client-visible or internal), share draft pages, approve pages, create and finish review rounds, and manage contributors, share links and invites. Use when asked to triage feedback, summarise what clients have said, reply on the team's behalf, move items along, set up a review round, or invite someone to review. For builder notes, use brxprod-notes.
---

# BRXProd client feedback

Client Feedback is BRXProd's own feature — clients and reviewers annotate the
live site from a widget, the team triages. **Bricks has no equivalent**, so
nothing here delegates to Bricks' abilities. (For pages, elements, classes or
design tokens, use the `brxprod` skill and Bricks' own tooling.)

Every feedback item **is a note** — the same rows the `brxprod-notes` skill
reads at site, page and element scope — with workflow fields on top: a
site-wide `#number`, a `status`, an `assignee`, a `visibility` and a threaded
conversation. Those fields change only through the abilities below, never
through `update-note`.

## The abilities

Every one needs the feedback **manage** capability (Administrator and Editor by
default). A contributor's account is never an agent's identity; a refusal here
is that line, not a bug. Reads keep working on a lapsed licence; writes do not.

**Items**

| ability | notes |
|---|---|
| `brxprod/list-feedback` | filter by `postId`, `status[]`, `assignee`, `roundId`, `open`, `q`; 50 per `page`. Returns `assignees` — the team members an item can go to |
| `brxprod/get-feedback` | one item in full: text, status, where it was pinned, the reporter's browser details, every reply (client-visible and internal), attachments, reactions |
| `brxprod/create-feedback` | `scope` site / page / element (+ `postId`, `elementId`), `body`, optional `label`, `format`, `visibility` |
| `brxprod/update-feedback` | `noteId` + only the fields to change: `label`, `body`, `visibility`, `dueAt` |
| `brxprod/delete-feedback` | permanent, with replies and attachments |
| `brxprod/update-feedback-status` | `new`, `assigned`, `in_progress`, `awaiting_feedback`, `approved`, `closed` |
| `brxprod/assign-feedback` | `userId` from the `assignees` list; `0` unassigns |
| `brxprod/comment-feedback` | `body`; `internal: true` hides it from the client; `awaitClient: true` also moves the item to `awaiting_feedback` |
| `brxprod/delete-feedback-comment` | `noteId` + `commentId` (from `get-feedback`) |

**Pages**

| ability | notes |
|---|---|
| `brxprod/list-feedback-pages` | every page holding feedback: open/total counts, approved, draft shared, its round |
| `brxprod/share-draft-page` | contributors see published pages only; this opens one draft to them (`shared: false` closes it) |
| `brxprod/approve-page` | records an approval (or withdraws one with `approved: false`), logged with who and when |

**Review rounds**

| ability | notes |
|---|---|
| `brxprod/list-feedback-rounds` | rounds with status, pages, per-page checklist state and progress |
| `brxprod/create-feedback-round` | `name`, `postIds`, optional `intro` shown to contributors |
| `brxprod/update-feedback-round` | `name`, `intro`, or `status` (`active` reopens, `finished`, `closed`) |
| `brxprod/finish-feedback-round` | notifies the team; may lock the round's pages for contributors (site setting) |
| `brxprod/delete-feedback-round` | the round only — its feedback is kept |

**People**

| ability | notes |
|---|---|
| `brxprod/list-feedback-contributors` | everyone who can review (joined, last seen, awaiting approval) plus every share link and invite |
| `brxprod/create-feedback-invite` | `kind: "invite"` bound to an `email` (emailed unless `send: false`); `kind: "link"` a site-wide share link, optionally `requiresApproval`, `maxUses`, `expiresDays`. **The URL comes back once** — pass it on |
| `brxprod/revoke-feedback-invite` | stops a link or invite; people already in keep their access |
| `brxprod/manage-feedback-contributor` | `approve` a person waiting on an approval-gated link, `resend` a sign-in link, `remove` their access (their feedback is kept, attributed to a former user) |

## How the workflow reads

- **`new`** just arrived. **`assigned`** someone owns it (set automatically on
  assign). **`in_progress`**. **`awaiting_feedback`** "we've done this, please
  check" — the client can answer `approved` or push it back to `in_progress`.
  **`approved`** is the client's word. **`closed`** is the team's word.
- **`approved` and `closed` tick the item done; anything else un-ticks it.** When
  the team has dealt with something and wants it off the board, use `closed`
  — `approved` is for the client to say. When you have fixed what was asked,
  `awaiting_feedback` with a client-visible reply saying what changed is the
  right move, not `closed`.
- **Assignment is team-only, to team members only.** Clients cannot set it from
  any surface, and the site may auto-assign every new item to a default
  assignee — so an item that arrives already `assigned` is not unusual.
- **Visibility is a wall, not a label.** Contributors' requests are filtered
  server-side; an internal item or reply never reaches them by any route.
  Replies default to client-visible: do not put into a client-visible reply
  anything that was said to you as internal, and do not reveal internal
  replies when summarising a thread for a client.
- **A reply on an internal item is internal** whatever you ask for.

## How to work with them

**Start with `list-feedback`**, usually `open: true`, and read what the client
actually wrote (`get-feedback` for the thread) before acting. A summary that
paraphrases the title alone will be wrong about what they meant.

**Change one thing per call.** Status, assignee, and text are separate abilities
on purpose — a stale copy of an item can never revert a status.

**Mentions and references** are markup, not names: `@[Name](user:12)` mentions
user 12 (they are notified), `#[42](note:NOTE_ID)` links feedback #42. Ids come
from `list-feedback` and its `assignees`; a mention of a contributor inside
internal content is dropped, by design.

**Creating feedback on an element** needs the element's Bricks id and the post
it belongs to — a header element belongs to the header template, not the page
it is seen on. Without a sound id the item lands at page scope.

**Approving a page on the client's behalf** is legitimate when they signed off
elsewhere (email, a call) — say so in your summary; the approval is logged
under your account, not theirs.

**Invites and share links are credentials.** Create one only when asked, hand
the URL to the user rather than posting it anywhere, and prefer a personal
`invite` over a `link` unless the user wants a URL for a group.

**Prefer `closed` over `delete-feedback`.** Deletion takes the thread and the
client's attachments with it and cannot be undone. Ask before deleting
anything a client wrote.

## If an ability is missing

These abilities sit behind their own switch at **Settings → AI Tools →
WordPress Abilities → Client Feedback**, off by default, and Client Feedback is
a **Pro** feature — on a free licence the switch cannot enable them.

An unregistered ability and a nonexistent one look identical from outside, so
do not conclude the plugin is broken. `brxprod/get-context` reports the group
state under `abilityGroups`: `feedback` says whether the switch is off or the
licence is the reason. Tell the user which it is.

## Say what you could not verify

Feedback is pinned to pages and elements you cannot see, written by people you
have not met. When you have acted, say plainly which items you touched — by
number and page, not by internal id — what status they are in now, and what
you told the client, so the user can check the tone before it lands in an
inbox.
