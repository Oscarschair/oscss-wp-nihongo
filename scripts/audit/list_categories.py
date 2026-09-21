import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

php = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
$cats = get_categories(array('hide_empty' => false));
foreach($cats as $c) {
    echo "ID: {$c->term_id} | Name: {$c->name} | Slug: {$c->slug} | Count: {$c->count} | Desc: {$c->description}\n";
}
"""

with sftp.open('list_cats.php', 'w') as f:
    f.write(php)

stdin, stdout, stderr = ssh.exec_command('LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php list_cats.php && rm list_cats.php')
print(stdout.read().decode('utf-8'))
sftp.close()
ssh.close()
