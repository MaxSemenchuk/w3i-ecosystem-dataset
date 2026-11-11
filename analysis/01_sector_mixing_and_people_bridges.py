"""Cross-sector mixing, bridging people, robustness (person-org graph). Run: python analysis/01_sector_mixing_and_people_bridges.py"""
import json, random, collections as C, itertools
import networkx as nx
from pathlib import Path
R=str(Path(__file__).resolve().parent.parent/"data"/"json")+"/"
L=lambda n: json.load(open(R+n+".json"))
orgs,people,projects=L("organizations"),L("people"),L("projects")
G_MAP={"Academy":"Academy","Gov Bodies":"Government","International Regulator":"Government","government":"Government","MinDigital":"Government",
"Products":"Business","CEX":"Business","L1/L2 Protocol":"Business","Developers":"Business","Mining":"Business","Finance":"Business","business":"Business","Legal":"Business",
"Investments":"Capital","Donor":"Capital","Hub":"Community","Media":"Community","Expert":"Community"}
osec={o["id"]:G_MAP.get(o["sector"],"Unknown") for o in orgs}
oname={o["id"]:o["name"] for o in orgs}
ocountry={o["id"]:(o["country"] or "") for o in orgs}
UA={i for i,c in ocountry.items() if c.strip().lower()=="ukraine"}

def build(allowed):
    B=nx.Graph()
    for p in people:
        os_=[i for i in p["organization_ids"] if i in allowed]
        for i in os_:
            B.add_node(("o",i)); B.add_edge(("p",p["id"]),("o",i))
    # co-membership through projects (orgs sharing a project) as extra org-org edges
    extra=[]
    for pr in projects:
        os_=[i for i in pr["organization_ids"] if i in allowed]
        for a,b in itertools.combinations(os_,2): extra.append((a,b))
    return B,extra

def report(name,allowed):
    B,extra=build(allowed)
    O=[n for n in B if n[0]=="o"]; P=[n for n in B if n[0]=="p"]
    print(f"\n===== {name}: {len(O)} orgs with people, {len(P)} people, {B.number_of_edges()} person-org links")
    # org projection
    Gp=nx.bipartite.projected_graph(B,O)
    for a,b in extra:
        if ("o",a) in Gp and ("o",b) in Gp: Gp.add_edge(("o",a),("o",b))
    for n in Gp: Gp.nodes[n]["s"]=osec[n[1]]
    known=[n for n in Gp if Gp.nodes[n]["s"]!="Unknown"]
    Gk=Gp.subgraph(known)
    ctr=C.Counter(); 
    for a,b in Gk.edges(): ctr[tuple(sorted((Gk.nodes[a]["s"],Gk.nodes[b]["s"])))]+=1
    tot=sum(ctr.values()); cross=sum(v for (a,b),v in ctr.items() if a!=b)
    # null model: shuffle labels
    labels=[Gk.nodes[n]["s"] for n in Gk]; nulls=[]
    for _ in range(200):
        random.shuffle(labels); d=dict(zip(Gk.nodes,labels))
        nulls.append(sum(d[a]!=d[b] for a,b in Gk.edges())/tot)
    print(f"org-org edges (known sector): {tot}; cross-sector share {cross/tot:.1%}; random expectation {sum(nulls)/len(nulls):.1%}")
    print("assortativity by sector:", round(nx.attribute_assortativity_coefficient(Gk,"s"),3))
    print("pairs:",[(f"{a}-{b}",v) for (a,b),v in ctr.most_common(10)])
    comps=sorted(nx.connected_components(Gp),key=len,reverse=True)
    print(f"org components: {len(comps)}; largest {len(comps[0])} ({len(comps[0])/len(O):.0%}); isolated-pair-or-single comps {sum(len(c)<=2 for c in comps)}")
    # per-sector share inside LCC
    lcc=comps[0]; sc=C.Counter(osec[n[1]] for n in O); sl=C.Counter(osec[n[1]] for n in lcc)
    print("share in largest component by sector:",{k:f"{sl[k]}/{sc[k]}" for k in sc})
    # people bridging sectors
    multi=[]; 
    for p in people:
        s={osec[i] for i in p["organization_ids"] if i in allowed and osec[i]!="Unknown"}
        if len(s)>=2: multi.append((p["name"],sorted(s)))
    withorg=sum(1 for p in people if any(i in allowed for i in p["organization_ids"]))
    print(f"people in >=2 sectors: {len(multi)} of {withorg} ({len(multi)/withorg:.1%})")
    print("sector pairs of bridging people:",C.Counter(tuple(s) if len(s)==2 else ("3+",) for _,s in multi).most_common(8))
    # robustness: remove top-k people by number of orgs / betweenness, LCC share of orgs
    bc=nx.betweenness_centrality(B,k=min(300,len(B)),seed=1)
    rank_p=sorted(P,key=lambda n:-bc[n]); 
    top=[(next(p["name"] for p in people if p["id"]==n[1]),round(bc[n],4)) for n in rank_p[:8]]
    print("top people by betweenness:",top)
    def lcc_share(rem):
        H=B.copy(); H.remove_nodes_from(rem)
        Os=[n for n in H if n[0]=="o"]
        if not Os: return 0
        Hp=nx.bipartite.projected_graph(H,Os)
        return len(max(nx.connected_components(Hp),key=len))/len(O)
    print("LCC share of orgs after removing top-k people by betweenness vs random:")
    for k in [0,5,10,25,50]:
        rnd=sum(lcc_share(random.sample(P,k)) for _ in range(5))/5 if k else lcc_share([])
        print(f"  k={k}: targeted {lcc_share(rank_p[:k]):.0%}  random {rnd:.0%}")

report("ALL",set(osec))
report("UKRAINE-based orgs",UA)
