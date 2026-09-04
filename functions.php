<?php
/**
 * oscss-wp-nihongo functions and definitions
 *
 * @package oscss-wp-nihongo
 * @version 1.0.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit; // 直接アクセス禁止
}

define( 'OSCSS_THEME_VERSION', '1.0.1' );
define( 'OSCSS_THEME_DIR', get_template_directory() );
define( 'OSCSS_THEME_URI', get_template_directory_uri() );

/**
 * モジュールローダー (PHP Modular Architecture)
 * 役割ごとに分割された functions/ 配下のファイルを読み込みます。
 */
$oscss_includes = array(
	'/functions/utility.php',   // 共通ヘルパー関数
	'/functions/action.php',    // add_action フック（セットアップ、エンキュー等）
	'/functions/filter.php',    // add_filter フック（抜粋、タイトル制御等）
	'/functions/shortcode.php', // カスタムショートコード
);

foreach ( $oscss_includes as $file ) {
	$filepath = OSCSS_THEME_DIR . $file;
	if ( file_exists( $filepath ) ) {
		require_once $filepath;
	}
}
