#!/usr/bin/env python3
"""OSM XML (api/0.6/map) -> compact scene JSON (local meters, origin = site center).

usage: build_data.py raw/map.osm config.json data/scene.json
"""
import json, math, sys, xml.etree.ElementTree as ET

osm, cfg_path, out = sys.argv[1:4]
cfg = json.load(open(cfg_path))
root = ET.parse(osm).getroot()
nodes, ways = {}, {}
for el in root:
    if el.tag == 'node':
        nodes[el.get('id')] = (float(el.get('lat')), float(el.get('lon')))
    elif el.tag == 'way':
        ways[el.get('id')] = ({t.get('k'): t.get('v') for t in el.findall('tag')},
                              [n.get('ref') for n in el.findall('nd')])

site_ids = [str(i) for i in cfg['siteWays']]
pts = [nodes[r] for i in site_ids for r in ways[i][1] if r in nodes]
lat0 = sum(p[0] for p in pts) / len(pts)
lon0 = sum(p[1] for p in pts) / len(pts)
KX = math.cos(math.radians(lat0)) * 111320.0
KZ = 110540.0

def xy(ref):
    la, lo = nodes[ref]
    return (round((lo - lon0) * KX, 1), round(-(la - lat0) * KZ, 1))

def ring(refs):
    r = [xy(n) for n in refs if n in nodes]
    if len(r) > 2 and r[0] == r[-1]:
        r = r[:-1]
    return r

def area(r):
    return sum(r[i][0] * r[(i + 1) % len(r)][1] - r[(i + 1) % len(r)][0] * r[i][1] for i in range(len(r))) / 2

def inside(p, r):
    x, y = p; c = False
    for i in range(len(r)):
        x1, y1 = r[i]; x2, y2 = r[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c

site_rings = [ring(ways[i][1]) for i in site_ids]
R = cfg.get('radius', 650)
buildings, roads, areas = [], [], []
ROADW = {'motorway': 22, 'trunk': 20, 'primary': 18, 'primary_link': 9, 'secondary': 14,
         'secondary_link': 8, 'tertiary': 11, 'residential': 7, 'service': 5, 'busway': 7,
         'pedestrian': 6, 'footway': 2.5, 'cycleway': 2.5, 'path': 2, 'steps': 2}
for wid, (t, refs) in ways.items():
    if wid in site_ids:
        continue
    r = ring(refs)
    if len(r) < 2:
        continue
    cx = sum(p[0] for p in r) / len(r); cz = sum(p[1] for p in r) / len(r)
    if math.hypot(cx, cz) > R:
        continue
    if 'building' in t and len(r) >= 3:
        a = area(r)
        if abs(a) < 20:
            continue
        if a < 0:  # make CCW in x/z screen sense consistent
            r = r[::-1]
        h = None
        try:
            h = float(t.get('height', '').replace('m', '').strip())
        except ValueError:
            pass
        lv = None
        try:
            lv = int(float(t.get('building:levels', '')))
        except ValueError:
            pass
        insite = any(inside((cx, cz), s) for s in site_rings)
        if h is None:
            h = (lv or (8 if insite else 5)) * (5.2 if insite else 3.4)
        if lv is None:
            lv = max(1, round(h / (5.2 if insite else 3.4)))
        lv = max(1, min(lv, 40))
        buildings.append({'id': int(wid), 'n': t.get('name', ''), 'h': round(h, 1), 'lv': lv,
                          's': 1 if insite else 0, 'p': r})
    elif 'highway' in t and t['highway'] in ROADW:
        roads.append({'w': ROADW[t['highway']], 'p': r if refs[0] != refs[-1] else r + [r[0]]})
    else:
        kind = None
        if t.get('natural') == 'water' or 'water' in t:
            kind = 'water'
        elif t.get('leisure') in ('park', 'garden') or t.get('landuse') in ('grass', 'forest') or t.get('natural') == 'wood':
            kind = 'green'
        elif t.get('leisure') == 'pitch':
            kind = 'pitch'
        if kind and len(r) >= 3:
            areas.append({'k': kind, 'p': r})

# drop outline polygons that contain another building's centroid (campus outlines)
def cen(r): return (sum(q[0] for q in r)/len(r), sum(q[1] for q in r)/len(r))
cont = {i for i, o in enumerate(buildings) for j, b in enumerate(buildings) if i != j and inside(cen(b['p']), o['p'])}
buildings = [b for i, b in enumerate(buildings) if i not in cont]

json.dump({'center': [lat0, lon0], 'radius': R, 'site': site_rings,
           'buildings': buildings, 'roads': roads, 'areas': areas},
          open(out, 'w'), ensure_ascii=False, separators=(',', ':'))
s = [b for b in buildings if b['s']]
print(f"buildings {len(buildings)} (site {len(s)}), roads {len(roads)}, areas {len(areas)}")
for b in s:
    print('  ', b['n'] or b['id'], b['h'], b['lv'])
