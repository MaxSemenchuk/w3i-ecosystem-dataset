"""Figures for the data paper, computed from data/json. Run: python3 -I analysis/04_figures.py
Writes paper/figures/fig1..fig5 (.png and .svg). Requires: networkx, matplotlib."""
import json, random, itertools, collections as C
from pathlib import Path
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "data" / "json"
OUT = ROOT / "paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
L = lambda n: json.load(open(R / f"{n}.json"))
orgs, people, projects, tags, materials = (L(n) for n in ["organizations", "people", "projects", "tags", "materials"])

# palette (categorical slots 1-3, sequential blue, text/ink tokens) from the dataviz reference palette
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE, AQUA, YELLOW, MAGENTA = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
SEQ = ["#e8f0fb", "#bcd4f3", "#8db6ea", "#5e97e0", "#2a78d6", "#1c58a0", "#123c70"]
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "text.color": INK, "axes.labelcolor": INK2,
    "axes.edgecolor": GRID, "xtick.color": INK2, "ytick.color": INK2,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
})

MAP = {"Academy": "Academy", "Gov Bodies": "Government", "International Regulator": "Government", "government": "Government", "MinDigital": "Government",
       "Products": "Business", "CEX": "Business", "L1/L2 Protocol": "Business", "Developers": "Business", "Mining": "Business", "Finance": "Business", "business": "Business", "Legal": "Business",
       "Investments": "Capital", "Donor": "Capital", "Hub": "Community", "Media": "Community", "Expert": "Community"}
SECTORS = ["Academy", "Business", "Government", "Capital", "Community"]
sec = {o["id"]: MAP.get(o["sector"], "Unknown") for o in orgs}
W3I = 27


def save(fig, name):
    for ext in ("png", "svg"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


def clean_axes(ax, grid_axis=None):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)
    if grid_axis:
        ax.grid(axis=grid_axis, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)


# ---------------------------------------------------------------- Fig 1: schema
def fig1():
    n_po = sum(len(p["organization_ids"]) for p in people)
    n_pp = sum(len(p["project_ids"]) for p in people)
    n_pt = sum(len(p["tag_ids"]) for p in people)
    n_jo = sum(len(p["organization_ids"]) for p in projects)
    n_jt = sum(len(p["tag_ids"]) for p in projects)
    n_ot = sum(len(o["tag_ids"]) for o in orgs)
    n_jj = len({frozenset((p["id"], j)) for p in projects for j in p["related_project_ids"]})
    box = {"organizations": (0.5, 0.66, len(orgs)), "people": (0.12, 0.66, len(people)),
           "projects": (0.88, 0.66, len(projects)), "tags": (0.5, 0.18, len(tags)),
           "materials": (0.88, 0.18, len(materials))}
    fig, ax = plt.subplots(figsize=(6.6, 3.9))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    w, h = 0.22, 0.14
    for name, (x, y, n) in box.items():
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.005,rounding_size=0.02",
                                    fc="white", ec=BLUE if name != "materials" else ORANGE, lw=1.6))
        ax.text(x, y + 0.02, name, ha="center", va="center", fontsize=10, fontweight="bold", color=INK)
        ax.text(x, y - 0.03, f"{n:,} records", ha="center", va="center", fontsize=8.5, color=INK2)

    def link(a, b, label, rad=0.0, ls="-", lx=0.0, ly=0.0, shrink=(36, 36), at=None):
        (x1, y1, _), (x2, y2, _) = box[a], box[b]
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), zorder=0,
                    arrowprops=dict(arrowstyle="-", color=INK2, lw=1.1, ls=ls, connectionstyle=f"arc3,rad={rad}",
                                    shrinkA=shrink[0], shrinkB=shrink[1]))
        px, py = at if at else ((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly)
        ax.text(px, py, label, ha="center", va="center", fontsize=8, color=INK2, bbox=dict(fc=SURFACE, ec="none", pad=1.5))

    link("people", "organizations", f"{n_po:,} links")
    link("projects", "organizations", f"{n_jo:,} links")
    link("people", "projects", f"{n_pp:,} links", rad=-0.3, shrink=(40, 40), at=(0.5, 0.855))
    link("people", "tags", f"{n_pt:,} links", lx=-0.04)
    link("projects", "tags", f"{n_jt:,} links", lx=0.04)
    link("organizations", "tags", f"{n_ot:,} links")
    link("materials", "tags", "linked by topic label", ls=(0, (4, 3)))
    ax.text(0.9, 0.47, f"{n_jj} project–project links", ha="center", va="center", fontsize=8, color=INK2)
    ax.set_title("Five record types; links are stored as id arrays", loc="left", fontsize=10, color=INK, pad=2)
    save(fig, "fig1_schema")


# ---------------------------------------------------------------- Fig 2: sector mixing
def org_graph(allowed=None):
    B = nx.Graph()
    for p in people:
        for i in p["organization_ids"]:
            if allowed is None or i in allowed:
                B.add_edge(("p", p["id"]), ("o", i))
    O = [n for n in B if n[0] == "o"]
    Gp = nx.bipartite.projected_graph(B, O)
    for pr in projects:
        os_ = [i for i in pr["organization_ids"] if ("o", i) in Gp]
        for a, b in itertools.combinations(os_, 2):
            Gp.add_edge(("o", a), ("o", b))
    return Gp


def fig2():
    Gp = org_graph()
    known = [n for n in Gp if sec[n[1]] in SECTORS]
    Gk = Gp.subgraph(known)
    edges = list(Gk.edges())
    idx = {s: i for i, s in enumerate(SECTORS)}
    obs = [[0] * 5 for _ in range(5)]
    for a, b in edges:
        i, j = idx[sec[a[1]]], idx[sec[b[1]]]
        obs[i][j] += 1
        if i != j:
            obs[j][i] += 1
    random.seed(7)
    labels = [sec[n[1]] for n in Gk]
    nodes = list(Gk.nodes)
    exp = [[0.0] * 5 for _ in range(5)]
    N = 300
    for _ in range(N):
        random.shuffle(labels)
        d = dict(zip(nodes, labels))
        for a, b in edges:
            i, j = idx[d[a]], idx[d[b]]
            exp[i][j] += 1 / N
            if i != j:
                exp[j][i] += 1 / N
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.6))
    # left: observed counts (sequential)
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
    seq = LinearSegmentedColormap.from_list("seq", SEQ)
    O = np.array(obs, float)
    ax = axes[0]
    ax.imshow(O, cmap=seq, vmin=0, vmax=O.max())
    for i in range(5):
        for j in range(5):
            ax.text(j, i, int(O[i, j]), ha="center", va="center", fontsize=8,
                    color="white" if O[i, j] > O.max() * 0.45 else INK)
    ax.set_title("Observed links", loc="left", fontsize=9.5, color=INK)
    # right: observed / expected
    ratio = O / np.array(exp)
    div = LinearSegmentedColormap.from_list("div", [ORANGE, "#f4f3f0", BLUE])
    ax2 = axes[1]
    ax2.imshow(np.log2(ratio), cmap=div, norm=TwoSlopeNorm(0, vmin=-2, vmax=2))
    for i in range(5):
        for j in range(5):
            ax2.text(j, i, f"{ratio[i, j]:.1f}×", ha="center", va="center", fontsize=8, color=INK)
    ax2.set_title("Observed ÷ expected by chance", loc="left", fontsize=9.5, color=INK)
    for a in axes:
        a.set_xticks(range(5)); a.set_yticks(range(5))
        a.set_xticklabels(SECTORS, rotation=40, ha="right"); a.set_yticklabels(SECTORS)
        a.tick_params(length=0)
        for s in a.spines.values():
            s.set_visible(False)
    tot = sum(1 for a, b in edges)
    cross = sum(1 for a, b in edges if sec[a[1]] != sec[b[1]])
    fig.text(0.01, -0.02, f"{len(edges):,} organization–organization links with a known sector; {cross / tot:.0%} cross sector boundaries. "
             "Expected values: 300 random reassignments of sector labels.\nBlue = more links than chance, orange = fewer.",
             fontsize=7.5, color=INK2, va="top")
    fig.tight_layout()
    save(fig, "fig3_sector_mixing")


# ---------------------------------------------------------------- Fig 3: robustness
def fig3():
    G = nx.Graph()
    for p in people:
        for i in p["organization_ids"]:
            G.add_edge(("p", p["id"]), ("o", i))
        for j in p["project_ids"]:
            G.add_edge(("p", p["id"]), ("j", j))
    for pr in projects:
        for i in pr["organization_ids"]:
            G.add_edge(("j", pr["id"]), ("o", i))
    keep = {n for n in G if n[0] != "p" or any(m[0] == "o" for m in G[n])}
    G = G.subgraph(keep).copy()
    N = sum(1 for n in G if n[0] == "o")

    def lcc(H):
        return max((sum(1 for n in c if n[0] == "o") for c in nx.connected_components(H)), default=0) / N

    bc = nx.betweenness_centrality(G, k=min(400, len(G)), seed=2)
    rk = sorted([n for n in G if n[0] != "o"], key=lambda n: -bc[n])
    pers = [n for n in G if n[0] == "p"]
    ks = [0, 1, 2, 3, 5, 7, 10, 15, 20, 30, 40]
    random.seed(11)
    targeted, rnd = [], []
    for k in ks:
        H = G.copy(); H.remove_nodes_from(rk[:k]); targeted.append(lcc(H) * 100)
        rs = []
        for _ in range(10):
            H2 = G.copy(); H2.remove_nodes_from(random.sample(pers, k)); rs.append(lcc(H2) * 100)
        rnd.append(sum(rs) / len(rs))
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.plot(ks, targeted, color=BLUE, lw=2, marker="o", ms=5, mfc=SURFACE, mew=2)
    ax.plot(ks, rnd, color=ORANGE, lw=2, marker="o", ms=5, mfc=SURFACE, mew=2)
    ax.text(40.8, targeted[-1], "most central\nconnectors removed", color=INK, va="center", fontsize=8.5)
    ax.text(40.8, rnd[-1], "random people\nremoved", color=INK, va="center", fontsize=8.5)
    for k in (0, 3, 40):
        ax.annotate(f"{targeted[ks.index(k)]:.0f}%", (k, targeted[ks.index(k)]), textcoords="offset points",
                    xytext=((-6, 8) if k == 40 else (0, -14 if k else 8)), ha="center", fontsize=8.5, color=INK)
    ax.set_xlim(-1, 48); ax.set_ylim(0, 80)
    ax.set_xlabel("Number of nodes removed"); ax.set_ylabel("Organizations in the largest\nconnected component (%)")
    clean_axes(ax, "y")
    ax.set_title("The network depends on a few programmes and events, not on random people",
                 loc="left", fontsize=9.5, color=INK)
    fig.text(0.01, -0.02, f"Graph: {N} organizations, people and projects as connectors. Connectors ranked by sampled betweenness (k=400). "
             "Random removal: mean of 10 draws.\nEight of the nine highest-ranked connectors are projects or events.",
             fontsize=7.5, color=INK2, va="top")
    save(fig, "fig4_robustness")
    top = [("project" if n[0] == "j" else "person") for n in rk[:9]]
    print("top-9 connectors:", C.Counter(top))


# ---------------------------------------------------------------- Fig 4: W3I vs non-W3I
def fig4():
    pw = [p for p in projects if W3I in p["organization_ids"]]
    pn = [p for p in projects if W3I not in p["organization_ids"] and p["organization_ids"]]
    A = {i for p in pw for i in p["organization_ids"]} - {W3I}
    Bs = {i for p in pn for i in p["organization_ids"]}
    cats = ["Business", "Government", "Community", "Capital", "Academy", "Unknown"]
    only_w = [sum(1 for i in A - Bs if sec[i] == s) for s in cats]
    both = [sum(1 for i in A & Bs if sec[i] == s) for s in cats]
    only_n = [sum(1 for i in Bs - A if sec[i] == s) for s in cats]
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    y = list(range(len(cats)))[::-1]
    gap = 0.4
    left = [0] * len(cats)
    for vals, col, lab in ((only_w, BLUE, f"Only in projects with W3I ({len(A - Bs)})"),
                           (both, AQUA, f"In both ({len(A & Bs)})"),
                           (only_n, ORANGE, f"Only in projects without W3I ({len(Bs - A)})")):
        ax.barh(y, vals, left=left, height=0.62, color=col, edgecolor=SURFACE, linewidth=gap * 2, label=lab)
        for yy, v, l in zip(y, vals, left):
            if v >= 6:
                ax.text(l + v / 2, yy, v, ha="center", va="center", fontsize=8, color="white" if col != AQUA else INK)
        left = [a + b for a, b in zip(left, vals)]
    ax.set_yticks(y); ax.set_yticklabels(cats)
    ax.set_xlabel("Organizations in at least one project")
    clean_axes(ax, "x")
    ax.legend(loc="lower right", frameon=False, fontsize=8)
    ax.set_title("Where W3I's projects reach, and what they do not touch", loc="left", fontsize=9.5, color=INK)
    fig.text(0.01, -0.02, f"{len(pw)} projects with W3I as participant, {len(pn)} without (projects with no recorded organizations are excluded). "
             "W3I itself is not counted.", fontsize=7.5, color=INK2, va="top")
    save(fig, "fig5_w3i_reach")


# ---------------------------------------------------------------- Fig 5: coverage
def fig5():
    def share(rows, f):
        return 100 * sum(1 for r in rows if f(r)) / len(rows)
    items = [
        ("Organizations", "sector known", share(orgs, lambda o: sec[o["id"]] != "Unknown")),
        ("Organizations", "country", share(orgs, lambda o: bool((o["country"] or "").strip()))),
        ("Organizations", "description", share(orgs, lambda o: bool(o["description"]))),
        ("Organizations", "tags", share(orgs, lambda o: bool(o["tag_ids"]))),
        ("Projects", "organizations", share(projects, lambda p: bool(p["organization_ids"]))),
        ("Projects", "description", share(projects, lambda p: bool(p["description"]))),
    ]
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    y = list(range(len(items)))[::-1]
    ax.barh(y, [100] * len(items), height=0.55, color=GRID)
    ax.barh(y, [v for _, _, v in items], height=0.55, color=BLUE)
    ax.set_yticks(y); ax.set_yticklabels([f"{e}: {a}" for e, a, _ in items])
    for yy, (_, _, v) in zip(y, items):
        ax.text(101.5, yy, f"{v:.0f}%", va="center", fontsize=8.5, color=INK)
    ax.set_xlim(0, 112); ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Records with the field filled (%)")
    clean_axes(ax)
    ax.set_title("How complete the records are", loc="left", fontsize=9.5, color=INK)
    save(fig, "fig2_coverage")
    for e, a, v in items:
        print(f"  {e}: {a}: {v:.0f}%")


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); fig5()
