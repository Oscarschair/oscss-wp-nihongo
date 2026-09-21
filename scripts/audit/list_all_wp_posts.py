import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))
ssh.connect(
    hostname=env['SSH_HOST'],
    port=int(env['SSH_PORT']),
    username=env['SSH_USER'],
    password=env['SSH_PASS'],
    look_for_keys=False,
    allow_agent=False
)

php = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
$posts = get_posts(array('post_status' => array('publish', 'future'), 'numberposts' => -1));
foreach($posts as $p) {
    echo "{$p->ID}: [{$p->post_status}] {$p->post_name}\n";
}
"""

sftp = ssh.open_sftp()
with sftp.open('list_all_posts.php', 'w') as f:
    f.write(php)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php list_all_posts.php && rm list_all_posts.php')
print(stdout.read().decode('utf-8'))
ssh.close()
