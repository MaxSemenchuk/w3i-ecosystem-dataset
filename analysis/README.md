# Analysis

Reproducible scripts over `data/json/`. Run from the repo root: `pip install -r analysis/requirements.txt && python analysis/<script>.py`.

| Script | Question |
|---|---|
| `01_sector_mixing_and_people_bridges.py` | Do organizations link across sectors more or less than chance? Which people span several sectors? |
| `02_connectivity_with_projects.py` | How connected is the network once projects count as connectors, and how fragile is it? |
| `03_w3i_ego_network.py` | What does the Web3 Institute footprint look like compared with projects it is not part of? |

## Findings (snapshot of the first run)

- Sectors are mixed, not siloed: 61% of org–org links cross sectors (about 73% expected at random).
- Individuals rarely bridge sectors (28 of 636 people); the network is held together by **projects and events**, not people.
- W3I projects reach 129 organizations; 30 organizations appear only in projects without W3I, mostly Ukrainian state agencies, donors and international bodies from earlier blockchain pilots.
- Academia is the largest sector by organizations (131) but appears in few projects (about 9%).

## Caveats

- The data is a snapshot of the W3I-visible network, not a census of the ecosystem (people came largely via W3I and IEEE events).
- Org pairs from large projects (Talent Connect, IEEE UA DLT Forum) inflate pair counts.
- Sector groups are coarse (`Business` includes exchanges, products, protocols, law firms).
- Only 50 projects are recorded; several pilots have no people linked.

`04_figures.py` draws the five figures of the data paper into `paper/figures/` (PNG and SVG). It needs `matplotlib` in addition to `networkx`.
