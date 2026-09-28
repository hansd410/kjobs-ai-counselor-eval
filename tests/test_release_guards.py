"""Release safeguards: staged identity leaks, excluded payloads, and vote edge cases."""
import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('privacy_scan',ROOT/'scripts/scan_anonymity.py')
scan=importlib.util.module_from_spec(spec);spec.loader.exec_module(scan)
from src.consensus import pairwise_majority

class ReleaseGuards(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.old=scan.ROOT;scan.ROOT=self.root
  self.term='Fixture'+'Identity'
  (self.root/'privacy').mkdir()
  (self.root/'privacy/identity_fingerprints.json').write_text(json.dumps({'lengths':[len(self.term)],'digests':[hashlib.sha256(self.term.casefold().encode()).hexdigest()]}))
  subprocess.run(['git','init','-q',str(self.root)],check=True)
 def tearDown(self):scan.ROOT=self.old;self.tmp.cleanup()
 def git(self,*args):return subprocess.run(['git','-C',str(self.root),*args],check=True,stdout=subprocess.PIPE)
 def test_staged_leak_blocked_even_with_clean_worktree(self):
  p=self.root/'README.md';p.write_text('An organization: '+self.term);self.git('add','.')
  p.write_text('Clean working copy')
  self.assertEqual(scan.scan(False)['matches'],0)
  self.assertGreater(scan.scan(True)['matches'],0)
 def test_excluded_archive_and_symlink_fail_closed(self):
  (self.root/'payload.bin').write_bytes(bytes([255,0,254]));(self.root/'linked').symlink_to('/dev/null')
  self.assertGreaterEqual(scan.scan()['matches'],2)
 def test_missing_rules_fail_closed(self):
  (self.root/'privacy/identity_fingerprints.json').unlink()
  with self.assertRaises(RuntimeError):scan.scan()
 def test_undecidable_votes_are_not_dropped(self):
  self.assertEqual(pairwise_majority(['A','B','tie']),(None,'tie'))
  self.assertEqual(pairwise_majority(['B','B','A']),('B','majority'))
  self.assertEqual(pairwise_majority(['B','B']),(None,'insufficient'))

if __name__=='__main__':unittest.main()
