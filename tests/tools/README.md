# Working tools (not part of the regression suites)

Small scripts used while building. Paths inside them point at `/home/claude` (the working page) and
`/home/claude/repo` (a clone of this repo); change them to match your machine.

- `ev.mjs '<js>' [hash]` or `ev.mjs @file.js`: run a snippet inside the working page and print the result.
- `ev_live.mjs`: the same against the live site.
- `qa.mjs`: every view on desktop and phone, looking for errors, blanks and overflow.
- `bookdiff.mjs [views]`: compare each view between the working page and the split build with a slow `book.js`.
- `bookflash.mjs`: what each view shows while `book.js` is still in flight.
- `perf_live.mjs [url]`: phone load timings on throttled 4G and slow 4G.
- `kirk.js`, `kirk2.js`: the 32 launch-QA cases (run with `ev_live.mjs @kirk.js view=desk`).
