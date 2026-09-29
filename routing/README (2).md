
# Routing Module

## Project
Computer Networks - NetPath: Adaptive Network Routing and Congestion
Monitoring System

## Description
This module computes the best paths between routers in a network
using both Dijkstra's algorithm and Distance Vector routing. It
generates routing tables with primary and backup routes, and can
recompute routes when link costs change (due to congestion) or when a
link fails.

## Features
- Computes shortest paths from any node using Dijkstra's algorithm
- Simulates Distance Vector routing (with split horizon and poisoned
  reverse) and verifies it matches Dijkstra's results
- Finds alternate (backup) paths using Yen's k-shortest paths
- Generates a full routing table per node: destination, next hop,
  cost, path, and backup route
- Reads network topology from JSON or a plain edge-list text file
- Simulates link failures and recomputes routes around them
- Exports routing tables to JSON and CSV


## Requirements
- Python 3.x (standard library only, no installs needed)

## How to Run
Open a terminal inside the project folder.

Run:

    python routing.py topology.json

To find paths between two specific routers:

    python routing.py topology.json --source A --dest F -k 3

To simulate a link failure:

    python routing.py topology.json --fail C-E

To export routing tables to files:

    python routing.py topology.json --out-dir out

To run the full pipeline with congestion data (routing + congestion +
adaptive rerouting) see `bridge.py` and `INTEGRATION_CONTRACT.md`.

## Algorithm
1. Load the network as a graph of routers (nodes) and links (edges)
   with costs.
2. Dijkstra: starting from the source, repeatedly pick the closest
   unvisited router and update its neighbors' costs, until every
   router has its shortest cost and path.
3. Distance Vector: each router starts knowing only its direct
   neighbors, then exchanges distance lists with them round by round
   until no router's table changes (convergence).
4. Alternate paths: find the next-best loopless paths so each route
   has a backup next hop.
5. Build a routing table per router: destination, next hop, cost,
   full path, and backup route.
6. On a link cost change or failure, recompute the tables so traffic
   reroutes automatically.

## Module Owner
Leela
