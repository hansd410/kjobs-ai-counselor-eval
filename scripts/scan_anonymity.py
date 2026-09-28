#!/usr/bin/env python3
"""Fail closed on known identities, private paths, credentials and excluded payloads.
Default checks worktree files. --staged checks the complete Git index, not just a diff.
Identity fingerprints prevent embedding the private denylist in a blind release.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SKIP = {'.git', '.venv', '__pycache__', 'outputs', '.pytest_cache'}
RULES = {
 'internal_path': re.compile(r'/(?:Users|home|private/var|var/folders)/[^\s/]+', re.I),
 'windows_user_path': re.compile(r'[A-Z]:[\\/](?:Users|Documents and Settings)[\\/]',re.I),
 'credential': re.compile(r'(?:sk-(?:proj-|ant-api\d+-)?[A-Za-z0-9_-]{30,}|AIza[\w-]{30,})'),
 'private_contact': re.compile(r'(?<!\d)(?:\+82[- ]?)?0\d{1,2}[- ]\d{3,4}[- ]\d{4}(?!\d)'),
 'hosting_domain': re.compile(r'(?:[a-z0-9-]+\.)+chatgpt\.site',re.I),
 'email': re.compile(r'[\w.+-]+@[\w.-]+\.[a-z]{2,}',re.I),
}
TOKENS = re.compile(r'[가-힣a-z0-9_.@+-]+')
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def files(staged):
 if staged:
  for item in git('ls-files','--stage','-z').split(b'\0'):
   if not item:continue
   head,name=item.split(b'\t',1);mode,oid,stage=head.decode().split();name=name.decode()
   if mode!='100644' and mode!='100755':yield name,None;continue
   yield name,git('cat-file','blob',oid)
 else:
  for p in sorted(ROOT.rglob('*')):
   rel=p.relative_to(ROOT)
   if any(s in SKIP for s in rel.parts):continue
   if p.is_symlink():yield str(rel),None
   elif p.is_file():yield str(rel),p.read_bytes()
def scan(staged=False):
 allfiles=list(files(staged));blobs=dict(allfiles)
 rulebytes=blobs.get('privacy/identity_fingerprints.json')
 if not rulebytes:raise RuntimeError('Missing identity fingerprints in scanned tree')
 f=json.loads(rulebytes);lengths=f['lengths'];digests=set(f['digests'])
 hits=[];seen={}
 def identity_hits(text):
  bad=0
  tokens = TOKENS.findall(text.casefold())
  candidates = set(tokens)
  candidates.update(''.join(tokens[i:i+n]) for n in (2, 3) for i in range(len(tokens)-n+1) if sum(map(len,tokens[i:i+n])) <= 80)
  for token in candidates:
   if token in seen:bad+=seen[token];continue
   matched=False
   if not token.isdecimal():
    for n in lengths:
     if n>len(token):continue
     for i in range(len(token)-n+1):
      if hashlib.sha256(token[i:i+n].encode()).hexdigest() in digests:matched=True;break
     if matched:break
   seen[token]=int(matched);bad+=int(matched)
  return bad
 for name,raw in allfiles:
  if raw is None:hits.append({'file':name,'rule':'symlink/submodule/nonregular','count':1});continue
  try:text=raw.decode('utf-8')
  except UnicodeDecodeError:hits.append({'file':name,'rule':'binary/archive-not-approved','count':1});continue
  if re.search(r'(^|/)(?:private|candidates|counselor-engine|deployment)(/|$)|feedback.*\.csv$|(^|/)C4/.*\.md$',name,re.I):
   hits.append({'file':name,'rule':'excluded-path','count':1})
  n=identity_hits(name+'\n'+text)
  if n:hits.append({'file':name,'rule':'identity-fingerprint','count':n})
  for label,rx in RULES.items():
   matches=[m[0] for m in rx.finditer(text)]
   if label=='email':matches=[v for v in matches if not v.lower().endswith('@example.invalid')]
   if matches:hits.append({'file':name,'rule':label,'count':len(matches)})
 return {'mode':'index' if staged else 'worktree','files_scanned':len(allfiles),'matches':sum(x['count'] for x in hits),'findings':hits}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--staged',action='store_true');args=ap.parse_args()
 try:result=scan(args.staged)
 except Exception as exc:print('Anonymity check failed closed:',type(exc).__name__,str(exc),file=sys.stderr);sys.exit(2)
 print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(1 if result['matches'] else 0)
