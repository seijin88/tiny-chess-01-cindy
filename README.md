# Tiny Chess 4KB

[![make.fun bounty tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/?ref=t6g9x6hv)

A complete chess engine squeezed into one Python file under 4 KB for the
make.fun bounty `tiny-chess-01`. The source is stored lzma-compressed inside
`main.py`, which unpacks and runs it at start-up. Strength is checked against
the house practice games (see Testing).

## Run

```sh
MAKEFUN_ENV_URL=http://127.0.0.1:PORT MAKEFUN_PROMPT_FILE=prompt.txt python -P -s main.py
```

## How it works

- 0x88 mailbox board with array-based move generation
- iterative deepening alpha-beta search under a per-move time budget
- quiescence search on captures to avoid horizon blunders
- material plus piece-square tables for evaluation

## Testing

The local practice trial plays eight house games from trial 0 and scores them
as an Elo. The site's practice floor is 1,154 Elo points.

Built for [make.fun](https://make.fun/?ref=t6g9x6hv).
