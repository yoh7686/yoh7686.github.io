from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import re
ROOT=Path(__file__).resolve().parent.parent
class Doc(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[];self.images=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='a' and 'href' in a:self.links.append(a['href'])
  if tag=='img':self.images.append(a)
docs={}
for path in ROOT.glob('*.html'):
 text=path.read_text();d=Doc();d.feed(text);docs[path.name]=d
 assert len(d.ids)==len(set(d.ids)),('duplicate IDs',path.name)
 for bad in ['mail.google.com','drive.google.com','docs.google.com','review-private','非公開照合','依頼元','掲載判定','実施未確認','スプレッドシート No.']:
  assert bad not in text,(path.name,bad)
 assert 'lang="ja"' in text and 'name="viewport"' in text
 assert all(x.get('alt') for x in d.images)
for name,d in docs.items():
 for u in d.links:
  p=urlsplit(u)
  if p.scheme or p.netloc:continue
  target=p.path.lstrip('/') or (name if p.fragment else 'index.html')
  if target.endswith('/'):continue # existing WebGL paths are preserved in the remote base tree
  assert (ROOT/target).exists(),(name,u)
  if p.fragment:assert unquote(p.fragment) in docs[target].ids,(name,u,'missing anchor')
print(f'PASS: {len(docs)} pages; internal routes and anchors; unique IDs; image alternatives; no private fields')
