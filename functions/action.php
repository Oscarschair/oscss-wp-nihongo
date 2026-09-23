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
	$tokens_css_ver = file_exists( OSCSS_THEME_DIR . '/assets/css/tokens.css' )
		? filemtime( OSCSS_THEME_DIR . '/assets/css/tokens.css' )
		: OSCSS_THEME_VERSION;

	wp_enqueue_style(
		'oscss-tokens',
		OSCSS_THEME_URI . '/assets/css/tokens.css',
		array(),
		$tokens_css_ver
	);

	// Main CSS
	$main_css_ver = file_exists( OSCSS_THEME_DIR . '/assets/css/main.css' )
		? filemtime( OSCSS_THEME_DIR . '/assets/css/main.css' )
		: OSCSS_THEME_VERSION;

	wp_enqueue_style(
		'oscss-main',
		OSCSS_THEME_URI . '/assets/css/main.css',
		array( 'oscss-tokens' ),
		$main_css_ver
	);

	// Main JS (defer)
	$main_js_ver = file_exists( OSCSS_THEME_DIR . '/assets/js/main.js' )
		? filemtime( OSCSS_THEME_DIR . '/assets/js/main.js' )
		: OSCSS_THEME_VERSION;

	wp_enqueue_script(
		'oscss-main-script',
		OSCSS_THEME_URI . '/assets/js/main.js',
		array(),
		$main_js_ver,
		true
	);

	// JSに変数を渡す（閲覧数非同期トラッキング用）
	wp_localize_script(
		'oscss-main-script',
		'oscssSettings',
		array(
			'restUrl'   => esc_url_raw( rest_url( 'oscss/v1/' ) ),
			'postId'    => is_single() ? get_the_ID() : 0,
			'isSingle'  => is_single() && ! is_preview(),
			'nonce'     => wp_create_nonce( 'wp_rest' ),
		)
	);
}
add_action( 'wp_enqueue_scripts', 'oscss_enqueue_scripts' );

/**
 * ユーザーのソート選択（?sort=）をCookieに保存
 */
function oscss_handle_sort_cookie() {
	if ( ! is_admin() && isset( $_GET['sort'] ) ) {
		$sort = sanitize_key( $_GET['sort'] );
		if ( in_array( $sort, array( 'latest', 'views' ), true ) ) {
			// 30日間記憶
			setcookie( 'oscss_post_sort', $sort, time() + ( 30 * DAY_IN_SECONDS ), COOKIEPATH ? COOKIEPATH : '/', COOKIE_DOMAIN, is_ssl(), false );
			$_COOKIE['oscss_post_sort'] = $sort;
		}
	}
}
add_action( 'init', 'oscss_handle_sort_cookie' );

/**
 * アーカイブページ（カテゴリー・タグ・日付一覧）のクエリ並び順制御
 */
function oscss_sort_archive_queries( $query ) {
	if ( ! is_admin() && $query->is_main_query() && ( $query->is_archive() || $query->is_home() || $query->is_search() ) ) {
		$sort = oscss_get_current_sort();

		if ( 'views' === $sort ) {
			$query->set( 'meta_key', '_oscss_post_views' );
			$query->set( 'orderby', array(
				'meta_value_num' => 'DESC',
				'date'           => 'DESC',
			) );
		}
	}
}
add_action( 'pre_get_posts', 'oscss_sort_archive_queries' );

/**
 * 閲覧数カウント用のREST APIエンドポイント登録
 * POST /wp-json/oscss/v1/track-view/{post_id}
 */
function oscss_register_view_tracker_endpoint() {
	register_rest_route(
		'oscss/v1',
		'/track-view/(?P<id>\d+)',
		array(
			'methods'             => 'POST',
			'callback'            => 'oscss_rest_track_view_callback',
			'permission_callback' => '__return_true',
			'args'                => array(
				'id' => array(
					'validate_callback' => function( $param ) {
						return is_numeric( $param );
					},
				),
			),
		)
	);
}
add_action( 'rest_api_init', 'oscss_register_view_tracker_endpoint' );

/**
 * 閲覧数トラッキング REST API コールバック
 */
function oscss_rest_track_view_callback( $request ) {
	$post_id = (int) $request->get_param( 'id' );

	if ( ! $post_id || 'post' !== get_post_type( $post_id ) || 'publish' !== get_post_status( $post_id ) ) {
		return new WP_Error( 'invalid_post', __( '無効な投稿IDです。', 'oscss-wp-nihongo' ), array( 'status' => 404 ) );
	}

	$views = oscss_set_post_views( $post_id );

	return rest_ensure_response(
		array(
			'success' => true,
			'post_id' => $post_id,
			'views'   => $views,
		)
	);
}

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

/**
 * 旧URL構造（/YYYY/MM/DD/slug/）から新URL（/%postname%/）への自動301リダイレクト
 */
function oscss_redirect_old_date_permalinks() {
	$request_uri = isset( $_SERVER['REQUEST_URI'] ) ? $_SERVER['REQUEST_URI'] : '';
	$path = trim( (string) wp_parse_url( $request_uri, PHP_URL_PATH ), '/' );

	// /2026/09/05/post-slug 形式にマッチするか判定
	if ( preg_match( '#^(\d{4})/(\d{2})/(\d{2})/([^/]+)$#', $path, $matches ) ) {
		$slug = sanitize_title( $matches[4] );
		$args = array(
			'name'        => $slug,
			'post_type'   => 'post',
			'post_status' => 'publish',
			'numberposts' => 1,
		);
		$posts = get_posts( $args );
		if ( ! empty( $posts ) ) {
			wp_safe_redirect( get_permalink( $posts[0]->ID ), 301 );
			exit;
		}
	}
}
add_action( 'template_redirect', 'oscss_redirect_old_date_permalinks', 1 );

/**
 * 投稿一覧画面のカスタムカラム（アイキャッチ・閲覧数）を出力
 */
function oscss_render_post_custom_columns( $column, $post_id ) {
	if ( 'thumbnail' === $column ) {
		if ( has_post_thumbnail( $post_id ) ) {
			$thumb_url = get_the_post_thumbnail_url( $post_id, 'thumbnail' );
			$edit_url  = get_edit_post_link( $post_id );
			echo '<a href="' . esc_url( $edit_url ) . '"><img src="' . esc_url( $thumb_url ) . '" alt="" class="oscss-admin-thumb" /></a>';
		} else {
			echo '<span class="oscss-admin-no-thumb">—</span>';
		}
	} elseif ( 'views' === $column ) {
		$views = (int) get_post_meta( $post_id, '_oscss_post_views', true );
		echo '<span class="oscss-admin-views"><strong>' . esc_html( number_format_i18n( $views ) ) . '</strong> <span style="font-size: 11px; color: #888;">PV</span></span>';
	}
}
add_action( 'manage_posts_custom_column', 'oscss_render_post_custom_columns', 10, 2 );

/**
 * 閲覧数でのソートクエリ処理
 */
function oscss_sort_posts_by_views( $query ) {
	if ( ! is_admin() || ! $query->is_main_query() ) {
		return;
	}
	if ( 'views' === $query->get( 'orderby' ) ) {
		$query->set( 'meta_key', '_oscss_post_views' );
		$query->set( 'orderby', 'meta_value_num' );
	}
}
add_action( 'pre_get_posts', 'oscss_sort_posts_by_views' );

/**
 * 管理画面の投稿一覧用スタイリング
 */
function oscss_admin_custom_css() {
	$screen = get_current_screen();
	if ( $screen && 'edit-post' === $screen->id ) {
		echo '<style>
			.column-thumbnail { width: 90px; text-align: center; vertical-align: middle !important; }
			.column-views { width: 90px; text-align: right; vertical-align: middle !important; }
			th.column-views { text-align: right; }
			.oscss-admin-thumb { width: 72px; height: 40px; object-fit: cover; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.15); display: block; margin: 0 auto; transition: transform 0.2s; border: 1px solid #e0e0e0; }
			.oscss-admin-thumb:hover { transform: scale(1.15); z-index: 10; position: relative; box-shadow: 0 4px 10px rgba(0,0,0,0.25); }
			.oscss-admin-no-thumb { color: #ccc; font-size: 14px; }
			.oscss-admin-views { font-variant-numeric: tabular-nums; font-size: 13px; }
		</style>';
	}
}
add_action( 'admin_head', 'oscss_admin_custom_css' );




