#!/usr/bin/env python3 

"""
Usage:

    $ ./main.py [city [count]]

For example,

    $ ./main.py Boston 123

will generate 123 images of intersections in Boston.

    $ ./main.py Boston

will default 100. 

    $ ./main.py

with NO arguments will default to Baltimore.
"""

import overpy
import numpy as np
import osmnx as ox
import json
import sys


if len(sys.argv) < 2:
    CITY_ARG = "Baltimore"
else:
    CITY_ARG = sys.argv[1]


if len(sys.argv) < 3:
    IMG_COUNT = 100
else:
    IMG_COUNT = sys.argv[2]


print("Finding interesting intersections in {}...".format(CITY_ARG))
TRAFFIC_SIGNAL_QUERY = """
[out:json]
[timeout:2500]
;
area["name"="[[CITY]]"]->.searchArea;
(
  node
    ["highway"="traffic_signals"]
    (area.searchArea);
  way
    ["highway"="traffic_signals"]
    (area.searchArea);
  relation
    ["highway"="traffic_signals"]
    (area.searchArea);
);
out;
>;
out skel qt;
""".replace('[[CITY]]', CITY_ARG)

api = overpy.Overpass()
response = api.query(TRAFFIC_SIGNAL_QUERY)
tlights = response.nodes

# First, get average, min, max distance:
X = np.array([[float(tl.lat), float(tl.lon)] for tl in tlights])

print("Calculating traffic-light distances...")
dists = np.ndarray((len(X), len(X)))
for i in range(len(X)):
    for j in range(len(X)):
        dists[i, j] = np.linalg.norm(X[i] - X[j])

# Postprocessing:
dists[dists < 0.0000001] = 99
potentials = dists < 0.02 # < ~100ft

res = [X[r[0]] for r in np.array(np.where(potentials > 0)).T]
_candidates = res
candidates = []
for c in _candidates:
    if tuple(c) not in candidates:
        candidates.append(tuple(c))
candidates = np.array(candidates)

# Then cluster:
print("Clustering...")
from sklearn.cluster import DBSCAN
dbs = DBSCAN(eps=0.001, min_samples=2).fit(candidates)

counts = dbs.labels_
# Intersections are centroids of lights:
complex_intersections = [[] for _ in range(np.max(dbs.labels_))]
for i in range(len(candidates)):
    if dbs.labels_[i] > -1:
        light = candidates[i]
        complex_intersections[dbs.labels_[i]-1].append(light)

complex_intersections = np.array([np.array(c) for c in complex_intersections])
complex_intersections = [[np.mean(c[:, 0]), np.mean(c[:, 1])] for c in complex_intersections]

def clean_name(s):
    quals = ['avenue', 'street', 'place', 'way', 'drive', 'boulevard', 'road']
    s = s.lower()
    for qual in quals:
        if s.endswith(" " + qual):
            return s[:-1 * (1 + len(qual))]
    return s

print("Generating images...")
fnames = []
ii = 0
for ci in complex_intersections[:IMG_COUNT]:
    gg = ox.graph_from_point(ci, distance=100, simplify=False, truncate_by_edge=True)
    rds = set([e[2].get('name') for e in gg.edges(data=True)])
    try:
        rds.remove(None)
    except:
        pass
    rds = [clean_name(r) for r in rds]
    if len(rds) > 1:
        rd_names = "{} & {}".format(", ".join(rds[:-1]), rds[-1])
    else:
        # self-intersect:
        rd_names = "{} & {}".format(rds[0], rds[0])
    
    fname = rds[-1] + str(np.random.randint(0, 1000))
    print("{}%".format(
        int(100 * ii / IMG_COUNT)
    ), end="\r")
    ii += 1
    fnames.append({ "name": fname, "roads": rd_names })
    
    ox.plot_graph(
        gg, 
        fig_height=3, fig_width=3, bgcolor="#55555500", 
        node_size=0, edge_linewidth=6, edge_color="#c0fefe",
        use_geom=True, 
        save=True, show=False, filename=fname
    )
    
print("Outputting JSON...")
with open('manifest.json', 'w') as fh:
    fh.write(json.dumps({"city": CITY_ARG, "images": fnames }))
