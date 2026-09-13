# Single-Timeframe RSI + Stochastic (Pine v5)

TradingView **strategy** plus two companion oscillator panes. RSI and Stochastic always come from **one** timeframe. There is no input that can pair daily RSI with hourly Stochastic.

| File | What it does |
| --- | --- |
| `Single_Timeframe_RSI_Stochastic_Strategy.pine` | Strategy: entries, exits, 2% stop, chart marks, dashboard |
| `Single_Timeframe_RSI_Pane.pine` | RSI pane with overbought / oversold lines |
| `Single_Timeframe_Stochastic_Pane.pine` | Stochastic %K / %D pane with overbought / oversold lines |

Pine Script can draw only **one** extra pane per script, so the oscillators are split into two pane scripts. Add all three to the chart. Set the **same Mode** on each.

## Add to TradingView

1. Open a symbol in TradingView (use a chart **at or below** the signal timeframe: 60m or lower for Swing, 15m or lower for Intraday).
2. Pine Editor → paste the strategy → **Add to chart**.
3. Repeat for the RSI pane script and the Stochastic pane script.
4. Open Settings on each and match **Mode**, RSI length, and Stochastic settings.

The strategy already plots RSI / %K / %D in the status line and data window, and shows them in the dashboard table. The pane scripts are the visual oscillators.

## Switch between Swing and Intraday

1. Click the strategy name on the chart (or its cog in the legend).
2. Open **1. Timeframe discipline**.
3. Set **Mode**:
   - **Swing (Hourly)** — `request.security` reads RSI(14) and Stochastic(14,3,3) from the **60-minute** chart (`lookahead` off).
   - **Intraday (15-min)** — the same two indicators are read from the **15-minute** chart.
4. Set that **same Mode** on the RSI pane and on the Stochastic pane.
5. If the dashboard Timeframe row warns you, drop the chart to the signal timeframe or faster (for example 15m or 5m in Intraday mode).

Mode is the only timeframe control. Both indicators are requested with the same `signalTf` (`"60"` or `"15"`). They cannot drift apart.

## Rules

**Long entry** (all must happen on the same confirmed signal-timeframe bar):

- RSI crosses **up** through the oversold level (default 30)
- Stochastic %K crosses **up** through %D
- Both %K and %D are still **under** the Stochastic oversold level (default 20)

**Exit** (first one that hits):

- RSI crosses **down** through the overbought level (default 70), or
- %K crosses **down** through %D with the cross **above** the Stochastic overbought level (default 80), or
- Stop-loss from entry (default **2%**)

Long only. One position at a time.

## Inputs

- Mode (Swing Hourly / Intraday 15-min)
- RSI length, RSI oversold, RSI overbought
- Stochastic length, %K smoothing, %D smoothing, Stoch oversold / overbought
- Stop-loss %
- Dashboard / markers / background tint

## No repainting

- `request.security(..., lookahead = barmerge.lookahead_off)`
- `process_orders_on_close = true` and `calc_on_every_tick = false`
- Entries and indicator exits require `barstate.isconfirmed`
- When the chart is faster than the signal TF, the strategy uses the **previous completed** signal-TF bar so a forming hourly/15m bar cannot change a signal after the fact

The stop-loss is a real stop order and **can** fill intra-bar; that is intentional protection, not an indicator signal.

## Check scripts locally

```bash
python3 pine/validate_pine.py
python3 pine/tests/test_signal_rules.py
```
