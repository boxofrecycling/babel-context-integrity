# Visual identity

Restrained developer tool. The design brief was to spend as little time on this
as possible while still looking deliberate.

## The mark

Two nodes and a dotted edge:

```
●┈┈┈┈┈○
```

Left node filled — the predecessor, complete. Dotted edge — the handoff, the
lossy part. Right node hollow, outlined — the successor, not yet filled in.

Inline SVG, 32×18, `currentColor`, no fill colours of its own so it inherits
the page's theme:

```html
<svg width="30" height="18" viewBox="0 0 32 18" aria-hidden="true">
  <circle cx="5" cy="9" r="3.6" fill="currentColor" opacity=".55"/>
  <path d="M10 9h11" stroke="currentColor" stroke-width="1.8"
        stroke-dasharray="2.4 2.4" opacity=".4"/>
  <circle cx="26" cy="9" r="3.6" fill="none" stroke="currentColor"
          stroke-width="1.8" opacity=".55"/>
</svg>
```

The favicon is the same shape at 32×32 as a data URI, so there is no image file
to keep in sync.

## The wordmark

`BABEL CONTEXT INTEGRITY` — monospace, uppercase, `.13em` letter-spacing, muted
colour, sitting next to the mark at small size. Never large, never a headline.
The headline is the sentence, not the name.

## The real identity is the CLI output

The dotted leader is the thing people will recognise:

```
structure ............. verified
retained constraints .. FAILED
external truth ........ not established
```

It is already in the tool, it is the actual product surface, and it survives
being pasted into a terminal, a GitHub comment, or a tweet. Every piece of
marketing material leads with it rather than with a logo.

## Colour

There is no brand colour. The page uses near-black on near-white, inverted for
dark mode, and borrows exactly three semantic colours from terminal
convention:

| Role | Light | Dark |
|---|---|---|
| verified | `#1a7f4b` | `#4ec27f` |
| failed | `#b4331f` | `#ef6d55` |
| not established | `#96690d` | `#d8a93c` |

Amber for `not established` is the one deliberate choice: it is neither pass
nor fail, and it should not read as either.

## Type

System sans for prose, `ui-monospace` for anything that is or resembles a
command. No web fonts — the page has no external requests at all, which is the
same property the tool claims.

## Things to avoid

The brief said it, and it is worth writing down: no brain iconography, no robot
head, no glowing neural mesh, no purple SaaS gradient, no badge wall. This is a
tool that prints text in a terminal and it should look like one.

## Assets

There are none. The mark is nine lines of inline SVG in
[`index.html`](index.html) and the favicon is a data URI in the same file. If a
raster version is ever needed, render the SVG rather than maintaining a second
copy.
