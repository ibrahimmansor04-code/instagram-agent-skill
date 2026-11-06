---
name: ig-motion
description: >-
  Design a faceless animated Reel built from bilingual Arabic and English text
  over illustrated scenes - two house styles (Lantern, the storyteller, and
  Thread, the kinetic-type one), a timed storyboard, and a playable HTML preview.
  Use when the user wants an animated text Reel, a reminder or story told in
  motion, a hadith or dua narrated over art, "design like these", Arabic and
  English subtitles, or a Reel with no face and no talking head.
---

# ig-motion

Turns a short piece of writing into a faceless animated Reel: the words arrive
one at a time over a flat illustrated scene, one word per line is lit up, and
the last frame is a single big idea on its own card. Two house styles, both
measured from reference reels, plus the tools to time it and preview it.

The art is separate from the layout. This skill gives you the layout system,
the colour, the type, the timing and the scene plan. The illustrations are
drawn or generated on their own and dropped in (see Scenes). Do not copy
someone else's characters, logo, channel mark or script. Take the system, make
the art original.

## Before you write

1. Read `~/.claude/instagram/voice.md` if it exists. Motion Reels have no
   on-camera voice, but the writing still has one.
2. Get the **text from the user**. If it is a hadith, an ayah, a dua or a
   saying, the user supplies the wording and the source. Do not write one from
   memory, do not paraphrase one and present it as a quotation, do not invent a
   grading or a reference. A source line on screen is a claim. If the user has
   not given one, leave the source line off and say so.
3. Ask for the **handle** to show on screen, and the **brand name** if they
   have one. If neither is given the player shows `@yourhandle`. Flag it.
4. Ask how it will be voiced. A recorded voiceover, a recitation they have the
   right to use, or text only. Do not synthesise a voice reciting the Quran or
   a hadith. Timings here are for pacing a human recording.

## Pick the style

| | **Lantern** | **Thread** |
| --- | --- | --- |
| Feel | warm, quiet, illustrated, a story being told | hard, sparse, one question at a time |
| Lead language | Arabic on top, English under it | English on top, Arabic under it |
| Reveal | karaoke: words are dim, then brighten as spoken | pop: each word appears when spoken |
| Accent | pale gold `#f5d397`, with a soft glow | amber `#e1ac64`, flat |
| Type | naskh Arabic (Amiri), classical serif English (Cormorant) | geometric sans for both (Cairo, Manrope) |
| Furniture | handle top right, source line, brand lockup | handle left, nothing else |
| Palette | midnight to parchment brown | crimson to dusk blue |
| Ending | big gold Arabic on near-black | slam card: cream `#efe6d8`, ink, brick red `#b54528` |
| Best for | a narrated story, a hadith with context, a dua | a reminder, a question, a short hit |
| Length | 25 to 60s | 10 to 25s |

If the user does not say, pick Lantern for anything with a narrator and a
source, Thread for anything that is one question and one answer. Say which you
picked and why in one line.

The full tokens (sizes, positions, colours, pacing) are in
`styles/lantern.json` and `styles/thread.json`. Those files are the source of
truth. Edit them to make a third style.

## The frame

1080x1920, 9:16. Every position below is a share of frame height.

```
 0%   +-------------------------+
      |   top 12%: Reels chrome |   nothing here
 12%  +-------------------------+
      |  TEXT BLOCK             |   Lantern starts at 12.5%
 25%  |  (handle right, lantern)|   Thread starts at 24.5%
      |                         |
      |  ART                    |   the scene lives here, mid frame
 61%  |  (handle left, thread)  |
 66%  |  source line  (lantern) |
 72%  |  brand        (lantern) |
 75%  +-------------------------+
      |  bottom 25%: caption,   |   nothing here
      |  audio strip, UI        |
100%  +-------------------------+
```

The handle is the one thing allowed in the right margin, because it sits at
y=25% and the action rail does not start until about 45%. Everything else
stays inside the box `/ig-reel` uses: nothing above y=230, nothing below
y=1440. Open the player and press `g` to see the zones drawn on the frame.

The reference reels put the source line and brand lower (74%, 81%). Those sit
under the caption in real use, so they are moved up here.

## Writing for it

- **One idea.** One line is one beat, and a beat is on screen about 1.2 to 3
  seconds. 10 words is a hard ceiling for the Arabic, 12 for the English.
- **Hook on beat one**, under 3 seconds, in the first frame.
- **One accent per line.** The word that carries the meaning goes in
  `*asterisks*`, in both languages, on the same idea. More than two accents and
  nothing is accented.
- **Write the Arabic as Arabic**, not as a translation of the English. Add
  tashkeel where a wrong reading is possible and nowhere else. Honorifics
  (ﷺ, رضي الله عنه) stay in the Arabic line as they would be written. Mirror
  them in the English as the user would write them.
- **The silence is a beat.** A `HOLD 0.8 black` before the turn is the
  strongest cut available. Use one.
- **The payoff gets its own card**: one to three words, nothing else on screen.
  Thread stacks them (`NO / ONE.`). Lantern sets one Arabic phrase large.
- **No beat repeats the one before it.** If the English only restates the
  Arabic in the same shape, merge them.

## The structure

```
BEAT 1     SETUP     wide scene. Who, where. Under 3s.
BEAT 2-3   OBJECT    one object or one figure the idea hangs on. Closer.
BEAT 4     TURN      the line that changes the meaning.
HOLD       SILENCE   black, 0.6 to 1s. Optional, but use it once.
BEAT 5     QUESTION  the scene opens up: wider, lighter, the moon or the sky.
CARD       PAYOFF    the answer, on its own, big.
```

Lantern runs longer and can carry a second act (a dua, a closing scene)
before the card. Thread is the short version of the same arc and often goes
straight from the hook to the question.

## Scenes

Each beat names a background. Built in: `night`, `warm`, `parchment`,
`ember`, `dusk`, `black`, `paper`. These are flat gradients so the layout can
be previewed and shipped with no art at all.

For real art, name a file instead: `image:art/chest.png` or
`video:art/walk.mp4`, 1080x1920, placed so the subject sits in the middle band
(25% to 70%) and the top and bottom stay quiet enough to read text over.

Art direction that holds across both references:

- Flat vector, one light source, no outlines on large shapes.
- **One warm light against a cool field**: a lantern, a keyhole, a glowing
  heart. It is the only bright thing in the frame, so the eye goes there.
- Plain figures: a faceless silhouette or a single stick figure with one
  coloured thread tying it to the idea. No faces.
- Scale is the pacing tool. Open wide, push in on the object, pull back wide
  for the question.
- Dark behind the text. If a scene is light (parchment), darken the top third
  with a gradient so the Arabic stays readable.
- Do not draw the Prophets, the Companions or any figure the user's own
  tradition says not to depict. Use light, objects, hands, silhouettes from
  behind, or text.

## The loop

**1. Write the lines file**, one beat per line. Either language can come first.

```
You told yourself *tomorrow*, || قلتَ لنفسك: *غدًا*، || ember
and tomorrow became a *year*. || وصار الغدُ *سنةً*. || ember
HOLD 0.7 black
So what are you *waiting* for? || فماذا *تنتظر*؟ || dusk
CARD: *TODAY.* || اليوم.
```

`CARD:` is English first, then Arabic. `HOLD secs scene` is a silent beat.
Examples are in `examples/`.

More syntax, all optional:

| write | means |
| --- | --- |
| `*word*` | accent: lit in the style's accent colour, and shown big |
| `~word~` | rejected word: struck through, in the warning red. For "not ~X~, but Y" |
| `^phrase^` | the same red, no strike. For a warning |
| `wa*albasar*` | marker inside a word. The spelling stays whole in the sentence and the big keyword shows only what is inside |
| `@12.5 line` | pin the beat to 12.5s in your recording |
| `word@12.5` | pin one word to a time |
| `arabic` alone | Arabic only, no second language |
| `CARD: \|\| arabic` | an Arabic-only closing card |

**The big keyword.** On a beat with no second language, the accented words are
also shown large in the middle of the frame, one keyword at a time, each from
the moment its word is spoken. The sentence stays small above it. This is the
reference reels' keyword-over-subtitle pattern, and it is what keeps an
Arabic-only Reel from being a single line of small text on an empty frame.

**2. Time it.**

```bash
python3 storyboard.py lines.txt --style thread --handle @you --target 15
```

It prints the beats with timecodes and flags: a hook past 3 seconds, a line
over 10 Arabic or 12 English words, more than two accents, an accent in one
language only, no accent at all, no closing card, a background that holds past
5 seconds, an unknown scene, and a length more than 15% off target. Fix every
flag and run it again.

**3. Preview it.**

```bash
python3 storyboard.py lines.txt --style lantern --handle @you \
  --brand "Your Brand" --source "<the reference you checked>" --html reel.html
```

Open `reel.html` in Chrome. Space plays and pauses, `r` restarts, `g` shows the
Reels safe zones. `?t=4.2` freezes on a moment. Show the user two or three
stills before anything else.

**4. Fit it to the voice.** Timings are estimates at 2.6 to 2.8 words a second.
When the real recording exists, pin every beat with `@seconds` (and the
keywords with `word@seconds`) and the storyboard follows the recording exactly;
each beat runs until the next one starts, and `--end` sets the last frame. If
you only have a rough match, pass `--wps` until the total fits. Pass `--audio
voice.m4a` and the HTML plays it in sync.

You can not hear the audio, and neither can this skill. When the user supplies a
recording, ask for the words and where they fall (or read them from captions
burned into a reference video, as frames sampled every half second), and
never transcribe from a guess.

**5. Export.** One command renders the player to an MP4, frame by frame, and
lays your audio under it. The page is a pure function of time, so the result is
identical on every run and the audio lines up to the frame.

```bash
python3 render.py reel.html --audio voice.m4a --out reel.mp4
```

1080x1920, 30 fps, H.264 plus AAC, about a minute of work per 40 seconds of
video. It needs Playwright for Python, Chrome or Chromium, and ffmpeg. `--scale
0.667` gives 720x1280. For a single still, open
`reel.html?t=4.2&record=1` and screenshot it.

**6. Humanize the English.** Run the English side through `/ig-human`. Do not
run the Arabic through it.

**7. Caption.** Hand off to `/ig-caption`. The caption for a motion Reel does
the work the voice would have done, so it carries the context and the source.

## Output

```
MOTION REEL READY
style:      Thread, 5 beats, 9.4s, 2.8 wps
hook:       "You told yourself tomorrow," at 1.4s
accents:    tomorrow / year / waiting / TODAY
scenes:     ember, ember, black, dusk, card
flags:      none
source:     none given, none shown
preview:    reel.html

Reply "yes" to build the final export, or tell me what to change.
```

Nothing is posted. The user posts it.

## Rules

- **Never fabricate a source.** No hadith number, no narrator, no grading, no
  ayah reference that the user did not give you. Leave `--source` empty.
- **Never put words in a scholar's, a Companion's or the Prophet's mouth that
  the user has not supplied from a source.** A modern reminder is written as
  the user's own voice, not as a quotation.
- **Never reproduce a reference reel.** Same system, original script, original
  art, the user's own handle and brand.
- **Do not guess the theology.** If a line makes a claim about Allah, the
  afterlife or a ruling, it is the user's claim to check. Flag it, do not
  smooth it.
- **Never publish.**
