import paramiko
import json

env_data = {}
with open('.env.deploy', 'r', encoding='utf-8') as ef:
    for line in ef:
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
sftp = ssh.open_sftp()

php_code = """<?php
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
// タグ一覧でJLPT関連
$tags = get_terms(array('taxonomy' => 'post_tag', 'hide_empty' => false));
$jlpt_tags = array();
foreach ($tags as $t) {
    if (stripos($t->name, 'jlpt') !== false) {
        $jlpt_tags[] = array('id' => $t->term_id, 'name' => $t->name, 'slug' => $t->slug, 'count' => $t->count);
    }
}
// メタデータ _oscss_jlpt_level のユニーク値と件数
global $wpdb;
$meta_levels = $wpdb->get_results("SELECT meta_value, COUNT(*) as cnt FROM {$wpdb->postmeta} WHERE meta_key = '_oscss_jlpt_level' GROUP BY meta_value");
echo json_encode(array('jlpt_tags' => $jlpt_tags, 'meta_levels' => $meta_levels), JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
"""

remote_php = 'web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/temp_jlpt_check.php'
with sftp.file(remote_php, 'w') as f:
    f.write(php_code)

stdin, stdout, stderr = ssh.exec_command('LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php $HOME/' + remote_php + ' && rm -f $HOME/' + remote_php)
print(stdout.read().decode('utf-8', errors='ignore'))
sftp.close()
ssh.close()
