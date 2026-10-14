# Refresh runbook

The exact procedure to refresh every number on the site from a clean machine
(written for the post-World Series refresh, works for any refresh). Python 3
with `reportlab` (`pip install reportlab --break-system-packages`) is the only
dependency beyond the standard library. All data comes from the free MLB
Stats API; nothing needs credentials.

Work in a scratch directory; scripts assume `/home/claude` as the working
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
    python3 sweep_score.py
    python3 fa_grade.py
    python3 ext_grade.py
    python3 ifa_score.py
    python3 dev_score.py
    python3 postseason.py            # pulls the finished postseason
    python3 archetype.py
    python3 ret2.py
    python3 validation.py
    python3 hist_score.py            # archive era
    python3 champions_build.py       # championship provenance + through lines
    python3 trade_comps.py           # market comps onto every graded trade
    python3 ages_fetch.py            # birth dates (only if the cache changed)
    python3 proj_v1.py               # Ledger Projection v1 onto open deals
    python3 pt_fetch.py              # playing time -> durability factors
                                     # (hits the people API ~150 times)
    python3 desk_data.py             # Deal Desk data pack (fetches prospect
                                     # orgs + standings from the API)
    python3 calib_suggest.py         # optional: re-backtest the term
                                     # suggester after a new FA winter enters
                                     # contracts_recent.py; update the MAE
                                     # numbers quoted in the Desk suggestion
                                     # panel and Methodology if they move
    python3 regen_v3.py              # splices everything into the prototype

`run_chain.sh` in the repo root runs the middle block. After regen, update
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
`ingest/` scripts, `data/` (sweep_results, hist_results, validation, parks,
postseason, rental_market, h2h_matrix, regimes, regimes_hist, lvm_cache,
ext_lvm_cache). Commit via the GitHub web upload flow (no tokens on this
project, ever) and verify the Pages deploy at
szerillo.github.io/front-office-ledger/prototype.
