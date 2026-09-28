# -*- coding: utf-8 -*-
import paramiko

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

sftp = ssh.open_sftp()
with sftp.open('list_all.php', 'w') as f:
    f.write("""<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
$posts = get_posts(array('numberposts' => -1, 'post_type' => 'post', 'post_status' => 'any'));
foreach ($posts as $p) {
    echo $p->ID . " | " . $p->post_name . " | " . $p->post_status . PHP_EOL;
}
""")
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php list_all.php && rm list_all.php')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
