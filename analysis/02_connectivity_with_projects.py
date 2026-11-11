"""Connectivity and robustness with projects as connectors. Run: python analysis/02_connectivity_with_projects.py"""
import json, random, collections as C
import networkx as nx
from pathlib import Path
R=str(Path(__file__).resolve().parent.parent/"data"/"json")+"/"
L=lambda n: json.load(open(R+n+".json"))
orgs,people,projects=L("organizations"),L("people"),L("projects")
ua={o["id"] for o in orgs if (o["country"] or "").strip().lower()=="ukraine"}
pname={p["id"]:p["name"] for p in people}; prname={p["id"]:p["name"] for p in projects}
def run(name,allowed):
    G=nx.Graph()
    for p in people:
        for i in p["organization_ids"]:
            if i in allowed: G.add_edge(("p",p["id"]),("o",i))
        for j in p["project_ids"]: G.add_edge(("p",p["id"]),("j",j))
    for pr in projects:
        for i in pr["organization_ids"]:
            if i in allowed: G.add_edge(("j",pr["id"]),("o",i))
    # keep only projects reachable to allowed orgs: drop person-project edges for persons without allowed org
    keep={n for n in G if n[0]!="p" or any(m[0]=="o" for m in G[n])}
    G=G.subgraph(keep).copy()
    O=[n for n in G if n[0]=="o"]; N=len(O)
    def lcc(H):
        if not H.number_of_nodes(): return 0
        best=0
        for c in nx.connected_components(H):
            best=max(best,sum(1 for n in c if n[0]=="o"))
        return best/N
    print(f"\n== {name}: orgs {N}, people {sum(n[0]=='p' for n in G)}, projects {sum(n[0]=='j' for n in G)}")
    print(f"baseline largest component holds {lcc(G):.0%} of orgs; components with orgs: {sum(1 for c in nx.connected_components(G) if any(n[0]=='o' for n in c))}")
    # via persons only vs projects only
    Gp=G.copy(); Gp.remove_nodes_from([n for n in G if n[0]=="j"]); print(f"  persons only: {lcc(Gp):.0%}")
    Gj=G.copy(); Gj.remove_nodes_from([n for n in G if n[0]=="p"]); print(f"  projects only: {lcc(Gj):.0%}")
    bc=nx.betweenness_centrality(G,k=min(400,len(G)),seed=2)
    rk=sorted([n for n in G if n[0]!="o"],key=lambda n:-bc[n])
    print("top connectors:",[( (pname if n[0]=='p' else prname)[n[1]]+(" [project]" if n[0]=='j' else "")) for n in rk[:10]])
    pers=[n for n in G if n[0]=="p"]
    for k in [0,3,5,10,20,40]:
        H=G.copy(); H.remove_nodes_from(rk[:k]); 
        rs=[]
        for _ in range(8):
            H2=G.copy(); H2.remove_nodes_from(random.sample(pers,min(k,len(pers)))); rs.append(lcc(H2))
        print(f"  remove top {k:>2} connectors: {lcc(H):.0%} | random persons: {sum(rs)/len(rs):.0%}")
run("ALL",{o["id"] for o in orgs}); run("UKRAINE",ua)
