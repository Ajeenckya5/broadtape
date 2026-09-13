#!/usr/bin/env python3
"""Static checks that Pine v5 files in this folder should compile and stay single-TF."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PINE_FILES = [
    ROOT / "Single_Timeframe_RSI_Stochastic_Strategy.pine",
    ROOT / "Single_Timeframe_RSI_Pane.pine",
    ROOT / "Single_Timeframe_Stochastic_Pane.pine",
]


def strip_comments_and_strings(src: str) -> str:
    out: list[str] = []
    i = 0
    n = len(src)
    while i < n:
        if src.startswith("//", i):
            while i < n and src[i] != "\n":
                i += 1
            continue
        if src[i] in "\"'":
            quote = src[i]
            i += 1
            while i < n and src[i] != quote:
                if src[i] == "\\":
                    i += 2
                    continue
                i += 1
            i += 1
            continue
        out.append(src[i])
        i += 1
    return "".join(out)


def balanced(src: str) -> str | None:
    pairs = {")": "(", "]": "[", "}": "{"}
    opening = set(pairs.values())
    stack: list[str] = []
    for ch in src:
        if ch in opening:
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack[-1] != pairs[ch]:
                return f"unbalanced '{ch}'"
            stack.pop()
    if stack:
        return f"unclosed {stack[-1]!r}"
    return None


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    name = path.name
    code = strip_comments_and_strings(text)

    if not text.startswith("//@version=5"):
        errors.append(f"{name}: must start with //@version=5")

    bal = balanced(code)
    if bal:
        errors.append(f"{name}: {bal}")

    if re.search(r"(?<!request\.)\bsecurity\s*\(", code):
        errors.append(f"{name}: use request.security, not v4 security()")
    if re.search(r"\bstudy\s*\(", code):
        errors.append(f"{name}: study() is v4; use strategy()/indicator()")
    if re.search(r"(?<!ta\.)\bcrossover\s*\(", code):
        errors.append(f"{name}: use ta.crossover")
    if re.search(r"(?<!ta\.)\bcrossunder\s*\(", code):
        errors.append(f"{name}: use ta.crossunder")

    if "lookahead = barmerge.lookahead_off" not in text and "lookahead=barmerge.lookahead_off" not in text:
        errors.append(f"{name}: request.security must set lookahead_off")
    if "barmerge.lookahead_on" in code:
        errors.append(f"{name}: lookahead_on is not allowed (repaint / future bar risk)")

    tf_args = re.findall(
        r"request\.security\s*\(\s*syminfo\.tickerid\s*,\s*([^,]+)\s*,",
        code,
    )
    if not tf_args:
        errors.append(f"{name}: missing request.security on syminfo.tickerid")
    for arg in tf_args:
        if arg.strip() != "signalTf":
            errors.append(f"{name}: security timeframe is {arg.strip()!r}, expected signalTf")

    if "Swing (Hourly)" not in text or "Intraday (15-min)" not in text:
        errors.append(f"{name}: Mode toggle options missing")
    if 'signalTf   = modeInput == "Swing (Hourly)" ? "60" : "15"' not in text:
        errors.append(f"{name}: Mode must map Swing->60 and Intraday->15")

    if name.endswith("_Strategy.pine"):
        for needle in (
            "strategy(",
            "process_orders_on_close = true",
            "calc_on_every_tick     = false",
            "barstate.isconfirmed",
            "ta.crossover(rsiVal, rsiOversold)",
            "ta.crossover(kVal, dVal)",
            "ta.crossunder(rsiVal, rsiOverbought)",
            "ta.crossunder(kVal, dVal)",
            'strategy.exit("SL"',
            "stopLossPct",
            "table.new(",
            "plotshape(",
        ):
            if needle not in text:
                errors.append(f"{name}: missing required snippet {needle!r}")
        if "overlay                = true" not in text:
            errors.append(f"{name}: strategy should overlay price for entry/exit marks")

    if name.endswith("RSI_Pane.pine"):
        if "overlay    = false" not in text:
            errors.append(f"{name}: RSI pane must use overlay=false")
        if "ta.rsi(" not in text:
            errors.append(f"{name}: RSI pane must plot ta.rsi")
        if "hline(" not in text:
            errors.append(f"{name}: RSI pane must draw overbought/oversold lines")

    if name.endswith("Stochastic_Pane.pine"):
        if "overlay    = false" not in text:
            errors.append(f"{name}: Stochastic pane must use overlay=false")
        if "ta.stoch(" not in text:
            errors.append(f"{name}: Stochastic pane must plot ta.stoch")
        if "hline(" not in text:
            errors.append(f"{name}: Stochastic pane must draw overbought/oversold lines")

    return errors


def main() -> int:
    errors: list[str] = []
    for path in PINE_FILES:
        if not path.exists():
            errors.append(f"missing file {path.name}")
            continue
        errors.extend(check_file(path))
    if errors:
        print("Pine validation failed:")
        for err in errors:
            print("  -", err)
        return 1
    print(f"OK: {len(PINE_FILES)} Pine v5 files passed static compile checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
