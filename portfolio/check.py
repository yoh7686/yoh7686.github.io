from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import re,runpy
ROOT=Path(__file__).resolve().parent.parent
class Doc(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[];self.images=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='a' and 'href' in a:self.links.append(a['href'])
  if tag=='img':self.images.append(a)
docs={}
for path in list(ROOT.glob('*.html'))+list((ROOT/'activities').glob('*.html')):
 text=path.read_text();d=Doc();d.feed(text);docs[str(path.relative_to(ROOT))]=d
 assert len(d.ids)==len(set(d.ids)),('duplicate IDs',path.name)
 for bad in ['mail.google.com','drive.google.com','docs.google.com','review-private','非公開照合','依頼元','掲載判定','実施未確認','スプレッドシート No.','会社での制作','実施状況確認中','金曜5限','event-sheet-0541','event-sheet-0534']:
  assert bad not in text,(path.name,bad)
 assert 'lang="ja"' in text and 'name="viewport"' in text
 assert all(x.get('alt') for x in d.images)
for name,d in docs.items():
 for u in d.links:
  p=urlsplit(u)
  if p.scheme or p.netloc:continue
  target=p.path.lstrip('/') or (name if p.fragment else 'index.html')
  assert (ROOT/target).exists(),(name,u)
  if p.fragment:assert unquote(p.fragment) in docs[target].ids,(name,u,'missing anchor')
# Every source record has exactly one year-page entry; no planned record is exported.
s=(ROOT/'portfolio/content/activities.md').read_text();ids=re.findall(r'^- id: (.+)$',s,re.M)
assert len(ids)==597
rendered=[i for name,d in docs.items() if name.startswith('activities/') for i in d.ids if i.startswith('event-')]
assert sorted(ids)==sorted(rendered)
assert not re.search(r'^- status: 予定$',s,re.M)
for dt in re.findall(r'^- date: (\d{4}-\d{2}-\d{2})$',s,re.M):assert dt<='2026-11-07'
v=(ROOT/'portfolio/content/videos.md').read_text()
assert len(re.findall(r'^- published_at: ',v,re.M))==31
assert len(re.findall(r'^- date: \d{4}-\d{2}-\d{2}$',v,re.M))==31
home=(ROOT/'index.html').read_text()
for required in ['狭霧の國','魔人と失われた王国','NA:I','The Bubble Diver','Qxb_vffcn0A','F-SMEYVXOvU','シニア・アドボケイト','特任准教授','エンタテインメント創造研究教育センター','profile.jpg']:assert required in home,required
print(f'PASS: {len(docs)} pages; routes and anchors; 597 activity records exactly once; no planned or excluded project entries; 31 video dates; selected works and affiliations')

# Every research record needs a usable destination; book covers retain their own links.
for block in (ROOT/'portfolio/content/research.md').read_text().split('\n## ')[1:]:
 fields=dict(re.findall(r'^- ([a-z_]+): (.*)$',block,re.M))
 assert fields.get('url','').startswith('https://'),fields.get('id')
 assert not re.search(r'[\s（）]',fields['url']),fields['url']
 assert fields['url'] in docs['research.html'].links,fields['id']
for block in (ROOT/'portfolio/content/works.md').read_text().split('\n## ')[1:]:
 fields=dict(re.findall(r'^- ([a-z_]+): (.*)$',block,re.M))
 if fields.get('id') in ['work-unityroom-magikaruta','work-unityroom-ezkaruta']:
  assert fields['category']=='研究作品'
 assert fields.get('source_label')!='本人の公開業績表（展示・イベント）',fields.get('id')
 if fields.get('video_url'):assert fields['video_url'] in docs['works.html'].links
print('PASS: research destinations, book links, research work categories and video links')

assert "代表作" not in home
assert "StratoJump" in home
