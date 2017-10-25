from aftershock_gms import *
from collections import OrderedDict
import csv
import json
import matplotlib.pyplot as plt
import numpy as np
import time
from tqdm import tqdm


# data prep
print('preparing data')
fault_geojson = '../data/puget_sound_ruptures.geojson'
with open(fault_geojson, 'r') as f:
    trace_dict = json.load(f)
    traces = trace_dict['features']

# study area
print('making sites')
sites_file = "../data/nw_washington_sites.csv"
lons, lats = np.loadtxt(sites_file, delimiter=',', unpack=True)
sites = SiteCollection([Site(location=Point(lon, lat), vs30=760.,
                             vs30measured=True, z1pt0=40., z2pt5=1.)
                        for lon, lat in zip(lons, lats)])

# mainshock ruptures
print('making ruptures')
mainshock_ruptures = {trace['properties']['event']: trace_to_rupture(trace)
                      for trace in tqdm(traces)}
mainshock_ruptures_file = "../data/mainshock_ruptures.csv"

print('calculating mainshock ground motions')
mainshock_gms = {k: ground_motion_from_rupture(rup, sites=sites)
                 for k, rup in tqdm(mainshock_ruptures.items())}
mainshock_gms_file = "../data/mainshock_gms.csv"

# aftershocks
n_days = 1000 # days after event
cutoff_mag = 4.5

print('making aftershock sequences')
aftershock_ruptures = {k: make_aftershock_rupture_sequence(rup, n_days,
                                                     min_return_mag=cutoff_mag)
                       for k, rup in tqdm(mainshock_ruptures.items())}
aftershock_ruptures_file = "../data/aftershock_ruptures.csv"

# ground motions in parallel
print('calculating aftershock ground motions')
for k in tqdm(aftershock_ruptures.keys()):
    calc_aftershock_gms(aftershock_ruptures[k], sites, n_jobs=-1, _joblib=False)
aftershock_gms_file = "../data/aftershock_gms.csv"
eid = 0
mid = 0

print('writing ruptures and ground motions')
with open(mainshock_gms_file, 'w') as mgfile, \
     open(mainshock_ruptures_file, 'w') as mrfile, \
     open(aftershock_gms_file, 'w') as agfile, \
     open(aftershock_ruptures_file, 'w') as arfile:
    frm = csv.writer(mrfile)
    fgm = csv.writer(mgfile)
    fra = csv.writer(arfile)
    fga = csv.writer(agfile)
    frm.writerow(["eid", "event", "mag", "lon", "lat", "depth"])
    fgm.writerow(["rlzi", "sid", "eid", "gmv_PGA"])
    fra.writerow(["eid", "aid", "mainshock", "mag", "lon", "lat", "depth"])
    fga.writerow(["rlzi", "sid", "eid", "gmv_PGA"])
    for k, rup in tqdm(mainshock_ruptures.items()):
        aid = 0
        frm.writerow([mid, k, rup.mag,
                     rup.hypocenter.longitude, rup.hypocenter.latitude,
                     rup.hypocenter.depth])
        fra.writerow([eid, aid, k, rup.mag,
                     rup.hypocenter.longitude, rup.hypocenter.latitude,
                     rup.hypocenter.depth])
        gmf = mainshock_gms[k]
        for (sid, _), gmv in np.ndenumerate(gmf[PGA()]):
            fgm.writerow([0, sid, mid, gmv])
            fga.writerow([0, sid, eid, gmv])
        eid += 1
        mid += 1
        aid += 1
        for i in aftershock_ruptures[k].keys():
            arup = aftershock_ruptures[k][i]
            fra.writerow([eid, aid, k, arup["Mw"],
                          arup["lon"], arup["lat"], arup["depth"]])
            agmf = arup["ground_motion"]
            for (sid, _), gmv in np.ndenumerate(agmf[PGA()]):
                fga.writerow([0, sid, eid, gmv])
            aid += 1
            eid += 1

print('wrote {:d} mainshock ground motion fields'.format(mid))
print('wrote {:d} aftershock ground motion fields'.format(eid))
