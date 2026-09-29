"""
NetPath - Routing Module
------------------------
Implements:
  * Dijkstra's link-state shortest path
  * Yen's k-shortest (alternate) paths
  * Distance Vector routing (distributed Bellman-Ford simulation,
    with split horizon + poisoned reverse)
  * Routing table generation (primary + backup next hop)
  * Input handling (JSON / edge-list text) and output (console, JSON, CSV)

Usage:
    python routing.py topology.json
    python routing.py topology.json --source A --dest F -k 3
    python routing.py topology.json --out-dir out/
    python routing.py topology.json --fail C-E        # simulate link failure
"""
import argparse
import csv
import heapq
import json
import os
import sys

INF = float("inf")


# ----------------------------------------------------------------------
# Graph + input handling
# ----------------------------------------------------------------------
class Graph:
    """Undirected weighted graph. Costs must be positive."""

    def __init__(self):
        self.adj = {}  # node -> {neighbor: cost}

    def add_node(self, n):
        self.adj.setdefault(str(n), {})

    def add_edge(self, u, v, cost):
        u, v, cost = str(u), str(v), float(cost)
        if u == v:
            raise ValueError(f"Self-loop not allowed: {u}-{v}")
        if cost <= 0:
            raise ValueError(f"Cost must be positive: {u}-{v} = {cost}")
        self.add_node(u)
        self.add_node(v)
        self.adj[u][v] = cost
        self.adj[v][u] = cost

    def remove_edge(self, u, v):
        if v not in self.adj.get(u, {}):
            raise KeyError(f"No such link: {u}-{v}")
        del self.adj[u][v]
        del self.adj[v][u]

    def update_cost(self, u, v, cost):
        """Hook for the congestion module: change a link's cost dynamically."""
        if v not in self.adj.get(u, {}):
            raise KeyError(f"No such link: {u}-{v}")
        self.add_edge(u, v, cost)

    def nodes(self):
        return sorted(self.adj)

    def edges(self):
        seen, out = set(), []
        for u in self.adj:
            for v, c in self.adj[u].items():
                if (v, u) not in seen:
                    seen.add((u, v))
                    out.append((u, v, c))
        return out

    def copy(self):
        g = Graph()
        for u, v, c in self.edges():
            g.add_edge(u, v, c)
        for n in self.adj:
            g.add_node(n)
        return g

    # ---- loaders ----
    @classmethod
    def from_json(cls, path):
        with open(path) as f:
            data = json.load(f)
        g = cls()
        for n in data.get("nodes", []):
            g.add_node(n)
        for e in data["edges"]:
            g.add_edge(e["u"], e["v"], e["cost"])
        return g

    @classmethod
    def from_edgelist(cls, path):
        """Text file, one link per line: 'A B 4'. '#' starts a comment."""
        g = cls()
        with open(path) as f:
            for ln, line in enumerate(f, 1):
                line = line.split("#")[0].strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) != 3:
                    raise ValueError(f"Line {ln}: expected 'u v cost', got '{line}'")
                g.add_edge(*parts)
        return g

    @classmethod
    def load(cls, path):
        if path.endswith(".json"):
            return cls.from_json(path)
        return cls.from_edgelist(path)


# ----------------------------------------------------------------------
# Dijkstra
# ----------------------------------------------------------------------
def dijkstra(graph, source):
    """Return (dist, prev) from source to every node."""
    if source not in graph.adj:
        raise KeyError(f"Unknown node: {source}")
    dist = {n: INF for n in graph.adj}
    prev = {n: None for n in graph.adj}
    dist[source] = 0
    pq = [(0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in graph.adj[u].items():
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    return dist, prev


def build_path(prev, source, dest):
    path, cur = [], dest
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path if path and path[0] == source else []


def shortest_path(graph, source, dest):
    dist, prev = dijkstra(graph, source)
    if dist[dest] == INF:
        return INF, []
    return dist[dest], build_path(prev, source, dest)


def path_cost(graph, path):
    return sum(graph.adj[a][b] for a, b in zip(path, path[1:]))


# ----------------------------------------------------------------------
# Alternate paths: Yen's k-shortest loopless paths
# ----------------------------------------------------------------------
def k_shortest_paths(graph, source, dest, k=3):
    """Return up to k loopless paths as [(cost, [nodes...]), ...], best first."""
    cost, path = shortest_path(graph, source, dest)
    if not path:
        return []
    A = [(cost, path)]
    B = []  # candidate heap
    for _ in range(1, k):
        last = A[-1][1]
        for i in range(len(last) - 1):
            spur, root = last[i], last[: i + 1]
            g = graph.copy()
            # block edges used by already-found paths sharing this root
            for _, p in A:
                if p[: i + 1] == root and len(p) > i + 1:
                    if p[i + 1] in g.adj[p[i]]:
                        g.remove_edge(p[i], p[i + 1])
            # block root nodes (except spur) to keep the path loopless
            for n in root[:-1]:
                for nb in list(g.adj[n]):
                    g.remove_edge(n, nb)
            sc, sp = shortest_path(g, spur, dest)
            if sp:
                total = root[:-1] + sp
                cand = (path_cost(graph, total), total)
                if cand not in B and cand not in A:
                    heapq.heappush(B, cand)
        if not B:
            break
        A.append(heapq.heappop(B))
    return A


# ----------------------------------------------------------------------
# Distance Vector routing (synchronous simulation)
# ----------------------------------------------------------------------
def distance_vector(graph, poison_reverse=True, max_rounds=100):
    """
    Simulate DV rounds until no table changes.
    Returns (tables, rounds) where tables[node][dest] = (cost, next_hop).
    """
    nodes = graph.nodes()
    table = {n: {d: (INF, None) for d in nodes} for n in nodes}
    for n in nodes:
        table[n][n] = (0, n)
        for nb, c in graph.adj[n].items():
            table[n][nb] = (c, nb)

    rounds = 0
    while rounds < max_rounds:
        rounds += 1
        # every node advertises its vector; with poisoned reverse, routes
        # learned via neighbor X are advertised to X as infinity
        adverts = {}
        for n in nodes:
            for nb in graph.adj[n]:
                adverts[(n, nb)] = {
                    d: (INF if poison_reverse and table[n][d][1] == nb and d != nb
                        else table[n][d][0])
                    for d in nodes
                }
        changed = False
        new_table = {n: dict(table[n]) for n in nodes}
        for n in nodes:
            for nb, link in graph.adj[n].items():
                vec = adverts[(nb, n)]
                for d in nodes:
                    cand = link + vec[d]
                    if cand < new_table[n][d][0]:
                        new_table[n][d] = (cand, nb)
                        changed = True
        table = new_table
        if not changed:
            break
    return table, rounds


# ----------------------------------------------------------------------
# Routing table generation
# ----------------------------------------------------------------------
def build_routing_tables(graph, k=2):
    """
    Per-node table: dest -> primary (next_hop, cost, path) and
    alternate (next_hop, cost, path) if a different next hop exists.
    """
    tables = {}
    for src in graph.nodes():
        dist, prev = dijkstra(graph, src)
        rows = []
        for dst in graph.nodes():
            if dst == src:
                continue
            if dist[dst] == INF:
                rows.append({"dest": dst, "next_hop": None, "cost": None,
                             "path": [], "alt_next_hop": None,
                             "alt_cost": None, "alt_path": []})
                continue
            paths = k_shortest_paths(graph, src, dst, k=k + 2)
            primary = paths[0]
            alt = next((p for p in paths[1:] if p[1][1] != primary[1][1]), None)
            if alt is None and len(paths) > 1:  # fall back: same next hop, diff path
                alt = paths[1]
            rows.append({
                "dest": dst,
                "next_hop": primary[1][1],
                "cost": primary[0],
                "path": primary[1],
                "alt_next_hop": alt[1][1] if alt else None,
                "alt_cost": alt[0] if alt else None,
                "alt_path": alt[1] if alt else [],
            })
        tables[src] = rows
    return tables


def verify_dv_matches_dijkstra(graph, dv_table):
    """Sanity check: DV costs must equal Dijkstra costs."""
    for src in graph.nodes():
        dist, _ = dijkstra(graph, src)
        for dst in graph.nodes():
            if abs(dist[dst] - dv_table[src][dst][0]) > 1e-9 and not (
                    dist[dst] == INF and dv_table[src][dst][0] == INF):
                return False
    return True


# ----------------------------------------------------------------------
# Output handling
# ----------------------------------------------------------------------
def fmt(x):
    if x is None or x == INF:
        return "-"
    return str(int(x)) if float(x).is_integer() else f"{x:.2f}"


def print_tables(tables):
    for src, rows in tables.items():
        print(f"\nRouting table for {src}")
        print(f"{'Dest':<6}{'NextHop':<9}{'Cost':<7}{'Path':<22}{'AltHop':<8}{'AltCost':<9}AltPath")
        print("-" * 78)
        for r in rows:
            print(f"{r['dest']:<6}{str(r['next_hop'] or '-'):<9}{fmt(r['cost']):<7}"
                  f"{'->'.join(r['path']) or '-':<22}{str(r['alt_next_hop'] or '-'):<8}"
                  f"{fmt(r['alt_cost']):<9}{'->'.join(r['alt_path']) or '-'}")


def print_dv(dv, rounds):
    print(f"\nDistance Vector converged in {rounds} round(s)")
    for n, row in dv.items():
        print(f"\nDV table for {n}")
        print(f"{'Dest':<6}{'Cost':<7}NextHop")
        for d, (c, nh) in row.items():
            if d != n:
                print(f"{d:<6}{fmt(c):<7}{nh or '-'}")


def export(tables, dv, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "routing_tables.json"), "w") as f:
        json.dump(tables, f, indent=2)
    with open(os.path.join(out_dir, "routing_tables.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source", "dest", "next_hop", "cost", "path",
                    "alt_next_hop", "alt_cost", "alt_path"])
        for src, rows in tables.items():
            for r in rows:
                w.writerow([src, r["dest"], r["next_hop"], r["cost"],
                            "->".join(r["path"]), r["alt_next_hop"],
                            r["alt_cost"], "->".join(r["alt_path"])])
    dv_json = {n: {d: {"cost": None if c == INF else c, "next_hop": nh}
                   for d, (c, nh) in row.items()} for n, row in dv.items()}
    with open(os.path.join(out_dir, "dv_tables.json"), "w") as f:
        json.dump(dv_json, f, indent=2)
    print(f"\nExported to {out_dir}/ (routing_tables.json/.csv, dv_tables.json)")


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description="NetPath routing module")
    ap.add_argument("topology", help="topology file (.json or edge-list .txt)")
    ap.add_argument("--source", help="source node for path query")
    ap.add_argument("--dest", help="destination node for path query")
    ap.add_argument("-k", type=int, default=3, help="number of paths for query")
    ap.add_argument("--fail", metavar="U-V", help="simulate failure of link U-V")
    ap.add_argument("--out-dir", help="export tables to this directory")
    args = ap.parse_args(argv)

    try:
        g = Graph.load(args.topology)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as e:
        sys.exit(f"Input error: {e}")

    if args.fail:
        try:
            u, v = args.fail.split("-")
            g.remove_edge(u, v)
            print(f"** Link {u}-{v} failed; recomputing routes **")
        except (ValueError, KeyError) as e:
            sys.exit(f"Bad --fail argument: {e}")

    tables = build_routing_tables(g)
    dv, rounds = distance_vector(g)

    print_tables(tables)
    print_dv(dv, rounds)
    print("\nDV matches Dijkstra:", verify_dv_matches_dijkstra(g, dv))

    if args.source and args.dest:
        try:
            paths = k_shortest_paths(g, args.source, args.dest, args.k)
        except KeyError as e:
            sys.exit(f"Unknown node: {e}")
        print(f"\nTop {args.k} paths {args.source} -> {args.dest}:")
        for i, (c, p) in enumerate(paths, 1):
            print(f"  {i}. cost={fmt(c)}  {' -> '.join(p)}")
        if not paths:
            print("  No path available.")

    if args.out_dir:
        export(tables, dv, args.out_dir)


if __name__ == "__main__":
    main()
