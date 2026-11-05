import gzip,json,math,statistics,unittest
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'frontend/public/data'
def load(file):return json.loads(file.read_text(encoding='utf-8'))
def cube(year):
 with gzip.open(DATA/f'defunciones-{year}.json.gz','rt',encoding='utf-8') as f:return json.load(f)
class LabTests(unittest.TestCase):
 def test_all_full_periods_and_clusters(self):
  base={d['id']:d for d in load(DATA/'index.json')['datasets'] if not d['partial']}
  idx=load(DATA/'lab/index.json')
  self.assertEqual(set(base),{d['id'] for d in idx['datasets']})
  for id,d in base.items():
   m=load(DATA/'lab'/f'{id}.json')
   self.assertEqual(m['sha256'],d['sha256'])
   for group in m['clusters']:
    self.assertEqual(len(group['groups']),m['entities'])
    self.assertEqual(set(group['groups'].values()),set(range(1,group['k']+1)))
    self.assertTrue(-1<=group['silhouette']<=1 and 0<=group['stability']<=1)
 def test_dendrogram_reconstructs_every_published_cut(self):
  for d in load(DATA/'lab/index.json')['datasets']:
   model=load(DATA/'lab'/f"{d['id']}.json")
   tree=model['dendrogram']
   labels=tree['labels']; n=len(labels)
   self.assertEqual(len(set(labels)),n)
   self.assertEqual(sorted(tree['order']),list(range(1,n+1)))
   self.assertEqual(len(tree['merge']),n-1)
   self.assertEqual(sorted(tree['height']),tree['height'])
   members={-i:{label} for i,label in enumerate(labels,1)}
   active=set(members)
   cuts={group['k']:group['groups'] for group in model['clusters']}
   for i,(a,b) in enumerate(tree['merge'],1):
    self.assertIn(a,active); self.assertIn(b,active);self.assertNotEqual(a,b)
    members[i]=members[a]|members[b]
    active.difference_update((a,b));active.add(i)
    if len(active) in cuts:
     groups=cuts[len(active)]
     expected={frozenset(k for k,v in groups.items() if v==g) for g in set(groups.values())}
     self.assertEqual({frozenset(members[k]) for k in active},expected,d['id'])
 def test_mds_reconstructs_distances_of_the_clustering_input(self):
  import numpy as np
  model=load(DATA/'lab/defunciones-2024.json')
  points=model['mds']['points']
  self.assertEqual({p['state'] for p in points},set(model['dendrogram']['labels']))
  d=cube(2024);counts=Counter();totals=Counter()
  for st,sex,age,month,ci,n in d['rows']:
   state=d['states'][st];totals[state]+=n
   counts[state,d['causes'][ci]]+=n
  x=[]
  for p in points:
   state=p['state'];v=[counts[state,c] for c in model['cluster_codes']]
   x.append(np.sqrt(np.array(v+[totals[state]-sum(v)])/totals[state]))
  x=np.array(x);y=np.array([[p['x'],p['y']] for p in points])
  distances=lambda m:np.linalg.norm(m[:,None,:]-m[None,:,:],axis=2)
  dx,dy=distances(x),distances(y)
  self.assertTrue(np.all(dy<=dx+1e-8))
  self.assertAlmostEqual(model['mds']['distortion'],np.linalg.norm(dx-dy)/np.linalg.norm(dx),places=8)
  self.assertAlmostEqual(model['mds']['retained'],np.sum(y**2)/np.sum((x-x.mean(axis=0))**2),places=8)
 def test_moran_matches_direct_state_totals(self):
  d=cube(2024);totals=Counter();cases=Counter()
  for st,sex,age,month,ci,n in d['rows']:
   k=d['states'][st];totals[k]+=n
   if d['causes'][ci]=='E11':cases[k]+=n
  valid={str(i).zfill(2) for i in range(1,33) if totals[str(i).zfill(2)]>=1000}
  edges=[(a,b) for a,b,_ in load(ROOT/'data/silver/lab/neighbors.json')['edges'] if a in valid and b in valid]
  nodes={x for edge in edges for x in edge}
  ratios={k:cases[k]/totals[k] for k in nodes};mean=statistics.mean(ratios.values())
  z={k:v-mean for k,v in ratios.items()}
  expected=len(nodes)/len(edges)*sum(z[a]*z[b] for a,b in edges)/sum(v*v for v in z.values())
  observed=load(DATA/'lab/defunciones-2024.json')['moran']['E11']
  self.assertAlmostEqual(observed['queen'],expected,places=8)
  self.assertEqual(observed['n'],len(nodes))
 def test_january_uses_only_prior_same_month(self):
  p=[]
  for y in range(2020,2025):
   d=cube(y);n=den=0
   for _,_,_,month,ci,c in d['rows']:
    if month==1:
     den+=c
     if d['causes'][ci]=='E11':n+=c
   p.append(n/den)
  row=next(r for r in load(DATA/'lab/defunciones-2024.json')['anomalies']['E11'] if r['month']==1)
  self.assertEqual(row['baseline'],'2020, 2021, 2022, 2023')
  self.assertAlmostEqual(row['share'],p[-1],places=8)
  self.assertAlmostEqual(row['typical'],statistics.median(p[:-1]),places=8)
  self.assertEqual(row['flag'],'above' if p[-1]>max(p[:-1]) else 'below' if p[-1]<min(p[:-1]) else 'inside')
if __name__=='__main__':unittest.main()
