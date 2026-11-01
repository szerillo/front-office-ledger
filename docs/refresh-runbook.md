# Refresh runbook

The exact procedure to refresh every number on the site from a clean machine
(written for the post-World Series refresh, works for any refresh). Python 3
with `reportlab` (`pip install reportlab --break-system-packages`) is the only
dependency beyond the standard library. All data comes from the free MLB
Stats API; nothing needs credentials.

Work in a scratch directory; scripts assume `/work` as the working
root (adjust paths or symlink if elsewhere).

## 0. Clone and seed

    git clone https://github.com/szerillo/front-office-ledger
    cp front-office-ledger/engine/*.py front-office-ledger/ingest/*.py .
    cp front-office-ledger/data/*.json front-office-ledger/data/*.csv .
    cp front-office-ledger/prototype/index.html front-office-ledger-prototype.html

Rebuild `ledger.sqlite` (not shipped; too big for the web upload flow):

    python3 sweep_ingest.py          # transactions, current regime windows
    python3 hist_ingest.py           # full 2005+ re-ingest (archive era)
    python3 retro_backfill.py        # Retrosheet 1985-2008 (the API feed is
                                     # empty pre-2009; scoring floors at 1998);
                                     # needs data/retro2mlbam.json and
                                     # data/retrosheet_tranDB.zip (auto-unzips)
    python3 draft_backfill.py        # drafts 1998-2004 from the draft endpoint
    # draft_picks 2005+ seeds from data/draft_picks.csv inside sweep_ingest

`lvm_cache.json` ships in `data/` at v1.5 (park factors + defense joined,
`__lvm_v15__` marker). Do NOT run `lvm_v1.py` or `lvm_v15_rebuild.py` on it
again unless rebuilding from scratch; the marker guards double-joining but
the backup files will be missing on a fresh machine.

## 1. Update season-bound constants (only at a season rollover)

- `END_YEAR` in `sweep_score.py` and `hist_score.py`
- year ranges in `postseason.py`, `validation.py`, `park_ingest.py`
- new FA winter: `contracts_recent.py` (verify terms by web search),
  QO list + CBT divergences in `contracts_ext.py`, extensions in `EXT`
- regime changes: `data/regimes.json` (active) and `data/regimes_hist.json`
  (a departing exec's window closes and moves to the archive table)

For the post-WS refresh only (same season), none of that changes: the only
new facts are the completed postseason and any early offseason transactions.

## 2. The chain (order matters)

    python3 park_ingest.py           # only if a season was added
    python3 pos_fetch.py             # canonical primaryPosition for the whole
                                     # cache (positions2.json). Rerun whenever
                                     # the player cache changes; everything
                                     # downstream overlays it on positions.json
    python3 sweep_score.py
    python3 fa_grade.py
    python3 ext_grade.py
    python3 ifa_score.py             # idempotent (backs out its prior intl
                                     # net before re-adding); window-filters by
                                     # TRUE signing date; class baseline is
                                     # league value over 30 clubs
    python3 dev_score.py
    python3 postseason.py            # pulls the finished postseason
    python3 archetype.py             # WARNING: ret2.py is NOT idempotent and
                                     # archetype resets chan.ret, so always run
                                     # archetype -> ret2 as a pair, never ret2
                                     # twice without archetype between
    python3 h2h_deals.py             # per-pair deal lists for Head to Head
                                     # (idempotent; after archetype)
    python3 ret2.py
    python3 validation.py
    python3 hist_score.py            # archive era
    python3 champions_build.py       # championship provenance + through lines
    python3 trade_comps.py           # market comps onto every graded trade
    python3 ages_fetch.py            # birth dates (only if the cache changed)
    python3 proj_v1.py               # Ledger Projection v1 onto open deals
    python3 desk_data.py             # Deal Desk data pack. On a pool change
    python3 pt_fetch.py              #   run desk_data -> pt_fetch -> desk_data
    python3 desk_data.py             #   so new pool members get durability
    python3 cache_audit.py           # completeness audit: every 150+ PA /
                                     # 40+ IP player vs the cache; fetch any
                                     # missing at v1.5 BEFORE the chain
    python3 scenario_build.py        # Scenario Room pack (standings-by-date)
    python3 gm_data.py               # Offseason Simulator comp pack (standings)
    python3 calib_suggest.py         # re-backtest the term suggester after a
                                     # new FA winter enters contracts_recent;
                                     # update quoted MAE numbers if they move
                                     # (also writes calib_results.json; the
                                     # page's CALIB scatter data derives from
                                     # it: [name, off, yrs, tot, sugY, sugT])
    python3 regen_v3.py              # splices everything into the prototype

### 2b. Winter-reality maintenance (every offseason, and at the Nov option deadline)

The computed FA class must be reconciled against the real winter:

- `contracts_ext.py` carries three curated blocks: missing guaranteed deals,
  exercised/in-the-money club options (one-year coverage at the option
  price), and the EXT list proper. Update all three from the league option
  tracker after the early-November decision deadline.
- `desk_data.py` carries FA27_NAMES (opt-outs/declines whose remaining book
  coverage is voided; rename per winter) and SVC_FIX (true service for
  players the cup-of-coffee proxy overcounts, plus NPB-origin players free
  by contract expiry encoded as service 6).
- Audit after rebuild: no player with an exercised option in the FA pool,
  every ranked FA in the public class lists present in ours (NPB postings
  with no MLB record excluded, disclosed).

After regen, update
by hand in `front-office-ledger-prototype.html`: the footer date line, the
"postseason in progress" phrasing (now final), and the validation paragraph
numbers if `validation.json` moved.

## 3. Verify before shipping

    node --check on the page's script block; then a headless browser pass:
    leaderboard renders 30 active + 71 archive rows, an archive card opens,
    no console errors. Check one known number against the site to confirm
    the regen actually took.

## 4. Artifacts

    python3 make_packet.py           # application packet PDF
    python3 make_dossiers.py         # 30 counterparty dossiers

## 5. Ship

Copy back into the repo clone: `prototype/index.html`, changed `engine/` and
`ingest/` scripts, and the full refreshed `data/` set (sweep_results,
hist_results, validation, parks, postseason, rental_market, h2h_matrix,
regimes, regimes_hist, lvm_cache, ext_lvm_cache, positions, positions2,
playtime, durability, desk_data, gm_offseasons, scenarios, champs_computed,
calib_results, ages, prospect_orgs). IMPORTANT: any engine/ingest script
copied into the repo gets its working-root paths neutralized first
(replace the local home prefix with /work). Commit via the GitHub web
upload flow (no tokens on this project, ever) and verify the Pages deploy
at szerillo.github.io/front-office-ledger/prototype.

## 6. Regression tests

`tests/` holds the headless acceptance harnesses (node, Playwright,
chromium). Run against the local page before shipping and the live page
after; every file encodes bugs that were actually found and fixed, so a
failure is a regression, not noise:

    node tests/t_gm_core.mjs      # Witt refusal, FA anchors, negotiation
                                  # exploits, payroll on trades
    node tests/t_features.mjs     # advisor, charts, salary book, class
                                  # reality, depth fits
    node tests/t_audit.mjs        # per-card date-vs-window boundary audit,
                                  # phone-width overflow sweep
