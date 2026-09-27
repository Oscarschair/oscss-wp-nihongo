import paramiko
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

php_code = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$p = get_post(2465);
if ($p) {
    if (preg_match('/<!-- wp:html -->\\s*<div class="c-vocab-box">.*?<\\/div>\\s*<!-- \\/wp:html -->/s', $p->post_content, $m)) {
        echo $m[0];
    } else {
        echo "Not found with pattern, showing c-vocab-box snippet:" . PHP_EOL;
        $pos = strpos($p->post_content, 'c-vocab-box');
        if ($pos !== false) {
            echo substr($p->post_content, $pos - 50, 1000);
        }
    }
}
"""

sftp = ssh.open_sftp()
with sftp.open('get_vocab_sample.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php get_vocab_sample.php && rm get_vocab_sample.php')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
