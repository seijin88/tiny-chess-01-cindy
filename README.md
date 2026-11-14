# tiny-chess-01 engine

A chess engine written for the make.fun **tiny-chess-01** bounty: the strongest chess engine in 4 KB of Python.

`main.py` is the whole engine. It is packed as an lzma-compressed base64 payload inside `main.py`, which unpacks and runs it, so the committed file stays under the 4,096-byte cap.

## Techniques

- 0x88 mailbox move generation
- Iterative deepening with a fixed node budget (deterministic)
- Alpha-beta with late-move reductions
- Quiescence search
- Killer/history move ordering
- Piece-square tables with a phase-interpolated endgame king term

## Run locally

Point `MAKEFUN_ENV_URL` at the practice env, `POST /game` to start a game, then `POST /move` with UCI moves (e.g. `e2e4`).

MIT licensed.
