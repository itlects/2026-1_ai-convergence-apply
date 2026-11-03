import csv,random
from collections import defaultdict,Counter
from sklearn.metrics import accuracy_score,confusion_matrix
rows=list(csv.DictReader(open('labels.csv',encoding='utf-8')))
groups=defaultdict(list)
for r in rows: groups[r['true_label']].append(r)
rng=random.Random(42)
parts={'train':[],'val':[],'test':[]}
for label,items in sorted(groups.items()):
 items=items.copy();rng.shuffle(items)
 n=len(items);nt=int(n*.7);nv=int(n*.15)
 parts['train']+=items[:nt]
 parts['val']+=items[nt:nt+nv]
 parts['test']+=items[nt+nv:]
for name,rs in parts.items():
 print(name,len(rs),dict(Counter(r['true_label'] for r in rs)))
 with open(name+'.csv','w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=['path','true_label'])
  w.writeheader();w.writerows(rs)
assert len({r['path'] for part in parts.values() for r in part})==len(rows)
y_true=[r['true_label'] for r in parts['test']]
y_pred=y_true.copy()
if len(y_pred)>2:
 y_pred[2]='square' if y_true[2]!='square' else 'circle'
print('OFFLINE DEMO accuracy:',accuracy_score(y_true,y_pred))
print(confusion_matrix(y_true,y_pred,labels=['circle','square','triangle']))
# DEMO PREDICTIONS ARE NOT GOOGLE VISION RESULTS