"""Read a respondent Form ID or URL from stdin; store only its encoded ID."""
from pathlib import Path
import base64,json,re,sys
from urllib.parse import urlsplit
value=sys.stdin.read().strip()
if value.startswith('https://'):
 u=urlsplit(value)
 if u.hostname!='docs.google.com':raise SystemExit('Use the Google Forms respondent URL or Form ID.')
 m=re.fullmatch(r'/forms/d/e/(1FAIpQL[A-Za-z0-9_-]+)/viewform/?',u.path)
 if not m:raise SystemExit('Use the respondent URL, not the editor URL.')
 value=m.group(1)
if not re.fullmatch(r'1FAIpQL[A-Za-z0-9_-]+',value):raise SystemExit('Invalid respondent Form ID.')
p=Path(__file__).parent/'assets/contact-config.json'
p.write_text(json.dumps({'formIdEncoded':base64.b64encode(value.encode()).decode()},indent=2)+'\n')
print('Updated contact-config.json. Publish this file to switch the destination.')
