#!/usr/bin/env python3
"""Signal-rule tests that mirror the Pine strategy (same-bar AND entry, OR exits)."""

from __future__ import annotations


def crossover(prev_a: float, a: float, prev_b: float, b: float) -> bool:
    return prev_a <= prev_b and a > b


def crossunder(prev_a: float, a: float, prev_b: float, b: float) -> bool:
    return prev_a >= prev_b and a < b


def long_entry(
    prev_rsi: float,
    rsi: float,
    prev_k: float,
    k: float,
    prev_d: float,
    d: float,
    rsi_os: float = 30,
    stoch_os: float = 20,
    bar_closed: bool = True,
) -> bool:
    rsi_leave = crossover(prev_rsi, rsi, rsi_os, rsi_os)
    stoch_bull = crossover(prev_k, k, prev_d, d)
    both_os = k < stoch_os and d < stoch_os
    return bar_closed and rsi_leave and stoch_bull and both_os


def long_exit(
    prev_rsi: float,
    rsi: float,
    prev_k: float,
    k: float,
    prev_d: float,
    d: float,
    rsi_ob: float = 70,
    stoch_ob: float = 80,
    bar_closed: bool = True,
) -> bool:
    rsi_exit = crossunder(prev_rsi, rsi, rsi_ob, rsi_ob)
    stoch_bear = crossunder(prev_k, k, prev_d, d) and max(k, d) > stoch_ob
    return bar_closed and (rsi_exit or stoch_bear)


def stop_hit(entry: float, low: float, stop_pct: float = 2.0) -> bool:
    return low <= entry * (1.0 - stop_pct / 100.0)


def mode_to_tf(mode: str) -> str:
    return "60" if mode == "Swing (Hourly)" else "15"


def test_mode_maps_to_one_tf() -> None:
    assert mode_to_tf("Swing (Hourly)") == "60"
    assert mode_to_tf("Intraday (15-min)") == "15"


def test_long_requires_both_crosses_in_oversold() -> None:
    assert long_entry(prev_rsi=25, rsi=31, prev_k=10, k=16, prev_d=14, d=12)
    # RSI crossed but stochastic did not
    assert not long_entry(prev_rsi=25, rsi=31, prev_k=16, k=18, prev_d=12, d=14)
    # Stoch crossed but RSI did not
    assert not long_entry(prev_rsi=32, rsi=35, prev_k=10, k=16, prev_d=14, d=12)
    # Crosses happen but K/D are not both under 20
    assert not long_entry(prev_rsi=25, rsi=31, prev_k=18, k=22, prev_d=21, d=19)


def test_no_entry_until_bar_close() -> None:
    assert not long_entry(25, 31, 10, 16, 14, 12, bar_closed=False)


def test_rsi_exit_and_stoch_exit() -> None:
    assert long_exit(prev_rsi=72, rsi=68, prev_k=40, k=42, prev_d=38, d=39)
    assert long_exit(prev_rsi=55, rsi=56, prev_k=85, k=81, prev_d=82, d=83)
    # Stoch bear cross below 80 does not exit
    assert not long_exit(prev_rsi=55, rsi=56, prev_k=60, k=50, prev_d=55, d=54)
    assert not long_exit(72, 68, 40, 42, 38, 39, bar_closed=False)


def test_stop_loss_two_percent() -> None:
    assert stop_hit(100.0, 97.9)
    assert not stop_hit(100.0, 98.1)


def test_single_tf_discipline() -> None:
    """Both indicators share one mapping; there is no second TF knob."""
    swing = {"rsi_tf": mode_to_tf("Swing (Hourly)"), "stoch_tf": mode_to_tf("Swing (Hourly)")}
    intra = {"rsi_tf": mode_to_tf("Intraday (15-min)"), "stoch_tf": mode_to_tf("Intraday (15-min)")}
    assert swing["rsi_tf"] == swing["stoch_tf"] == "60"
    assert intra["rsi_tf"] == intra["stoch_tf"] == "15"
    assert swing["rsi_tf"] != intra["stoch_tf"]


if __name__ == "__main__":
    tests = [
        test_mode_maps_to_one_tf,
        test_long_requires_both_crosses_in_oversold,
        test_no_entry_until_bar_close,
        test_rsi_exit_and_stoch_exit,
        test_stop_loss_two_percent,
        test_single_tf_discipline,
    ]
    for fn in tests:
        fn()
        print("ok", fn.__name__)
    print(f"OK: {len(tests)} signal-rule tests passed.")
