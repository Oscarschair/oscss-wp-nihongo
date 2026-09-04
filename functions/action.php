<?php
/**
 * Action hooks for oscss-wp-nihongo
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * テーマ初期セットアップ
 */
function oscss_theme_setup() {
	// 自動タイトルタグ
	add_theme_support( 'title-tag' );

	// アイキャッチ画像の有効化
	add_theme_support( 'post-thumbnails' );
	set_post_thumbnail_size( 1200, 630, true ); // OGP/SNS最適サイズ
	add_image_size( 'oscss-card', 640, 360, true ); // 16:9 カードサイズ

	// HTML5マークアップサポート
	add_theme_support(
		'html5',
		array(
			'search-form',
			'comment-form',
			'comment-list',
			'gallery',
			'caption',
			'style',
			'script',
		)
	);

	// カスタムロゴ
	add_theme_support(
		'custom-logo',
		array(
			'height'      => 60,
			'width'       => 240,
			'flex-height' => true,
			'flex-width'  => true,
		)
	);

	// ナビゲーションメニュー登録
	register_nav_menus(
		array(
			'primary' => __( 'メインナビゲーション', 'oscss-wp-nihongo' ),
			'footer'  => __( 'フッターナビゲーション', 'oscss-wp-nihongo' ),
		)
	);

	// コンテンツ幅
	$GLOBALS['content_width'] = 1120;
}
add_action( 'after_setup_theme', 'oscss_theme_setup' );

/**
 * CSS・JavaScriptアセットのエンキュー
 */
function oscss_enqueue_scripts() {
	// Google Fonts (Noto Sans JP, Inter)
	wp_enqueue_style(
		'oscss-google-fonts',
		'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;700&display=swap',
		array(),
		null
	);

	// Design Tokens CSS
	wp_enqueue_style(
		'oscss-tokens',
		OSCSS_THEME_URI . '/assets/css/tokens.css',
		array(),
		OSCSS_THEME_VERSION
	);

	// Main CSS
	wp_enqueue_style(
		'oscss-main',
		OSCSS_THEME_URI . '/assets/css/main.css',
		array( 'oscss-tokens' ),
		OSCSS_THEME_VERSION
	);

	// Main JS (defer)
	wp_enqueue_script(
		'oscss-main-script',
		OSCSS_THEME_URI . '/assets/js/main.js',
		array(),
		OSCSS_THEME_VERSION,
		true
	);
}
add_action( 'wp_enqueue_scripts', 'oscss_enqueue_scripts' );

/**
 * ウィジェットエリア（サイドバー・フッター）の登録
 */
function oscss_widgets_init() {
	register_sidebar(
		array(
			'name'          => __( 'フッターウィジェット 1', 'oscss-wp-nihongo' ),
			'id'            => 'footer-1',
			'description'   => __( 'フッター左列に表示されるウィジェットです。', 'oscss-wp-nihongo' ),
			'before_widget' => '<div id="%1$s" class="c-widget %2$s">',
			'after_widget'  => '</div>',
			'before_title'  => '<h3 class="c-widget__title">',
			'after_title'   => '</h3>',
		)
	);

	register_sidebar(
		array(
			'name'          => __( 'フッターウィジェット 2', 'oscss-wp-nihongo' ),
			'id'            => 'footer-2',
			'description'   => __( 'フッター右列に表示されるウィジェットです。', 'oscss-wp-nihongo' ),
			'before_widget' => '<div id="%1$s" class="c-widget %2$s">',
			'after_widget'  => '</div>',
			'before_title'  => '<h3 class="c-widget__title">',
			'after_title'   => '</h3>',
		)
	);
}
add_action( 'widgets_init', 'oscss_widgets_init' );

/**
 * Google AdSense & Google Analytics 4 (GA4) を wp_head に出力
 */
function oscss_head_analytics_and_ads() {
	?>
	<!-- Google AdSense -->
	<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6358046201606104" crossorigin="anonymous"></script>

	<!-- Google tag (gtag.js) - GA4 -->
	<script async src="https://www.googletagmanager.com/gtag/js?id=G-3QBPY87VPP"></script>
	<script>
		window.dataLayer = window.dataLayer || [];
		function gtag(){dataLayer.push(arguments);}
		gtag('js', new Date());
		gtag('config', 'G-3QBPY87VPP');
	</script>
	<?php
}
add_action( 'wp_head', 'oscss_head_analytics_and_ads', 2 );

