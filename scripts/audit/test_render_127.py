import paramiko
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

sftp = ssh.open_sftp()
test_php = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$p = get_post(127);
$rendered = apply_filters('the_content', $p->post_content);

preg_match_all('/<h2[^>]*>(.*?)<\\/h2>/su', $rendered, $h2_matches);
echo "RENDERED H2 COUNT: " . count($h2_matches[0]) . "\\n";
foreach ($h2_matches[1] as $idx => $h2_text) {
    $num = $idx + 1;
    echo "  H2 #$num: " . strip_tags($h2_text) . "\\n";
}

preg_match_all('/<section[^>]*class=["\']([^"\']*)["\'][^>]*>/i', $rendered, $sec_matches);
echo "\\nRENDERED SECTION COUNT: " . count($sec_matches[0]) . "\\n";
foreach ($sec_matches[1] as $idx => $cls) {
    $num = $idx + 1;
    echo "  SEC #$num: " . $cls . "\\n";
}
"""
with sftp.open('test_render_127.php', 'w') as f:
    f.write(test_php)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php test_render_127.php && rm test_render_127.php')
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("STDOUT:", out)
if err:
    print("STDERR:", err)
ssh.close()
