#!/usr/bin/env python3
"""storyboard.py - bilingual lines in, timed storyboard and a playable HTML out.

No dependencies, no network. Python 3.8+.

    python3 storyboard.py lines.txt --style thread --handle @you
    python3 storyboard.py lines.txt --style lantern --html reel.html --json reel.json

Input, one beat per line:

    arabic || english                  a text beat (either order works)
    arabic                             Arabic only, no second line
    arabic || english || scene         ... on a named background
    @12.5 arabic || english            pin the beat to 12.5s (match a recording)
    CARD: english || arabic            the closing slam card
    HOLD 0.8 black                     a silent beat on a background
    # comment                          ignored

Wrap the one word (or phrase) that carries the line in *asterisks*, in either
language. The accent is what the viewer remembers. Wrap a word you are
rejecting in ~tildes~ and it is struck through ("not ~deprivation~, but dignity").
Use ^carets^ for a warning colour without the strike. A marker can sit inside
a word (wa*albasar*) so the spelling stays whole and the big keyword shows
only what is inside. Add @12.5 after a word to pin it to a time in your recording.

If every beat carries an @time the storyboard follows your recording exactly;
each beat runs until the next one starts. Use --end for the final frame.
"""
import argparse
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
STYLES_DIR = HERE / "styles"
PLAYER = HERE / "player.html"
AR_RE = re.compile(r"[؀-ۿ]")
SCENES = {"night", "warm", "parchment", "ember", "dusk", "black", "paper"}
CARD_SECS = 2.4
FIRST_BEAT_MAX = 3.0
STATIC_MAX = 5.0


MARKS = {"*": "accent", "~": "strike", "^": "warn"}
INNER_RE = re.compile(r"^([^*~^]*)([*~^])(.+?)\2(.*)$")


def tokenize(text, warnings, where):
    """Split on spaces and read the markers: *accent*, ~strike~, ^warn^.

    A marker can sit inside a word to keep its spelling whole: wa*albasar*
    stays one word on screen and the big keyword shows just albasar.
    """
    out, state = [], {"accent": False, "strike": False, "warn": False}
    for tok in text.split():
        pin = None
        pm = re.search(r"@([\d.]+)$", tok)
        if pm:
            pin, tok = float(pm.group(1)), tok[: pm.start()]
        n0 = len(out)
        m = INNER_RE.match(tok)
        if m and (m.group(1) or m.group(4)):
            pre, mk, inner, suf = m.groups()
            w = {"w": pre + inner + suf, "accent": False, "hero": inner}
            w[MARKS[mk]] = True
            out.append(w)
            if pin is not None:
                w["pin"] = pin
            continue
        body = tok.replace("*", "").replace("~", "").replace("^", "")
        starts = tok[:1] if tok[:1] in MARKS else ""
        flags = {k: state[k] or (starts and MARKS[starts] == k) for k in state}
        if body:
            w = {"w": body, "accent": bool(flags["accent"] and not flags["strike"] and not flags["warn"])}
            if flags["strike"]:
                w["strike"] = True
            if flags["warn"]:
                w["warn"] = True
            if pin is not None:
                w["pin"] = pin
            out.append(w)
        for mk, k in MARKS.items():
            if tok.count(mk) % 2 == 1:
                state[k] = not state[k]
    if any(state.values()):
        warnings.append("%s: unbalanced * ~ or ^ marker." % where)
    return out


def load_style(name):
    path = STYLES_DIR / (name + ".json")
    if not path.exists():
        names = ", ".join(sorted(p.stem for p in STYLES_DIR.glob("*.json")))
        sys.exit("Unknown style '%s'. Available: %s" % (name, names))
    return json.loads(path.read_text(encoding="utf-8"))


def parse(path, style, warnings):
    beats = []
    default_scene = style["default_scene"]
    for ln, raw in enumerate(pathlib.Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        where = "line %d" % ln
        at = None
        m = re.match(r"@([\d.]+)\s+(.*)$", line)
        if m:
            at, line = float(m.group(1)), m.group(2).strip()
        m = re.match(r"HOLD\s+([\d.]+)\s*(\S*)$", line, re.I)
        if m:
            beats.append({"kind": "hold", "secs": float(m.group(1)), "at": at,
                          "scene": m.group(2) or "black", "ar": [], "en": [], "src": ln})
            continue
        if line.upper().startswith("CARD:"):
            parts = [p.strip() for p in line[5:].split("||")]
            scene = parts[2] if len(parts) > 2 and parts[2] else "paper"
            beats.append({"kind": "card", "secs": CARD_SECS, "at": at, "scene": scene,
                          "en": tokenize(parts[0], warnings, where),
                          "ar": tokenize(parts[1], warnings, where) if len(parts) > 1 else [],
                          "src": ln})
            continue
        parts = [p.strip() for p in line.split("||")]
        if len(parts) < 2:
            if AR_RE.search(parts[0]):
                parts.append("")
            else:
                warnings.append("%s: expected 'arabic || english', skipped." % where)
                continue
        ar_text, en_text = parts[0], parts[1]
        scene = parts[2] if len(parts) > 2 and parts[2] else default_scene
        # either order works: the field with Arabic letters is the Arabic one
        if not AR_RE.search(ar_text) and AR_RE.search(en_text):
            ar_text, en_text = en_text, ar_text
        elif not AR_RE.search(ar_text):
            warnings.append("%s: neither field has Arabic letters." % where)
        elif AR_RE.search(en_text):
            warnings.append("%s: both fields contain Arabic letters. Using the first as Arabic." % where)
        beats.append({"kind": "line", "secs": None, "at": at, "scene": scene,
                      "ar": tokenize(ar_text, warnings, where),
                      "en": tokenize(en_text, warnings, where), "src": ln})
    return beats


def time_beats(beats, pacing, tail, end):
    t = 0.0
    for i, b in enumerate(beats):
        if b["at"] is not None:
            t = b["at"]
            nxt = next((c["at"] for c in beats[i + 1:] if c["at"] is not None), None)
            if nxt is not None and nxt > t:
                b["secs"] = round(nxt - t, 2)
            elif end and end > t and b["kind"] != "hold":
                b["secs"] = round(end - t, 2)
        if b["secs"] is None:
            n_ar, n_en = len(b["ar"]), len(b["en"])
            need = max(n_ar / pacing["wps"], n_en / (pacing["wps"] * 1.25)) + 0.3
            b["secs"] = round(max(pacing["min_line"], need), 2)
        b["t0"] = round(t, 2)
        b["t1"] = round(t + b["secs"], 2)
        for lang in ("ar", "en"):
            words = b[lang]
            n = len(words)
            for j, w in enumerate(words):
                frac = (j / n) if n else 0
                if "pin" in w:
                    w["t"] = w.pop("pin")
                elif b["kind"] == "card":
                    w["t"] = round(b["t0"] + 0.15 + 0.35 * j, 2)
                else:
                    w["t"] = round(b["t0"] + b["secs"] * 0.7 * frac + 0.05, 2)
        b["hero"] = hero_items(b["ar"])
        pinned_next = i + 1 < len(beats) and beats[i + 1]["at"] is not None
        t = b["t1"] + (0 if pinned_next or b["at"] is not None else (pacing["gap"] if b["kind"] == "line" else 0))
    return round(end if end else t + tail, 2)


def hero_items(words):
    """Consecutive words with the same mark become one big keyword, shown from its first word."""
    items, cur = [], None
    for w in words:
        kind = "strike" if w.get("strike") else "warn" if w.get("warn") else "accent" if w["accent"] else None
        if kind is None:
            cur = None
            continue
        if cur and cur["kind"] == kind and "hero" not in w:
            cur["w"] += " " + w.get("hero", w["w"])
        else:
            cur = {"w": w.get("hero", w["w"]), "t": w["t"], "kind": kind}
            items.append(cur)
    return items


def check(beats, total, target, warnings):
    lines = [b for b in beats if b["kind"] == "line"]
    if not beats:
        warnings.append("No beats found.")
        return
    first = beats[0]
    if first["secs"] > FIRST_BEAT_MAX:
        warnings.append("Hook beat runs %.1fs. Past 3s the viewer has decided. Split it or cut words." % first["secs"])
    for b in lines:
        if len(b["ar"]) > 10:
            warnings.append("Line %d: %d Arabic words. Over 10 and it stops being readable at phone size." % (b["src"], len(b["ar"])))
        if len(b["en"]) > 12:
            warnings.append("Line %d: %d English words. Over 12 and it wraps to three lines." % (b["src"], len(b["en"])))
        acc = sum(1 for w in b["en"] if w["accent"])
        acc_ar = sum(1 for w in b["ar"] if w["accent"])
        if acc > 2 or acc_ar > 2:
            warnings.append("Line %d: more than two accent words. When everything is gold, nothing is." % b["src"])
        if b["en"] and b["ar"] and bool(acc) != bool(acc_ar):
            warnings.append("Line %d: the accent is set in only one language. Mark the same idea in both." % b["src"])
        if b["scene"] not in SCENES and not b["scene"].startswith(("image:", "video:")):
            warnings.append("Line %d: unknown scene '%s'. Use %s, image:path or video:path." % (b["src"], b["scene"], ", ".join(sorted(SCENES))))
    if lines and not any(w["accent"] or w.get("strike") or w.get("warn") for b in lines for w in b["en"] + b["ar"]):
        warnings.append("No accent words anywhere. Mark the one word per line that carries it with *asterisks*.")
    if beats[-1]["kind"] != "card":
        warnings.append("No closing CARD. The payoff should land on its own frame, with nothing else on screen.")
    run, run_scene = 0.0, None
    for b in beats:
        if b["scene"] == run_scene:
            run += b["secs"]
        else:
            run, run_scene = b["secs"], b["scene"]
        if run > STATIC_MAX and b["scene"] != "black":
            warnings.append("Background '%s' holds for %.1fs by %0.1fs. Change the frame or move the art." % (b["scene"], run, b["t1"]))
            run = 0.0
    if target and abs(total - target) / target > 0.15:
        warnings.append("Runs %.1fs against a %.1fs target (%+.0f%%)." % (total, target, 100 * (total - target) / target))


def clip(words, n):
    s = " ".join(("*%s*" % w["w"]) if w["accent"] else ("~%s~" % w["w"]) if w.get("strike") else ("^%s^" % w["w"]) if w.get("warn") else w["w"] for w in words)
    return s if len(s) <= n else s[: n - 3] + "..."


def show(beats, style, total, target, wps, warnings):
    head = "STORYBOARD  -  %s  -  %d beats  -  %.1fs" % (style["name"], len(beats), total)
    if target:
        head += " (target %.1fs)" % target
    print(head + "  -  %.1f wps" % wps)
    print("=" * 78)
    for b in beats:
        m, s = divmod(b["t0"], 60)
        tag = {"line": "", "card": "CARD", "hold": "HOLD"}[b["kind"]]
        en = clip(b["en"], 34) if b["en"] else ""
        ar = clip(b["ar"], 24) if b["ar"] else ""
        print(" %d:%04.1f %4.1fs  %-9s %-4s %s" % (m, s, b["secs"], b["scene"], tag, en))
        if ar:
            print("%32s%s" % ("", ar))
    print("-" * 78)
    if warnings:
        for w in warnings:
            print("  - " + w)
    else:
        print("  Clean. Nothing flagged.")


def main():
    ap = argparse.ArgumentParser(description="Timed storyboard and playable HTML for ig-motion.")
    ap.add_argument("lines", help="text file, one beat per line")
    ap.add_argument("--style", default="thread", help="lantern or thread (default thread)")
    ap.add_argument("--handle", default="@yourhandle", help='handle on screen; pass "" to hide it')
    ap.add_argument("--brand", default="", help="small name under the text (lantern shows it)")
    ap.add_argument("--source", default="", help="source or credit line, shown under the text in lantern")
    ap.add_argument("--audio", default="", help="path to your voiceover, played in sync by the HTML")
    ap.add_argument("--wps", type=float, default=0, help="words per second, overrides the style default")
    ap.add_argument("--target", type=float, default=0, help="target length in seconds")
    ap.add_argument("--tail", type=float, default=0.8, help="seconds to hold after the last beat")
    ap.add_argument("--end", type=float, default=0, help="total length in seconds (overrides --tail)")
    ap.add_argument("--json", default="", help="write the storyboard JSON here")
    ap.add_argument("--html", default="", help="write a self-contained player here")
    a = ap.parse_args()

    style = load_style(a.style)
    pacing = dict(style["pacing"])
    if a.wps:
        pacing["wps"] = a.wps
    warnings = []
    beats = parse(a.lines, style, warnings)
    total = time_beats(beats, pacing, a.tail, a.end)
    check(beats, total, a.target, warnings)
    show(beats, style, total, a.target, pacing["wps"], warnings)

    data = {"style": style, "handle": a.handle, "brand": a.brand, "source": a.source,
            "audio": a.audio, "duration": total, "beats": beats}
    if a.json:
        pathlib.Path(a.json).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        print("\nwrote " + a.json)
    if a.html:
        tpl = PLAYER.read_text(encoding="utf-8")
        blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
        pathlib.Path(a.html).write_text(tpl.replace("null/*__STORYBOARD__*/", blob), encoding="utf-8")
        print("wrote " + a.html + "  (open it in Chrome; space plays, g shows the Reels safe zones)")


if __name__ == "__main__":
    main()
