# In Colab, run before this cell: !pip -q install google-cloud-vision
from google.colab import auth
auth.authenticate_user()
from google.cloud import vision
from pathlib import Path
import google.auth
PROJECT_ID='REPLACE_WITH_YOUR_PROJECT_ID'
if PROJECT_ID.startswith('REPLACE_'):
    raise ValueError('Set Google Cloud project ID and enable Vision API + billing')
creds,_=google.auth.default(
    scopes=['https://www.googleapis.com/auth/cloud-platform'],
    quota_project_id=PROJECT_ID,
)
client=vision.ImageAnnotatorClient(credentials=creds)
image_bytes=Path('circle_01.png').read_bytes()
response=client.label_detection(image=vision.Image(content=image_bytes))
if response.error.message:
    raise RuntimeError(response.error.message)
for label in response.label_annotations[:10]:
    print(label.description,round(label.score,3))
# score is per-label confidence, not accuracy