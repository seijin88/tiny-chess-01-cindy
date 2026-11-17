# tiny-chess-01 engine

A tiny chess engine for the make.fun tiny-chess-01 bounty. `main.py` stays under 4 KB and plays the eight-game gauntlet over the MAKEFUN_ENV_URL HTTP protocol.

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/seijin88/tiny-chess-01-cindy/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/seijin88/tiny-chess-01-cindy/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

See the bounty page: https://make.fun/bounty/tiny-chess-01

## Engine

- 0x88 mailbox board, legal move generation (castling, en passant, queen promotion)
- Iterative-deepening alpha-beta, fixed node budget
- Late move reductions, killer moves, MVV-LVA capture ordering
- Quiescence search over captures
- Eval: material, piece-square tables, phase-interpolated king term, bishop pair
- No wall clock, no randomness: every move follows from the position alone, so a replayed trial equals the live one

## Layout

- `main.py`: entry point; unpacks the engine (lzma + base64), then runs it
- `LICENSE`: MIT

## Rules compliance

- Standard library only
- `main.py` reads no other file
- Every move is derived from the position, so live and replayed trials match byte for byte
