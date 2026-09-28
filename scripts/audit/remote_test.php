<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$p = get_post(127);
// do_blocks を適用した後のHTML
$content = do_blocks($p->post_content);

// 単純に <h2 または c-vocab-box で分割
$pattern = '/(?=<h2\b|<div\s+class=["\'][^"\']*c-vocab-box)/iu';
$parts = preg_split($pattern, $content);

echo "PARTS COUNT AFTER DO_BLOCKS: " . count($parts) . PHP_EOL;
foreach ($parts as $idx => $pt) {
    $sub = trim(mb_substr($pt, 0, 80, 'UTF-8'));
    echo "  PART " . ($idx+1) . ": " . str_replace("\n", " ", $sub) . PHP_EOL;
}
