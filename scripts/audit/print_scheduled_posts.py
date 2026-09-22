import sys
import subprocess

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

res = subprocess.check_output(['python', 'scripts/audit/comprehensive_audit.py'], encoding='utf-8', errors='replace')
lines = res.split('\n')
for i, line in enumerate(lines):
    if 'WORDPRESS DATABASE POSTS AUDIT' in line:
        print('\n'.join(lines[i:i+65]))
        break
