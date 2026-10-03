---
name: brxprod-notes
description: Read, create, edit, tick off and delete Bricks builder notes on a site running the Bricks Productivity plugin (BRXProd). Use when asked to review notes, add a note, mark notes done, tidy or reorganise notes, or manage note groups — at site, page, element or personal scope. For client feedback (status, assignment, replies, rounds, contributors), use the brxprod-feedback skill.
---

# BRXProd builder notes

Notes are BRXProd's own feature. **Bricks has no equivalent**, so unlike the rest
of this plugin's surface there is nothing here to delegate — none of Bricks' own
abilities apply. (For anything touching pages, elements, classes or design
tokens, use the `brxprod` skill and Bricks' own abilities instead.)

## The four locations

Every note lives at one of four scopes, addressed by a `location` object:

| scope | means | needs |
|---|---|---|
| `site` | the whole site | — |
| `page` | one page | `postId` |
| `element` | one Bricks element on a page | `postId` + `elementId` |
| `user` | a person's private notes | `userId`, or omit for your own |

A missing `postId` or `elementId` is refused with an error naming exactly what
was needed, so you do not have to guess the shape.

## The abilities

| ability | notes |
|---|---|
| `brxprod/list-notes` | read one location, grouped by group id |
| `brxprod/create-note` | `location` + `label`, optional `body`, `groupId`, `done`, `format` |
| `brxprod/update-note` | `noteId` + only the fields to change |
| `brxprod/delete-note` | `noteId`. Permanent |
| `brxprod/list-note-groups` | the site-wide group registry |
| `brxprod/save-note-groups` | replace that registry. Administrators only |

## How to work with them

**Call `list-note-groups` before creating a note** and pick a real `groupId`.
Omit it and the note lands in `g_default`, which is rarely what the user meant
when they said "add this to the content review list".

**`update-note` and `delete-note` take a `noteId` only.** The note's location is
resolved for you — you never restate where it lives, and you cannot reach a note
through this route that you could not reach through its own location.

**Only the fields you send are changed.** Ticking a note off is
`{noteId, done: true}` and nothing else; the label, body, colour and group are
untouched. Do not read a note, modify it, and send the whole thing back — that
is how a note's text gets clobbered by a stale copy.

**A note body containing HTML needs `format: "rich"`.** The default is
`plain`, which is correct for ordinary text and preserves line breaks — but it
escapes markup, so a body written as HTML is shown to the reader as its own
tags. This is not auto-detected, deliberately: a note legitimately reading
"keep this under < 500px" would be misread as markup, and only the caller knows
which was meant.

Rich bodies are still filtered (`wp_kses_post`), so scripts and event handlers
are stripped whatever you send. Ordinary formatting — paragraphs, lists, links,
bold — survives.

**An existing note can be promoted**: `{noteId, format: "rich"}` alone, no body
needed. That is the fix if a note was already added as HTML and is displaying
its tags.

**Prefer marking a note done over deleting it.** Deletion is permanent, and the
body is *not* recoverable from the audit log, which stores only the label. When
a user says "clear these", ask whether they mean done or gone unless it is
already unambiguous.

**`save-note-groups` replaces the whole registry.** Send every group you want to
keep — omitted ones are removed. The two built-in groups are always restored, so
they cannot be lost.

## Client feedback is a note with a workflow — but not this skill's job

Feedback a client leaves on the live site is stored as a note at the same
locations, so `list-notes` shows it — read-only, with its `#number`,
`status`, `assignee` and `visibility`. Those fields are **never** changed
through `update-note`; the `brxprod-feedback` skill and its abilities
(`list-feedback`, `update-feedback-status`, `assign-feedback`,
`comment-feedback` and the rest) own them. If the user is asking about the
feedback queue rather than about a place, switch to that skill.

## Permissions are not bugs

- **Site notes** are readable by editors but writable only by administrators.
  That asymmetry is deliberate.
- **Page and element notes** follow edit rights on that specific post.
- **Another person's notes** need `edit_user` on them.

A refused write here is the permission model working. Say which permission is
missing rather than retrying or routing around it.

## If an ability is missing

Notes abilities are behind their own switch at **Settings → AI Tools → WordPress
Abilities → Notes**, off by default, and Notes is a **Pro** feature — so on a
free licence the switch cannot enable them.

An unregistered ability and a nonexistent one look identical from outside, so do
not conclude the plugin is broken. `brxprod/get-context`
reports the group state: anything under `abilityGroups.unavailable` is switched
off, and it distinguishes "off" from "needs Pro". Tell the user which it is.

## Say what you could not verify

Notes are attached to elements and pages you cannot see. When you have made
changes, say plainly which notes you touched and at which location — an element
id means nothing to a person reading a summary, so name the page and what the
note says.
