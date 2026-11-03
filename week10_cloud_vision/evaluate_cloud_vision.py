"""Actual Google Cloud Vision test evaluation; paid API calls may occur."""
import csv
from pathlib import Path
import google.auth
from google.cloud import vision
from sklearn.metrics import accuracy_score, confusion_matrix
PROJECT_ID = 'REPLACE_WITH_YOUR_PROJECT_ID'
if PROJECT_ID.startswith('REPLACE_'):
    raise ValueError('Set PROJECT_ID after activating Vision API and billing')
# Fix mapping using validation data BEFORE evaluating the held-out test set
CLASS_KEYWORDS = {
    'circle': ('circle','round'),
    'square': ('square','rectangle'),
    'triangle': ('triangle','triangular')
}
MIN_LABEL_SCORE=0.50
creds,_=google.auth.default(
    scopes=['https://www.googleapis.com/auth/cloud-platform'],
    quota_project_id=PROJECT_ID
)
client=vision.ImageAnnotatorClient(credentials=creds)
def predict(path):
    response=client.label_detection(image=vision.Image(content=path.read_bytes()))
    if response.error.message:
        raise RuntimeError(response.error.message)
    best='unknown'; best_score=0.0
    for item in response.label_annotations:
        desc=item.description.lower()
        for cls,terms in CLASS_KEYWORDS.items():
            if any(t in desc for t in terms) and item.score>=MIN_LABEL_SCORE and item.score>best_score:
                best,best_score=cls,item.score
    return best,best_score
with open('test.csv',newline='',encoding='utf8') as f:
    rows=list(csv.DictReader(f))
if not rows: raise ValueError('Empty test.csv')
records=[]
for row in rows:
    path=Path('week10_data')/row['path']
    predicted,score=predict(path)
    records.append({'path':row['path'],'true_label':row['true_label'],
                    'predicted_label':predicted,'matched_score':round(score,4)})
with open('vision_test_results.csv','w',newline='',encoding='utf8') as f:
    w=csv.DictWriter(f,fieldnames=list(records[0]))
    w.writeheader();w.writerows(records)
truth=[r['true_label'] for r in records]
pred=[r['predicted_label'] for r in records]
print('Real API accuracy:',accuracy_score(truth,pred))
print('Confusion matrix:',confusion_matrix(truth,pred,labels=[*CLASS_KEYWORDS,'unknown']))
print('Saved vision_test_results.csv')
# The synthetic shapes might not be recognized. Unknown counts as wrong.