# -*- coding: utf-8 -*-
import paramiko
import requests

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

sftp = ssh.open_sftp()
with sftp.open('web/nihongo.oscarchair.jp/purge_header.php', 'w') as f:
    f.write("""<?php
header('X-LiteSpeed-Purge: *');
header('Cache-Control: no-cache, must-revalidate, max-age=0');
echo "Purge header sent!";
""")
sftp.close()
ssh.close()

# Request purge_header.php via HTTP so LiteSpeed web server receives X-LiteSpeed-Purge: *
res = requests.get('https://nihongo.oscarchair.jp/purge_header.php')
print("HTTP Purge Response:", res.status_code)

# Also test hair salon page with cache-busting query
res2 = requests.get('https://nihongo.oscarchair.jp/street-japanese-hair-salon-survival-shampoo-trap-guide/?nocache=' + str(requests.utils.default_user_agent()))
print("Hair salon response:", res2.status_code, "X-Cache:", res2.headers.get('X-Cache'), "LSCache:", res2.headers.get('x-litespeed-cache'))

# Check if 梳く is in the response
print("Contains 梳く:", '梳く' in res2.text)
print("Contains c-vocab-card:", 'c-vocab-card' in res2.text)
