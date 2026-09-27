import re
import sys
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()
print("Connected to SSH successfully!")

# PHP code to update the vocabulary box in post 2476
php_code = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$post_id = 2476;
$p = get_post($post_id);
if (!$p) {
    echo "Post not found\\n";
    exit;
}

$content = $p->post_content;

$new_vocab_box = '<!-- wp:html -->
<div class="c-vocab-box">
  <h3 class="c-vocab-box__title">🎯 今回の語彙（重要ボキャブラリー）</h3>
  <p class="c-vocab-box__lead">この学習ノートに登場した、覚えておきたい重要日本語：</p>
  <div class="c-vocab-grid">
    <div class="c-vocab-card">
      <div class="c-vocab-card__header">
        <span class="c-vocab-card__word">様子（ようす）</span>
        <span class="c-badge c-badge--jlpt c-badge--jlpt-n3">JLPT N3</span>
      </div>
      <p class="c-vocab-card__meaning"><strong>意味：</strong>state, appearance, condition</p>
      <p class="c-vocab-card__example"><strong>例文：</strong>窓の外の様子を見ると、外はもう雨が降っているようだ。</p>
    </div>
    <div class="c-vocab-card">
      <div class="c-vocab-card__header">
        <span class="c-vocab-card__word">天気予報（てんきよほう）</span>
        <span class="c-badge c-badge--jlpt c-badge--jlpt-n3">JLPT N4/N3</span>
      </div>
      <p class="c-vocab-card__meaning"><strong>意味：</strong>weather forecast</p>
      <p class="c-vocab-card__example"><strong>例文：</strong>天気予報によると、午後から雨が降るそうだ。</p>
    </div>
    <div class="c-vocab-card">
      <div class="c-vocab-card__header">
        <span class="c-vocab-card__word">雲行き（くもゆき）</span>
        <span class="c-badge c-badge--jlpt c-badge--jlpt-n3">JLPT N3/N2</span>
      </div>
      <p class="c-vocab-card__meaning"><strong>意味：</strong>look of the sky, situation</p>
      <p class="c-vocab-card__example"><strong>例文：</strong>怪しい雲行きを見て「今にも雨が降りそうだ」と感じた。</p>
    </div>
    <div class="c-vocab-card">
      <div class="c-vocab-card__header">
        <span class="c-vocab-card__word">確信（かくしん）</span>
        <span class="c-badge c-badge--jlpt c-badge--jlpt-n3">JLPT N3/N2</span>
      </div>
      <p class="c-vocab-card__meaning"><strong>意味：</strong>conviction, confidence</p>
      <p class="c-vocab-card__example"><strong>例文：</strong>自分の目で直接見たことには強い確信が持てる。</p>
    </div>
  </div>
</div>
<!-- /wp:html -->';

$pattern = '/(<!-- wp:html -->\s*)?<div class="c-vocab-box">.*?<\/div>\s*<\/div>(\s*<!-- \/wp:html -->)?/us';
if (preg_match($pattern, $content)) {
    $content = preg_replace($pattern, $new_vocab_box, $content, 1);
    wp_update_post(array(
        'ID' => $post_id,
        'post_content' => $content
    ));
    echo "SUCCESS: Replaced vocab box with N3 vocabulary!\\n";
} else {
    echo "ERROR: Regex pattern not matched!\\n";
}

if (has_action('litespeed_purge_all')) {
    do_action('litespeed_purge_all');
    echo "LiteSpeed cache purged!\\n";
}
"""

with sftp.open('update_vocab_1015.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php update_vocab_1015.php && rm update_vocab_1015.php')
print("OUTPUT:\n", stdout.read().decode('utf-8', errors='replace'))
ssh.close()
