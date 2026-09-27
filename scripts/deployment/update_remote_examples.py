import paramiko
import sys
import json

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

sys.path.insert(0, '.')
from scripts.audit.clean_all_vocab_examples import curated_examples

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

# Upload curated json
with sftp.open('curated_examples.json', 'w') as jf:
    jf.write(json.dumps(curated_examples, ensure_ascii=False))

php_script = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$json_str = file_get_contents('curated_examples.json');
$curated = json_decode($json_str, true);

$posts = get_posts(array(
    'post_type' => 'post',
    'post_status' => 'any',
    'numberposts' => -1
));

$updated_count = 0;

foreach ($posts as $p) {
    $content = $p->post_content;
    $changed = false;
    
    $new_content = preg_replace_callback('/<div class="c-vocab-card">.*?<\\/div>/s', function($matches) use ($curated, &$changed) {
        $card = $matches[0];
        
        if (preg_match('/<span class="c-vocab-card__word">(.*?)<\\/span>/s', $card, $wm)) {
            $raw_word = strip_tags($wm[1]);
            $clean_word = preg_replace('/[\\(（].*?[\\)）]/u', '', $raw_word);
            $clean_word = trim($clean_word);
            
            $replacement_ex = null;
            foreach ($curated as $k => $v) {
                if (mb_strpos($clean_word, $k) !== false || mb_strpos($k, $clean_word) !== false) {
                    $replacement_ex = $v;
                    break;
                }
            }
            
            if (preg_match('/<p class="c-vocab-card__example">(.*?)<\\/p>/s', $card, $em)) {
                $cur_ex_full = $em[1];
                $cur_ex_text = preg_replace('/^<strong>.*?<\\/strong>\\s*/u', '', $cur_ex_full);
                $cur_ex_plain = strip_tags($cur_ex_text);
                
                $is_dirty = (
                    mb_strpos($cur_ex_plain, '##') !== false ||
                    mb_strpos($cur_ex_plain, '|') !== false ||
                    mb_strpos($cur_ex_plain, '│') !== false ||
                    mb_strpos($cur_ex_plain, '」') !== false ||
                    mb_strpos($cur_ex_plain, '➔') !== false ||
                    mb_strpos($cur_ex_plain, '**') !== false ||
                    mb_strlen(trim($cur_ex_plain)) < 8
                );
                
                if ($replacement_ex || $is_dirty) {
                    $final_ex = $replacement_ex ? $replacement_ex : "日常会話やビジネスの場面で「" . $clean_word . "」を正しく使いこなす。";
                    $new_card = preg_replace(
                        '/<p class="c-vocab-card__example">.*?<\\/p>/s',
                        '<p class="c-vocab-card__example"><strong>例文：</strong>' . $final_ex . '</p>',
                        $card
                    );
                    $changed = true;
                    return $new_card;
                }
            }
        }
        return $card;
    }, $content);
    
    if ($changed) {
        wp_update_post(array(
            'ID' => $p->ID,
            'post_content' => $new_content
        ));
        $updated_count++;
        echo "[UPDATED EXAMPLES] Post ID: " . $p->ID . " - " . $p->post_title . PHP_EOL;
    }
}

echo "Total updated posts: " . $updated_count . PHP_EOL;

if (has_action('litespeed_purge_all')) {
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache Purged All!" . PHP_EOL;
}
"""

with sftp.open('run_clean_examples.php', 'w') as pf:
    pf.write(php_script)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php run_clean_examples.php && rm run_clean_examples.php curated_examples.json')
out = stdout.read().decode('utf-8', errors='replace')
print(out)
ssh.close()
