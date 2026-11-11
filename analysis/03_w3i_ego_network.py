"""Web3 Institute ego network: projects with vs without W3I. Run: python analysis/03_w3i_ego_network.py"""
import json, collections as C, itertools
import networkx as nx
from pathlib import Path
R=str(Path(__file__).resolve().parent.parent/"data"/"json")+"/"
L=lambda n: json.load(open(R+n+".json"))
orgs,projects=L("organizations"),L("projects")
on={o["id"]:o for o in orgs}
W=27
MAP={"Academy":"Academy","Gov Bodies":"Government","International Regulator":"Government","government":"Government","MinDigital":"Government",
"Products":"Business","CEX":"Business","L1/L2 Protocol":"Business","Developers":"Business","Mining":"Business","Finance":"Business","business":"Business","Legal":"Business",
"Investments":"Capital","Donor":"Capital","Hub":"Community","Media":"Community","Expert":"Community"}
sec=lambda i: MAP.get(on[i]["sector"],"Unknown")
pw=[p for p in projects if W in p["organization_ids"]]
pn=[p for p in projects if W not in p["organization_ids"] and p["organization_ids"]]
A={i for p in pw for i in p["organization_ids"]}-{W}
B={i for p in pn for i in p["organization_ids"]}
print(f"projects with orgs: {len(pw)+len(pn)} | with W3I: {len(pw)} | without W3I: {len(pn)}")
print(f"orgs: reached by W3I projects {len(A)} | in non-W3I projects {len(B)} | both {len(A&B)} | non-W3I only {len(B-A)}")
print("\nSector profile (orgs in W3I projects vs all orgs in any project vs whole base):")
allp=A|B; base=C.Counter(sec(o["id"]) for o in orgs)
a=C.Counter(sec(i) for i in A); b=C.Counter(sec(i) for i in B-A); ap=C.Counter(sec(i) for i in allp)
for s in ["Business","Academy","Government","Capital","Community","Unknown"]:
    print(f"  {s:11} W3I-reached {a[s]:3} | only non-W3I {b[s]:3} | base {base[s]:3}")
ctry=lambda i:(on[i]["country"] or "unknown")
ua=lambda S:sum(ctry(i).lower()=="ukraine" for i in S)
print(f"\nUkraine share: W3I-reached {ua(A)}/{len(A)} | non-W3I-only {ua(B-A)}/{len(B-A)}")
print("\nNon-W3I-only orgs (the ecosystem W3I projects do not touch):")
for i in sorted(B-A,key=lambda i:sec(i)): print("  ",sec(i),"|",on[i]["name"],"|",ctry(i))
# project-org graph
G=nx.Graph()
for p in projects:
    for i in p["organization_ids"]: G.add_edge(("j",p["id"]),("o",i))
def lcc(H): 
    return max((sum(1 for n in c if n[0]=="o") for c in nx.connected_components(H)),default=0)
tot=sum(1 for n in G if n[0]=="o")
print(f"\nproject-org graph: {tot} orgs, largest component {lcc(G)} ({lcc(G)/tot:.0%})")
H=G.copy(); H.remove_node(("o",W)); print(f"without Web3 Institute node: largest component {lcc(H)} ({lcc(H)/tot:.0%}); orgs in largest: ", lcc(H))
# per-org removal effect: which orgs fragment the graph most
eff=[]
for n in [x for x in G if x[0]=="o"]:
    if G.degree(n)<4: continue
    H=G.copy(); H.remove_node(n); eff.append((lcc(H),on[n[1]]["name"],G.degree(n)))
print("largest component after removing a single org (lowest = most critical):",sorted(eff)[:8])
# W3I-only bridges: org pairs across sectors connected only through W3I-involved projects
pairs_w=set(); pairs_n=set()
for p in pw:
    for x,y in itertools.combinations(sorted(set(p["organization_ids"])-{W}),2): pairs_w.add((x,y))
for p in pn:
    for x,y in itertools.combinations(sorted(set(p["organization_ids"])),2): pairs_n.add((x,y))
onlyw=pairs_w-pairs_n
cross=lambda S:sum(sec(x)!=sec(y) for x,y in S)
print(f"\norg pairs linked via W3I projects: {len(pairs_w)} | via non-W3I: {len(pairs_n)} | only via W3I: {len(onlyw)} ({len(onlyw)/len(pairs_w):.0%} of W3I pairs)")
print(f"cross-sector share: W3I-pairs {cross(pairs_w)/len(pairs_w):.0%} | non-W3I pairs {cross(pairs_n)/max(len(pairs_n),1):.0%}")
# project type of W3I involvement
print("\nW3I project types:",C.Counter(p['type'] for p in pw))
print("non-W3I project types:",C.Counter(p['type'] for p in pn))
# sponsor Binance
bn=[o["id"] for o in orgs if o["name"]=="Binance"]
print("Binance in projects:",sum(bn[0] in p["organization_ids"] for p in projects) if bn else None)
