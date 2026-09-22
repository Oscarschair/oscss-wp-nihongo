import paramiko

env_data = {}
with open('.env.deploy', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env_data[k.strip()] = v.strip()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    hostname=env_data['SSH_HOST'],
    port=int(env_data['SSH_PORT']),
    username=env_data['SSH_USER'],
    password=env_data['SSH_PASS'],
    look_for_keys=False,
    allow_agent=False
)

cmd = """LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php -r "
require getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php';
\$p = get_page_by_path('japanese-comparing-chotto-and-sukoshi-differences', OBJECT, 'post');
if (\$p) {
    echo 'DB POST TITLE: ' . \$p->post_title . PHP_EOL;
} else {
    echo 'Post not found' . PHP_EOL;
}
" """

stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))
ssh.close()
