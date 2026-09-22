import paramiko, sys
env_data = {}
with open('.env.deploy', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env_data[k.strip()] = v.strip()

host = env_data.get('SSH_HOST', 'ssh.lolipop.jp')
port = int(env_data.get('SSH_PORT', 2222))
user = env_data.get('SSH_USER')
password = env_data.get('SSH_PASS')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=host, port=port, username=user, password=password, look_for_keys=False, allow_agent=False)
cmd = "/usr/local/php/8.2/bin/php -r \"require('web/nihongo.oscarchair.jp/wp-load.php'); \\$p = get_post(620); preg_match_all('/<ruby>.*?<\\/ruby>/u', \\$p->post_content, \\$m); print_r(\\$m[0]);\""
stdin, stdout, stderr = ssh.exec_command(cmd)
print("Result:", stdout.read().decode('utf-8'))
err = stderr.read().decode('utf-8')
if err:
    print("Err:", err)
ssh.close()
