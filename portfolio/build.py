#!/usr/bin/env python3
"""Build the portfolio from public Markdown. Python 3.10+, standard library only."""
from pathlib import Path
from html import escape
from collections import defaultdict
import re
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
def order(items):return sorted(items,key=lambda d:date(d),reverse=True)
def link(url,label,cls=''):
 if not (url.startswith(('https://','http://','/','#')) or re.match(r'^[a-z]+\.html',url)):raise ValueError('Unsafe link '+url)
 return f'<a href="{esc(url)}"'+(f' class="{esc(cls)}"' if cls else '')+'>'+label+'</a>'
def tag(kind):return '<span class="badge">'+esc(kind)+'</span>'
NAV=[('profile','プロフィール'),('research','研究・著作'),('activities','活動記録'),('works','作品'),('videos','動画'),('media','メディア掲載')]
P=read('profile')[0];A=order(read('activities'));M=order(read('media'));V=order(read('videos'));R=read('research');W=read('works')
def page(name,title,body,intro='',filters=False):
 nav=''.join(f'<a href="/{key}.html"'+(' aria-current="page"' if name==key else '')+'>'+label+'</a>' for key,label in NAV)
 head='' if name=='index' else f'<div class="breadcrumb"><a href="/">ホーム</a> <span aria-hidden="true"> / </span> {esc(title)}</div><header class="page-header"><div class="page-title-en">{name.upper()}</div><h1>{esc(title)}</h1>'+(f'<p>{esc(intro)}</p>' if intro else '')+'</header>'
 desc='𥱋瀨洋平（Yohei Yanase）の研究、著作、ゲーム制作、講演・教育活動、動画、メディア掲載の記録。'
 html=f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} | Yohei Yanase</title><meta name="description" content="{esc(desc)}"><meta name="theme-color" content="#165e57"><link rel="canonical" href="{BASE}/{' ' if name=='index' else name+'.html'}"><meta property="og:title" content="{esc(title)} | Yohei Yanase"><meta property="og:type" content="website"><meta property="og:description" content="{esc(desc)}"><link rel="icon" href="/portfolio/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/portfolio/assets/site.css"><script defer src="/portfolio/assets/site.js"></script></head>
<body><a class="skip" href="#main">本文へ移動</a><header class="header"><div class="wrap header-inner"><a class="brand" href="/">Yohei Yanase<span> /</span></a><button class="menu-toggle" aria-controls="navigation" aria-expanded="false" type="button">メニュー</button><nav class="nav" id="navigation" aria-label="メインナビゲーション">{nav}</nav></div></header><main id="main" class="wrap">{head}<div class="page-content">{body}</div></main><div class="wrap"><footer class="footer"><span>© Yohei Yanase</span><nav aria-label="フッター"><a href="/profile.html">プロフィール</a><a href="https://github.com/yoh7686">GitHub ↗</a><a href="/profile.html#contact">Contact</a><a href="#main">ページ上部へ ↑</a></nav></footer></div></body></html>'''
 html=html.replace(BASE+'/ ',BASE+'/')
 (ROOT/(name+'.html')).write_text(html,encoding='utf-8')
def section_head(title,url,label='一覧を見る'):
 return f'<div class="section-head"><h2>{esc(title)}</h2>{link(url,esc(label)+' <span aria-hidden="true">→</span>')}</div>'
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
def activity_entry(r):
 sub=r.get('subtitle','')
 return f'<article class="entry" {attr(r)}><div class="date">{esc(date(r) or "日付不明")}</div><div class="publisher">{tag(r["kind"])}</div><div class="entry-body"><h3>{esc(r["title"])}</h3>'+(f'<p>{esc(sub)}</p>' if sub and sub!=r['title'] else '')+'</div></article>'
def video_card(r):
 return f'<article class="card" {attr(r)}><a class="thumb" href="{esc(r["url"])}" aria-label="{esc(r["title"])}をYouTubeで見る"><img src="https://i.ytimg.com/vi/{esc(r["youtube"])}/hqdefault.jpg" alt="{esc(r["title"])}" width="480" height="270" loading="lazy"><span class="play" aria-hidden="true">▶</span></a><div class="meta"><span>VIDEO / YOUTUBE</span><span>{esc(date(r))}</span></div><h3>{link(r["url"],esc(r["title"]))}</h3></article>'
FEATURES=[dict(id='achievement-xi-015',title='魔人と失われた王国',date='2010',category='会社での制作',image='https://i.ytimg.com/vi/iizuEKdBvAw/hqdefault.jpg',url='https://youtu.be/iizuEKdBvAw',description='ゲームデザイナー',credit='公式紹介動画：BANDAI NAMCO Europe'),dict(id='achievement-xi-001',title='Unlimited Corridor',date='2016',category='研究作品',image='https://i.ytimg.com/vi/THk92rev1VA/hqdefault.jpg',url='https://youtu.be/THk92rev1VA',description='リダイレクテッドウォーキングによるVR体験。制作チームとして参加。',credit='研究作品の紹介動画')]
def work_card(r,home=False):
 dest='/works.html#'+r['id'] if home else r['url']
 return f'<article class="card"'+('' if home else f' id="{r["id"]}"')+f'><a class="thumb" href="{esc(dest)}"><img src="{esc(r["image"])}" alt="{esc(r["title"])}" width="480" height="270" loading="lazy"></a><div class="meta"><span>{esc(r["category"])}</span><span>{esc(r["date"])}</span></div><h3>{link(dest,esc(r["title"]))}</h3><p>{esc(r["description"])}</p>'+('' if home else f'<p class="caption">{esc(r["credit"])}</p>')+'</article>'
# One combined news stream, linking to the relevant archive entries.
news=[]
for r in M:
 if not date(r):continue
 news.append(dict(id='news-'+r['id'],date=date(r),kind='メディア',title=r['publisher']+'に'+('聞き手として参加したインタビュー' if '聞き手' in r['kind'] else ('寄稿' if '寄稿' in r['kind'] else ('登壇レポート' if any(x in r['kind'] for x in ['講演','パネル']) else ('インタビュー・対談' if any(x in r['kind'] for x in ['インタビュー','対談','座談会']) else '活動紹介記事'))))+'が掲載されました。「'+r['title']+'」',url='/media.html#'+r['id']))
for r in A:
 if not date(r):continue
 role=r['kind'];verb='で講演しました' if any(x in role for x in ['講演','登壇','クロストーク','パネル']) else ('で講義を行いました' if any(x in role for x in ['講義','授業','講師']) else 'に'+role+'として参加しました')
 news.append(dict(id='news-'+r['id'],date=date(r),kind='活動',title=r['title']+verb+'。',url='/activities.html#'+r['id']))
for r in V:
 if date(r):news.append(dict(id='news-'+r['id'],date=date(r),kind='動画',title='動画「'+r['title']+'」を公開しました。',url='/videos.html#'+r['id']))
news=order(news)
def news_rows(items,compact=False):
 return '<ul class="news-list">'+''.join(f'<li class="news-row" {attr(r)}><span class="date">{esc(date(r).replace("-","."))}</span>{tag(r["kind"])}{link(r["url"],esc(r["title"].split('。「')[0]+'。' if compact and '。「' in r["title"] else r["title"]))}</li>' for r in items)+'</ul>'
summary=f'<div class="profile-summary"><p class="eyebrow">PROFILE &amp; ACTIVITIES</p><h1>Yohei Yanase</h1><p class="name-ja">{esc(P["title"])}</p><p class="role">{esc(P["role"])}<small>{esc(P["company"])}</small></p><p class="fields">{esc(P["fields"])}</p><a class="subtle-link" href="/profile.html">プロフィールを見る →</a></div>'
body='<div class="intro">'+summary+'<section>'+section_head('News','/news.html','すべての活動')+news_rows(news[:8],True)+'</section></div>'
body+='<section class="section">'+section_head('作品','/works.html')+'<div class="card-grid home-works">'+''.join(work_card(r,True) for r in FEATURES)+'</div></section>'
body+='<section class="section">'+section_head('動画','/videos.html')+'<div class="card-grid">'+''.join(video_card(r) for r in V[:3])+'</div></section>'
body+='<div class="bottom-grid"><section class="section">'+section_head('メディア掲載','/media.html')+'<ul class="media-preview">'+''.join('<li><small>'+esc(date(r))+' / '+esc(r['publisher'])+' / '+esc(r['kind'])+'</small>'+link('/media.html#'+r['id'],esc(r['title']))+'</li>' for r in M[:3])+'</ul></section><section class="section">'+section_head('活動記録','/activities.html')+'<p class="muted">講演・講義・メンター・審査員の活動を年別に掲載しています。</p><nav class="year-links" aria-label="活動記録の年">'+''.join(link('/activities.html#year-'+y,esc(y)) for y in list(groups(A))[:5])+'</nav>'+link('/research.html','研究・著作一覧 →')+'</section></div>'
page('index','𥱋瀨 洋平',body)
page('media','メディア掲載',yearnav(M)+filterbar(M,True)+yearly(M,media_entry)+empty(),'インタビュー、活動・研究紹介、講演レポート、寄稿など。記事の掲載年ごとにまとめています。')
page('activities','活動記録',yearnav(A)+filterbar(A)+yearly(A,activity_entry)+empty(),'講演・講義・メンター・審査員などの活動記録。公開記録を確認できた活動を掲載しています。')
page('videos','動画',yearnav(V)+filterbar(V)+''.join(f'<section class="year-group" data-group id="year-{esc(y)}"><h2 class="year-heading">{esc(y)}'+('年' if y.isdigit() else '')+'</h2><div class="card-grid video-grid">'+''.join(video_card(r) for r in vs)+'</div></section>' for y,vs in groups(V).items())+empty(),'Unityの使い方、ゲーム制作、クリエイターへのインタビューなど。年は制作リストの区分に基づきます。')
page('news','News',yearnav(news)+filterbar(news,True)+yearly(news,lambda r:news_rows([r]))+empty(),'動画公開、登壇、メディア掲載など、活動全体のお知らせ。各項目から詳しい記録に進めます。')
body='<nav class="archive-links" aria-label="研究・著作の分類">'
cats=list(dict.fromkeys(r['category'] for r in R))
body+=''.join(link('#research-'+str(i),esc(cat)) for i,cat in enumerate(cats))+'</nav>'
for i,cat in enumerate(cats):
 body+=f'<section class="year-group" id="research-{i}"><h2 class="year-heading">{esc(cat)}</h2>'
 for n,r in enumerate([r for r in R if r['category']==cat],1):
  body+=f'<article class="entry research-entry" id="{esc(r["id"])}"><span class="number">{n:02}</span><div class="entry-body"><h3>{esc(r["title"])}</h3>'+(link(r['url'],'資料・掲載先 ↗','source-link') if r.get('url') else '')+'</div></article>'
 body+='</section>'
body+='<p class="notice">書誌情報・活動年は業績原簿に基づきます。委員・アドバイザー歴の開始年は、現在の在任を示すものではありません。</p>'
page('research','研究・著作',body,'論文、書籍、研究発表、展示、受賞などの記録。')
body='<nav class="archive-links" aria-label="作品の分類">'+''.join(link('#works-'+str(i),c) for i,c in enumerate(['会社での制作','個人制作','研究作品']))+'</nav>'
for i,cat in enumerate(['会社での制作','個人制作','研究作品']):
 body+=f'<section class="works-group" id="works-{i}"><h2 class="year-heading">{cat}</h2><div class="card-grid">'+''.join(work_card(r) for r in FEATURES if r['category']==cat)+'</div>'
 for r in W:
  if r['category']!=cat or r['id'] in [f['id'] for f in FEATURES]:continue
  body+=f'<div class="compact-work" id="{esc(r["id"])}">{esc(r["title"])}'+(' '+link(r['url'],'掲載先 ↗') if r.get('url') else '')+'</div>'
 body+='</section>'
body+='<p class="muted">作品画像は紹介動画のサムネイルです。個人制作のタイトル画像は本サイト用の表紙です。作品・画像の権利は各権利者に帰属します。</p>'
page('works','作品',body,'会社での制作、個人制作、研究作品。商業作品はクレジット上の担当を記載しています。')
body=f'<div class="prose"><p class="name-ja">{esc(P["title"])} / {esc(P["english"])}</p><p class="role">{esc(P["role"])}<small>{esc(P["company"])}</small></p><p>{esc(P["biography"])}</p><h2>活動分野</h2><p>{esc(P["fields"])}</p><h2>略歴</h2><p>1995年よりゲーム開発に従事。ゲームデザインやシナリオ制作に携わり、「魔人と失われた王国」などを制作。2012年より研究職へ転じました。</p><p>2017年、制作に参加した「Unlimited Corridor」が文化庁メディア芸術祭エンターテインメント部門優秀賞を受賞しました。</p><p>研究・制作とともに、講演、教育、メンター、審査などの活動を行っています。</p><h2>表記について</h2><p>氏名の文字が正しく表示されない場合は「簗瀬 洋平」をお使いください。</p><h2 id="contact">Contact / Links</h2><p>公開しているプロフィール・活動情報はこちらからご覧いただけます。</p><div class="profile-links">{link(P["github"],"GitHub ↗")}{link("https://learning.unity3d.jp/speaker/yohei-yanase/","Unity Learning Materials ↗")}</div><p class="muted">お問い合わせ窓口は準備中です。</p></div>'
page('profile','プロフィール',body)
page('404','ページが見つかりません','<p>URLが変更されたか、ページが存在しません。</p><p><a href="/">トップページへ戻る →</a></p>')
(ROOT/'portfolio/assets/favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="5" fill="#165e57"/><path d="M8 8l8 10 8-10M16 18v8" fill="none" stroke="#fff" stroke-width="3"/></svg>')
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+BASE+('/' if n=='index' else '/'+n+'.html')+'</loc></url>' for n in ['index','profile','research','activities','works','videos','media','news'])+'</urlset>')
print(f'Built: {len(A)} activities, {len(M)} media, {len(V)} videos, {len(R)} research records, {len(W)} works')
