"""Create an isolated analysis environment. No provider SDKs or API keys used."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
py=ROOT/'.venv/bin/python'
if not py.exists():
 if sys.version_info >= (3,12):subprocess.run([sys.executable,'-m','venv','.venv'],check=True)
 elif shutil.which('uv'):subprocess.run(['uv','venv','--python','3.12','.venv'],check=True)
 elif shutil.which('python3.12'):subprocess.run(['python3.12','-m','venv','.venv'],check=True)
 else:raise SystemExit('Python >=3.12 or uv is required to create the pinned environment.')
req=ROOT/'requirements.txt';stamp=ROOT/'.venv/requirements.installed'
if not stamp.exists() or stamp.read_bytes()!=req.read_bytes():
 if subprocess.run([str(py),'-m','pip','--version'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:
  cmd=[str(py),'-m','pip','install','-r',str(req)]
 elif shutil.which('uv'):cmd=['uv','pip','install','--python',str(py),'-r',str(req)]
 else:raise SystemExit('pip or uv is required to install dependencies.')
 subprocess.run(cmd,check=True);stamp.write_bytes(req.read_bytes())
