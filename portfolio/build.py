#!/usr/bin/env python3
"""Build the portfolio from public Markdown. Python 3.10+, standard library only."""
from pathlib import Path
from html import escape
from collections import defaultdict
import re, json
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parent.parent
CONTENT=ROOT/'portfolio/content'
BASE='https://yoh7686.github.io'
def esc(s):return escape(str(s),quote=True)
def read(name):
 out=[]
 for block in re.split(r'^## ',(CONTENT/(name+'.md')).read_text(encoding='utf-8'),flags=re.M)[1:]:
  d=dict(re.findall(r'^- ([a-z_]+): (.*)$',block,re.M));d['title']=block.splitlines()[0];out.append(d)
 return out
def date(d):return d.get('date','').replace('未確認','').replace('不明','')
def year(d):
 m=re.match(r'(\d{4})',date(d));return m[1] if m else '年不明'
def order(items):
 def key(d):
  stamp=d.get('published_at','')
  return (date(d),datetime.fromisoformat(stamp).astimezone(timezone.utc).isoformat() if stamp else '')
 return sorted(items,key=key,reverse=True)
def link(url,label,cls=''):
 if not (url.startswith(('https://','http://','/','#')) or re.match(r'^[a-z]+\.html',url)):raise ValueError('Unsafe link '+url)
 return f'<a href="{esc(url)}"'+(f' class="{esc(cls)}"' if cls else '')+'>'+label+'</a>'
def tag(kind):return '<span class="badge">'+esc(kind)+'</span>'
NAV=[('profile','プロフィール'),('research','研究・著作'),('activities','活動記録'),('works','作品'),('videos','動画'),('media','メディア掲載')]
P=read('profile')[0];A=order(read('activities'));M=order(read('media'));V=order(read('videos'));R=order(read('research'));W=order(read('works'))
def page(name,title,body,intro='',filters=False):
 nav=''.join(f'<a href="/{key}.html"'+(' aria-current="page"' if name==key or name.startswith(key+'/') else '')+'>'+label+'</a>' for key,label in NAV)
 head='' if name=='index' else f'<div class="breadcrumb"><a href="/">ホーム</a> <span aria-hidden="true"> / </span> {esc(title)}</div><header class="page-header"><div class="page-title-en">{name.split("/")[0].upper()}</div><h1>{esc(title)}</h1>'+(f'<p>{esc(intro)}</p>' if intro else '')+'</header>'
 desc='𥱋瀨洋平（Yohei Yanase）の研究、著作、ゲーム制作、講演・教育活動、動画、メディア掲載の記録。'
 html=f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} | Yohei Yanase</title><meta name="description" content="{esc(desc)}"><meta name="theme-color" content="#165e57"><link rel="canonical" href="{BASE}/{' ' if name=='index' else name+'.html'}"><meta property="og:title" content="{esc(title)} | Yohei Yanase"><meta property="og:type" content="website"><meta property="og:description" content="{esc(desc)}"><link rel="icon" href="/portfolio/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/portfolio/assets/site.css"><script defer src="/portfolio/assets/site.js"></script></head>
<body><a class="skip" href="#main">本文へ移動</a><header class="header"><div class="wrap header-inner"><a class="brand" href="/">Yohei Yanase<span> /</span></a><button class="menu-toggle" aria-controls="navigation" aria-expanded="false" type="button">メニュー</button><nav class="nav" id="navigation" aria-label="メインナビゲーション">{nav}</nav></div></header><main id="main" class="wrap">{head}<div class="page-content">{body}</div></main><div class="wrap"><footer class="footer"><span>© Yohei Yanase</span><nav aria-label="フッター"><a href="/profile.html">プロフィール</a><a href="https://github.com/yoh7686">GitHub ↗</a><a href="/profile.html#contact">Contact</a><a href="#main">ページ上部へ ↑</a></nav></footer></div></body></html>'''
 html=html.replace(BASE+'/ ',BASE+'/')
 (ROOT/(name+'.html')).parent.mkdir(parents=True,exist_ok=True)
 (ROOT/(name+'.html')).write_text(html,encoding='utf-8')
def section_head(title,url,label='一覧を見る'):
 return '<div class="section-head"><h2>'+esc(title)+'</h2>'+link(url,esc(label)+' <span aria-hidden="true">→</span>')+'</div>'
def groups(items):
 out=defaultdict(list)
 for r in items:out[year(r)].append(r)
 return out
def yearnav(items):return '<nav class="archive-links" aria-label="年別一覧">'+''.join(link('#year-'+y,esc(y)+('年' if y.isdigit() else '')) for y in groups(items))+'</nav>'
def filterbar(items,types=False):
 ys=groups(items); options=''.join(f'<option value="{esc(y)}">{esc(y)}</option>' for y in ys)
 ks=sorted(set(x.get('kind','') for x in items if x.get('kind')))
 types_html='<label>種別<select id="kind"><option value="">すべて</option>'+''.join(f'<option>{esc(k)}</option>' for k in ks)+'</select></label>' if types else ''
 return '<div class="filter"><label>キーワード検索<input id="query" type="search" placeholder="タイトル・媒体・活動名" autocomplete="off"></label><label>年<select id="year"><option value="">すべての年</option>'+options+'</select></label>'+types_html+'</div><p id="result-count" class="result-count" role="status" aria-live="polite">'+str(len(items))+'件を表示</p>'
def attr(r):return f'id="{esc(r["id"])}" data-entry data-year="{esc(year(r))}" data-kind="{esc(r.get("kind",""))}"'
def empty():return '<p id="empty" class="empty" hidden>該当する項目がありません。検索条件を変更してください。</p>'
def yearly(items,render):
 return ''.join(f'<section class="year-group" id="year-{esc(y)}" data-group><h2 class="year-heading">{esc(y)}'+('年' if y.isdigit() else '')+'</h2>'+''.join(render(r) for r in recs)+'</section>' for y,recs in groups(items).items())
def media_entry(r):
 return f'<article class="entry" {attr(r)}><div class="date">{esc(date(r) or "公開日不明")}</div><div class="publisher">{esc(r["publisher"])}<br>{tag(r["kind"])}</div><div class="entry-body"><h3>{link(r["url"],esc(r["title"])+" <span class=external aria-label=外部サイト>↗</span>")}</h3></div></article>'
def activity_url(r):return '/activities/'+(year(r) if year(r).isdigit() else 'undated')+'.html#'+r['id']
def activity_entry(r):
 sub=r.get('subtitle','')
 details=(f'<p>{esc(sub)}</p>' if sub and sub!=r['title'] else '')
 if r.get('note'):details+='<p class="record-note">'+esc(r['note'])+'</p>'
 return f'<article class="entry" {attr(r)}><div class="date">{esc(date(r) or "日付不明")}</div><div class="publisher">{tag(r["kind"])}</div><div class="entry-body"><h3>{esc(r["title"])}</h3>{details}</div></article>'
def video_card(r):
 return f'<article class="card" {attr(r)}><a class="thumb" href="{esc(r["url"])}" aria-label="{esc(r["title"])}をYouTubeで見る"><img src="https://i.ytimg.com/vi/{esc(r["youtube"])}/hqdefault.jpg" alt="{esc(r["title"])}" width="480" height="270" loading="lazy"><span class="play" aria-hidden="true">▶</span></a><div class="meta"><span>VIDEO / YOUTUBE</span><span>{esc(date(r))}</span></div><h3>{link(r["url"],esc(r["title"]))}</h3></article>'
def work_links(r):
 links=[]
 if r.get('url'):links.append(link(r['url'],esc(r.get('source_label','作品・資料'))+' ↗','source-link'))
 if r.get('video_url'):links.append(link(r['video_url'],'動画を見る ↗','source-link'))
 return '<div class="resource-links">'+''.join(links)+'</div>' if links else ''
FEATURES=[r for r in W if r.get('featured')=='true']
def work_card(r,home=False):
 dest='/works.html#'+r['id'] if home else r.get('url','')
 image=f'<img src="{esc(r["image"])}" alt="{esc(r["title"])}" width="480" height="270" loading="lazy">' if r.get('image') else '<span class="work-image-missing">'+esc(r['title'])+'</span>'
 thumb_class='thumb square-thumb' if r.get('url','').startswith('https://unityroom.com/') else 'thumb'
 if r.get('image_fit')=='contain':thumb_class+=' contain-thumb'
 visual=link(dest,image,thumb_class) if dest else '<div class="'+thumb_class+'">'+image+'</div>'
 title=link(dest,esc(r['title'])) if dest else esc(r['title'])
 return '<article class="card"'+('' if home else f' id="{r["id"]}"')+'>'+visual+'<div class="meta"><span>'+esc(r['category'])+'</span><span>'+esc(date(r))+'</span></div><h3>'+title+'</h3><p>'+esc(r.get('description',''))+'</p>'+('' if home or not r.get('credit') else '<p class="caption">'+esc(r['credit'])+'</p>')+('' if home else work_links(r))+'</article>'
# One combined news stream, linking to the relevant archive entries.
news=[]
for r in M:
 if not date(r):continue
 news.append(dict(id='news-'+r['id'],date=date(r),kind='メディア',title=r['publisher']+'に'+('聞き手として参加したインタビュー' if '聞き手' in r['kind'] else ('寄稿' if '寄稿' in r['kind'] else ('登壇レポート' if any(x in r['kind'] for x in ['講演','パネル']) else ('インタビュー・対談' if any(x in r['kind'] for x in ['インタビュー','対談','座談会']) else '活動紹介記事'))))+'が掲載されました。「'+r['title']+'」',url='/media.html#'+r['id']))
for r in A:
 if not date(r) or r.get('omit_news')=='true' or r.get('note'):continue
 role=r['kind']
 if any(x in role for x in ['講義','授業','教育','レクチャー','講習','講座','勉強会講師']):verb='で講義を行いました'
 elif 'ハンズオン' in role or 'ワークショップ' in role or 'WS' in role:verb='でワークショップ'+('をサポートしました' if any(x in role for x in ['手伝い','サポート']) else 'を行いました')
 elif 'モデレーター' in role:verb='でモデレーターを務めました'
 elif '座長' in role:verb='で座長を務めました'
 elif '審査' in role and 'メンター' in role:verb='で審査員・メンターを務めました'
 elif '審査' in role:verb='で審査を行いました'
 elif '講評' in role:verb='で作品講評を行いました'
 elif 'メンター' in role:verb='でメンターを務めました'
 elif 'アドバイザー' in role:verb='でアドバイザーを務めました'
 elif '展示' in role or 'デモ' in role:verb='で研究デモを紹介しました'
 elif '出演' in role:verb='に出演しました'
 elif '対談' in role or 'クロストーク' in role:verb='で対談しました'
 elif 'パネル' in role or 'シンポジウム' in role:verb='に登壇しました'
 elif '発表' in role or role=='LT' or role.startswith('LT('):verb='で発表しました'
 elif any(x in role for x in ['講演','セミナー','トーク','プレゼン','セッション','登壇']):verb='で講演しました'
 else:verb='で'+role+'を担当しました'
 name=r['title']
 if verb=='で講義を行いました':name=re.sub(r'[ 　]+(?:ゲスト講義|特別講義|集中講義|講義|授業|講習会|講座)$','',name)
 elif verb=='で講演しました':name=re.sub(r'[ 　]+(?:招待講演|基調講演|ゲスト講演|講演)$','',name)
 news.append(dict(id='news-'+r['id'],date=date(r),kind='活動',title=name+verb+'。',url=activity_url(r)))
for r in V:
 if date(r):news.append(dict(id='news-'+r['id'],date=date(r),kind='動画',title='動画「'+r['title']+'」を公開しました。',url='/videos.html#'+r['id']))
news=order(news)
def news_rows(items,compact=False):
 rows=[]
 for r in items:
  text=r['title'].split('。「')[0]+'。' if compact and '。「' in r['title'] else r['title']
  rows.append(f'<li class="news-row" {attr(r)}><span class="date">{esc(date(r).replace("-","."))}</span>{tag(r["kind"])}{link(r["url"],esc(text))}</li>')
 return '<ul class="news-list">'+''.join(rows)+'</ul>'
def roles():
 return '<div class="affiliations"><div><span>'+esc(P['company'])+'</span><strong>'+esc(P['role'])+'</strong></div><div><span>'+esc(P['university'])+'<br>'+esc(P['department'])+'</span><strong>'+esc(P['university_role'])+'</strong></div></div>'
summary=f'<div class="profile-summary"><div class="profile-heading"><img class="portrait" src="{esc(P["portrait"])}" alt="𥱋瀨洋平のプロフィール写真" width="112" height="112"><div><h1>Yohei Yanase</h1><p class="name-ja">{esc(P["title"])}</p></div></div>{roles()}<p class="fields">{esc(P["fields"])}</p><a class="subtle-link" href="/profile.html">プロフィール・略歴を見る →</a></div>'
body='<div class="intro">'+summary+'<section>'+section_head('News','/news.html','すべての活動')+news_rows(news[:8],True)+'</section></div>'
body+='<section class="section">'+section_head('作品','/works.html','すべての作品')
for cat in ['商業作品','個人制作','研究作品']:
 body+='<div class="home-work-group"><h3 class="work-category">'+cat+'</h3><div class="card-grid featured-grid">'+''.join(work_card(r,True) for r in FEATURES if r['category']==cat)+'</div></div>'
body+='</section>'
body+='<section class="section">'+section_head('動画','/videos.html')+'<div class="card-grid featured-grid">'+''.join(video_card(r) for r in V if r.get('featured')=='true')+'</div></section>'
body+='<div class="bottom-grid"><section class="section">'+section_head('メディア掲載','/media.html')+'<ul class="media-preview">'+''.join('<li><small>'+esc(date(r))+' / '+esc(r['publisher'])+' / '+esc(r['kind'])+'</small>'+link('/media.html#'+r['id'],esc(r['title']))+'</li>' for r in M[:3])+'</ul></section><section class="section">'+section_head('活動記録','/activities.html')+'<p class="muted">講演・講義・メンター・審査員の活動を年別に掲載しています。</p><nav class="year-links" aria-label="活動記録の年">'+''.join(link('/activities/'+(y if y.isdigit() else 'undated')+'.html',esc(y)) for y in list(groups(A))[:5])+'</nav>'+link('/research.html','研究・著作一覧 →')+'</section></div>'
page('index','𥱋瀨 洋平',body)
page('media','メディア掲載',yearnav(M)+filterbar(M,True)+yearly(M,media_entry)+empty(),'インタビュー、活動・研究紹介、講演レポート、寄稿など。記事の掲載年ごとにまとめています。')
activity_groups=groups(A)
activity_years=list(activity_groups)
activity_intro='講演・講義・メンター・審査員などの活動を年ごとに掲載しています。予定は含めていません。'
year_cards='<div class="activity-years">'+''.join('<a class="year-card" id="year-'+y+'" href="/activities/'+(y if y.isdigit() else 'undated')+'.html"><strong>'+esc(y)+('年' if y.isdigit() else '')+'</strong><span>'+str(len(rs))+'件の記録 →</span></a>' for y,rs in activity_groups.items())+'</div>'
routes={r['id']:activity_url(r) for r in A}
page('activities','活動記録',year_cards+'<script type="application/json" id="activity-routes">'+json.dumps(routes,ensure_ascii=False)+'</script>',activity_intro)
for i,(y,rs) in enumerate(activity_groups.items()):
 slug=y if y.isdigit() else 'undated'
 nav='<nav class="archive-links" aria-label="活動記録の年">'+link('/activities.html','年別一覧')+''.join(link('/activities/'+(a if a.isdigit() else 'undated')+'.html',esc(a)) for a in activity_years)+'</nav>'
 details='<p class="muted">原稿に基づく活動記録です。同一活動の可能性がある項目には注記しています。</p>' if any(r.get('note') for r in rs) else ''
 page('activities/'+slug,('活動記録 / '+y+'年' if y.isdigit() else '活動記録 / 年不明'),nav+details+filterbar(rs)+yearly(rs,activity_entry)+empty(),activity_intro)
page('videos','動画',yearnav(V)+filterbar(V)+''.join(f'<section class="year-group" data-group id="year-{esc(y)}"><h2 class="year-heading">{esc(y)}'+('年' if y.isdigit() else '')+'</h2><div class="card-grid video-grid">'+''.join(video_card(r) for r in vs)+'</div></section>' for y,vs in groups(V).items())+empty(),'Unityの使い方、ゲーム制作、クリエイターへのインタビューなど。公開日が新しい順に掲載しています。公開日は日本時間で表示しています。')
page('news','News',yearnav(news)+filterbar(news,True)+yearly(news,lambda r:news_rows([r]))+empty(),'動画公開、登壇、メディア掲載など、活動全体のお知らせ。各項目から詳しい記録に進めます。')
body='<nav class="archive-links" aria-label="研究・著作の分類">'
cats=list(dict.fromkeys(r['category'] for r in R))
body+=''.join(link('#research-'+str(i),esc(cat)) for i,cat in enumerate(cats))+'</nav>'
for i,cat in enumerate(cats):
 body+=f'<section class="year-group" id="research-{i}"><h2 class="year-heading">{esc(cat)}</h2>'
 for n,r in enumerate([r for r in R if r['category']==cat],1):
  book=r['category']=='著書，編書，翻訳書' or bool(r.get('book_title'))
  visual=link(r['url'],f'<img src="{esc(r["image"])}" alt="{esc(r.get("book_title",r["title"]))}の書影" loading="lazy" width="120" height="175">','book-cover') if book and r.get('image') else f'<span class="number">{n:02}</span>'
  sources=link(r['url'],esc(r.get('source_label','出版社の書籍ページ' if book else '資料・掲載先'))+' ↗','source-link') if r.get('url') else '<span class="record-note">掲載先を確認中</span>'
  if r.get('publisher_url'):sources+=link(r['publisher_url'],'出版社サイト ↗','source-link')
  body+=f'<article class="entry research-entry'+(' book-entry' if book else '')+f'" id="{esc(r["id"])}">'+visual+f'<div class="entry-body"><h3>{esc(r["title"])}</h3><div class="resource-links">'+sources+'</div>'+('<p class="caption">'+esc(r['image_credit'])+'</p>' if r.get('image_credit') else '')+'</div></article>'
 body+='</section>'
body+='<p class="notice">書誌情報・活動年は業績原簿に基づきます。委員・アドバイザー歴の開始年は、現在の在任を示すものではありません。</p>'
page('research','研究・著作',body,'論文、書籍、研究発表、展示、受賞などの記録。')
body='<nav class="archive-links" aria-label="作品の分類">'+''.join(link('#works-'+str(i),c) for i,c in enumerate(['商業作品','個人制作','研究作品']))+'</nav>'
for i,cat in enumerate(['商業作品','個人制作','研究作品']):
 body+=f'<section class="works-group" id="works-{i}"><h2 class="year-heading">{cat}</h2><div class="card-grid">'+''.join(work_card(r) for r in W if r['category']==cat)+'</div></section>'
body+='<p class="muted">各分類内で新しい順に掲載しています。画像は作品の紹介動画・公開ページのサムネイルです。作品・画像の権利は各権利者に帰属します。</p>'
page('works','作品',body,'商業作品、個人制作、研究作品。商業作品には担当を記載しています。')
other_roles=''.join('<li>'+esc(r.strip())+'</li>' for r in P.get('other_roles','').split('|') if r.strip())
body=f'<div class="prose"><div class="profile-heading"><img class="portrait" src="{esc(P["portrait"])}" alt="𥱋瀨洋平のプロフィール写真" width="112" height="112"><div><h2 class="profile-name">{esc(P["title"])}</h2><p>Yohei Yanase</p></div></div><h2>所属・役職</h2>{roles()}<ul class="other-roles">{other_roles}</ul><h2>略歴</h2><p>{esc(P["biography"])}</p><p>商業作品では「魔人と失われた王国」のゲームデザイン、「狭霧の國」の脚本協力などを担当。個人制作と並行して、ヒューマン・コンピュータ・インタラクション（HCI）、ゲームデザイン、エンタテインメントコンピューティングの研究に取り組む。</p><p>2017年、制作に参加した「Unlimited Corridor」が第20回文化庁メディア芸術祭エンターテインメント部門優秀賞を受賞。</p><h2>研究・教育活動</h2><p>{esc(P["university"])}{esc(P["department"])}{esc(P["university_role"])}。ゲーム開発・ナラティブデザインに関する教育・研究に従事。講演・講義のほか、メンター、審査員としての活動を行っている。</p><h2>表記について</h2><p>氏名の文字が正しく表示されない場合は「簗瀬 洋平」をお使いください。</p><h2 id="contact">Contact / Links</h2><div class="profile-links">{link(P["github"],"GitHub ↗")}{link("https://learning.unity3d.jp/speaker/yohei-yanase/","Unity Learning Materials ↗")}{link(P["university_source"],"電気通信大学 CEREC ↗")}</div><p class="muted">お問い合わせ窓口は準備中です。</p></div>'
page('profile','プロフィール',body)
page('404','ページが見つかりません','<p>URLが変更されたか、ページが存在しません。</p><p><a href="/">トップページへ戻る →</a></p>')
(ROOT/'portfolio/assets/favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="5" fill="#165e57"/><path d="M8 8l8 10 8-10M16 18v8" fill="none" stroke="#fff" stroke-width="3"/></svg>')
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+BASE+('/' if n=='index' else '/'+n+'.html')+'</loc></url>' for n in ['index','profile','research','activities','works','videos','media','news']+['activities/'+(y if y.isdigit() else 'undated') for y in activity_years])+'</urlset>')
print(f'Built: {len(A)} activities, {len(M)} media, {len(V)} videos, {len(R)} research records, {len(W)} works')
