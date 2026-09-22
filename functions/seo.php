<?php
/**
 * SEO, OGP, and Structured Data (JSON-LD) Engine for oscss-wp-nihongo
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * 1. メタタグ・OGP・Twitter Cards を wp_head に出力
 */
function oscss_seo_meta_tags() {
	$site_name   = get_bloginfo( 'name' );
	$site_desc   = get_bloginfo( 'description' );
	$current_url = oscss_get_canonical_url();
	$og_title    = '';
	$og_desc     = '';
	$og_type     = 'website';
	$og_image    = OSCSS_THEME_URI . '/assets/images/og-image.png'; // デフォルトOGP画像 (1200x630)
	$robots      = 'index, follow, max-image-preview:large';

	if ( is_front_page() || is_home() ) {
		$og_title = $site_name . ' | ' . $site_desc;
		$og_desc  = '香港出身のオスカーが、外国人視点で日本語の「ことばのあや」や文化の違い、現場サバイバルを解説する日本語学習ブログ。全記事・全漢字ルビ（ふりがな）完備で、辞書なしでスラスラ読める！';
		$og_type  = 'website';
	} elseif ( is_single() ) {
		global $post;
		$clean_title = oscss_get_clean_title( $post );
		$og_title    = $clean_title . ' | ' . $site_name;
		$og_desc     = oscss_get_clean_excerpt( $post, 120 );
		$og_type     = 'article';

		if ( has_post_thumbnail( $post->ID ) ) {
			$thumb_url = get_the_post_thumbnail_url( $post->ID, 'full' );
			if ( $thumb_url ) {
				$og_image = $thumb_url;
			}
		}
	} elseif ( is_page() ) {
		global $post;
		$clean_title = oscss_get_clean_title( $post );
		$og_title    = $clean_title . ' | ' . $site_name;
		$og_desc     = oscss_get_clean_excerpt( $post, 120, false );
		$og_type     = 'article';

		if ( has_post_thumbnail( $post->ID ) ) {
			$thumb_url = get_the_post_thumbnail_url( $post->ID, 'full' );
			if ( $thumb_url ) {
				$og_image = $thumb_url;
			}
		}
	} elseif ( is_category() ) {
		$cat       = get_queried_object();
		$cat_title = single_cat_title( '', false );
		$og_title  = $cat_title . 'の記事一覧 | ' . $site_name;
		$cat_slug  = isset( $cat->slug ) ? $cat->slug : '';

		// 未分類（uncategorized）または記事数0のカテゴリーは noindex にして検索汚染を防止
		if ( 'uncategorized' === $cat_slug || ( isset( $cat->count ) && 0 === (int) $cat->count ) ) {
			$robots = 'noindex, follow';
		}

		$cat_desc = category_description();
		if ( ! empty( $cat_desc ) ) {
			$og_desc = wp_strip_all_tags( $cat_desc );
		} else {
			// カテゴリー別の特化ディスクリプション（各連載の魅力を具体的に要約）
			$cat_specific_descs = array(
				'culture-shock'   => '香港と日本の文化の違いや生活習慣のギャップに驚いた実体験を徹底解説！真冬の氷水、街中にゴミ箱がない理由、主食×主食の炭水化物コンボ、散髪代5,000円など、外国人視点で発見した日本の面白い日常と文化の深層をお届けします。',
				'comparing'       => '似ているけれどニュアンスが全く違う日本語を徹底比較！「全然」VS「全く」、「さようなら」VS「またね」、「あげる」VS「くれる」など、教科書では教えてくれない日常会話のリアルな使い分けを香港出身のオスカーが分かりやすく解説します。',
				'kotoba-no-aya'   => '「大丈夫です」「その節はどうも…」「すみません」など、文脈やトーンで意味が180度変わる日本語の「ことばのあや」を深掘り！終助詞「ぞ・ぜ・ね・よ」の微妙なニュアンスや、日本人の本音と建前を外国人視点から分かりやすく解き明かします。',
				'street-japanese' => 'コンビニのレジ、駅の自動改札、居酒屋、美容室、カフェ注文など、教科書には載っていない日本のリアルな日常現場で生き残るための実践的日本語とマナーをRPG風に楽しく攻略する実践サバイバルガイドです。',
			);

			if ( isset( $cat_specific_descs[ $cat_slug ] ) ) {
				$og_desc = $cat_specific_descs[ $cat_slug ];
			} else {
				$og_desc = sprintf( '香港出身のオスカーが外国人視点で解説する「%s」に関する日本語学習ノート・解説記事一覧です。', $cat_title );
			}
		}
		$og_type = 'object';
	} elseif ( is_tag() ) {
		$tag_title = single_tag_title( '', false );
		$og_title  = '#' . $tag_title . ' の記事一覧 | ' . $site_name;
		$tag_desc  = tag_description();
		$og_desc   = ! empty( $tag_desc ) ? wp_strip_all_tags( $tag_desc ) : sprintf( 'タグ「%s」に関連する日本語学習ノート記事一覧です。', $tag_title );
		$og_type   = 'object';
	} elseif ( is_search() ) {
		$og_title = '「' . get_search_query() . '」の検索結果 | ' . $site_name;
		$og_desc  = sprintf( '「%s」の検索結果ページです。', get_search_query() );
		$robots   = 'noindex, follow';
	} elseif ( is_404() ) {
		$og_title = 'ページが見つかりませんでした (404 Not Found) | ' . $site_name;
		$og_desc  = 'お探しのページは見つかりませんでした。URLが変更されたか削除された可能性があります。';
		$robots   = 'noindex, follow';
	} else {
		$og_title = wp_get_document_title();
		$og_desc  = $site_desc;
	}

	// メタディスクリプション & Robots & Canonical & Theme Color
	echo "\n<!-- oscss-wp-nihongo SEO & Social Meta -->\n";
	echo '<meta name="description" content="' . esc_attr( $og_desc ) . '">' . "\n";
	echo '<meta name="robots" content="' . esc_attr( $robots ) . '">' . "\n";
	echo '<meta name="theme-color" content="#2563eb">' . "\n";
	echo '<link rel="canonical" href="' . esc_url( $current_url ) . '">' . "\n";

	// Open Graph (OGP)
	echo '<meta property="og:site_name" content="' . esc_attr( $site_name ) . '">' . "\n";
	echo '<meta property="og:type" content="' . esc_attr( $og_type ) . '">' . "\n";
	echo '<meta property="og:title" content="' . esc_attr( $og_title ) . '">' . "\n";
	echo '<meta property="og:description" content="' . esc_attr( $og_desc ) . '">' . "\n";
	echo '<meta property="og:url" content="' . esc_url( $current_url ) . '">' . "\n";
	echo '<meta property="og:image" content="' . esc_url( $og_image ) . '">' . "\n";
	echo '<meta property="og:locale" content="ja_JP">' . "\n";

	if ( is_single() ) {
		echo '<meta property="article:published_time" content="' . esc_attr( get_the_date( 'c' ) ) . '">' . "\n";
		echo '<meta property="article:modified_time" content="' . esc_attr( get_the_modified_date( 'c' ) ) . '">' . "\n";
		$categories = get_the_category();
		if ( ! empty( $categories ) ) {
			echo '<meta property="article:section" content="' . esc_attr( $categories[0]->name ) . '">' . "\n";
		}
	}

	// Twitter Cards
	echo '<meta name="twitter:card" content="summary_large_image">' . "\n";
	echo '<meta name="twitter:title" content="' . esc_attr( $og_title ) . '">' . "\n";
	echo '<meta name="twitter:description" content="' . esc_attr( $og_desc ) . '">' . "\n";
	echo '<meta name="twitter:image" content="' . esc_url( $og_image ) . '">' . "\n";
	echo "<!-- /oscss-wp-nihongo SEO & Social Meta -->\n\n";
}
add_action( 'wp_head', 'oscss_seo_meta_tags', 1 );

/**
 * 2. JSON-LD 構造化データ（Schema.org）を出力
 */
function oscss_seo_json_ld() {
	$site_url  = home_url( '/' );
	$site_name = get_bloginfo( 'name' );
	$site_desc = '香港出身のオスカーが、外国人視点で日本語の「ことばのあや」や文化の違い、現場サバイバルを解説する日本語学習ブログ。全記事・全漢字ルビ（ふりがな）完備で、辞書なしでスラスラ読める！';
	$logo_url  = OSCSS_THEME_URI . '/assets/images/my-icon.png';
	$og_image  = OSCSS_THEME_URI . '/assets/images/og-image.png';

	$schemas = array();

	// 1. 全ページ共通: パンくずリスト（BreadcrumbList）
	$breadcrumbs = oscss_get_breadcrumb_schema_items();
	if ( ! empty( $breadcrumbs ) ) {
		$schemas[] = array(
			'@context'        => 'https://schema.org',
			'@type'           => 'BreadcrumbList',
			'itemListElement' => $breadcrumbs,
		);
	}

	// 2. トップページ: WebSite ＆ Person/Author
	if ( is_front_page() || is_home() ) {
		$schemas[] = array(
			'@context'        => 'https://schema.org',
			'@type'           => 'WebSite',
			'name'            => $site_name,
			'alternateName'   => 'オスカーの日本語学習帳',
			'url'             => $site_url,
			'description'     => $site_desc,
			'inLanguage'      => 'ja',
			'image'           => $og_image,
			'author'          => array(
				'@type' => 'Person',
				'name'  => 'オスカー',
				'url'   => 'https://oscarchair.jp/',
				'image' => $logo_url,
			),
			'publisher'       => array(
				'@type' => 'Person',
				'name'  => 'オスカー',
				'url'   => 'https://oscarchair.jp/',
				'image' => $logo_url,
			),
			'potentialAction' => array(
				'@type'       => 'SearchAction',
				'target'      => array(
					'@type'       => 'EntryPoint',
					'urlTemplate' => $site_url . '?s={search_term_string}',
				),
				'query-input' => 'required name=search_term_string',
			),
		);
	}

	// 3. 記事ページ: BlogPosting
	if ( is_single() ) {
		global $post;
		$author_name = 'オスカー';
		$author_url  = 'https://oscarchair.jp/';
		$image_url   = has_post_thumbnail( $post->ID )
			? get_the_post_thumbnail_url( $post->ID, 'full' )
			: OSCSS_THEME_URI . '/assets/images/og-image.png';

		$cat_name = '';
		$categories = get_the_category( $post->ID );
		if ( ! empty( $categories ) ) {
			$cat_name = $categories[0]->name;
		}

		$post_schema = array(
			'@context'         => 'https://schema.org',
			'@type'            => 'BlogPosting',
			'mainEntityOfPage' => array(
				'@type' => 'WebPage',
				'@id'   => get_permalink( $post->ID ),
			),
			'headline'         => oscss_get_clean_title( $post->ID ),
			'description'      => oscss_get_clean_excerpt( $post, 120 ),
			'image'            => array(
				'@type' => 'ImageObject',
				'url'   => $image_url,
			),
			'datePublished'    => get_the_date( 'c', $post->ID ),
			'dateModified'     => get_the_modified_date( 'c', $post->ID ),
			'author'           => array(
				'@type' => 'Person',
				'name'  => $author_name,
				'url'   => $author_url,
				'image' => $logo_url,
			),
			'publisher'        => array(
				'@type' => 'Organization',
				'name'  => $site_name,
				'url'   => $site_url,
				'logo'  => array(
					'@type' => 'ImageObject',
					'url'   => $logo_url,
				),
			),
			'inLanguage'       => 'ja',
		);

		if ( $cat_name ) {
			$post_schema['articleSection'] = $cat_name;
		}

		$schemas[] = $post_schema;
	}

	// JSON-LD 出力
	if ( ! empty( $schemas ) ) {
		echo "\n<!-- oscss-wp-nihongo JSON-LD Structured Data -->\n";
		foreach ( $schemas as $schema ) {
			echo '<script type="application/ld+json">' . "\n";
			echo wp_json_encode( $schema, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT ) . "\n";
			echo "</script>\n";
		}
		echo "<!-- /oscss-wp-nihongo JSON-LD Structured Data -->\n\n";
	}
}
add_action( 'wp_head', 'oscss_seo_json_ld', 2 );

/**
 * 構造化データ用のパンくずアイテム配列を生成
 *
 * @return array
 */
function oscss_get_breadcrumb_schema_items() {
	if ( is_front_page() ) {
		return array();
	}

	$items = array();
	$items[] = array(
		'@type'    => 'ListItem',
		'position' => 1,
		'name'     => 'ホーム',
		'item'     => home_url( '/' ),
	);

	$pos = 2;

	if ( is_single() ) {
		$categories = get_the_category();
		if ( ! empty( $categories ) ) {
			$cat = $categories[0];
			$items[] = array(
				'@type'    => 'ListItem',
				'position' => $pos,
				'name'     => $cat->name,
				'item'     => get_category_link( $cat->term_id ),
			);
			$pos++;
		}
		$items[] = array(
			'@type'    => 'ListItem',
			'position' => $pos,
			'name'     => oscss_get_clean_title(),
			'item'     => get_permalink(),
		);
	} elseif ( is_page() ) {
		global $post;
		if ( $post && $post->post_parent ) {
			$ancestors = array_reverse( get_post_ancestors( $post->ID ) );
			foreach ( $ancestors as $ancestor ) {
				$items[] = array(
					'@type'    => 'ListItem',
					'position' => $pos,
					'name'     => oscss_get_clean_title( $ancestor ),
					'item'     => get_permalink( $ancestor ),
				);
				$pos++;
			}
		}
		$items[] = array(
			'@type'    => 'ListItem',
			'position' => $pos,
			'name'     => oscss_get_clean_title(),
			'item'     => get_permalink(),
		);
	} elseif ( is_category() ) {
		$items[] = array(
			'@type'    => 'ListItem',
			'position' => $pos,
			'name'     => single_cat_title( '', false ),
			'item'     => get_category_link( get_queried_object_id() ),
		);
	} elseif ( is_tag() ) {
		$items[] = array(
			'@type'    => 'ListItem',
			'position' => $pos,
			'name'     => single_tag_title( '', false ),
			'item'     => get_tag_link( get_queried_object_id() ),
		);
	} elseif ( is_search() ) {
		$items[] = array(
			'@type'    => 'ListItem',
			'position' => $pos,
			'name'     => '検索: ' . get_search_query(),
			'item'     => get_search_link(),
		);
	} elseif ( is_404() ) {
		$items[] = array(
			'@type'    => 'ListItem',
			'position' => $pos,
			'name'     => '404 Not Found',
			'item'     => home_url( '/404' ),
		);
	}

	return $items;
}

/**
 * 3. パフォーマンス最適化: Preconnect & DNS-Prefetch
 */
function oscss_seo_resource_hints() {
	?>
	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link rel="dns-prefetch" href="//pagead2.googlesyndication.com">
	<link rel="dns-prefetch" href="//www.googletagmanager.com">
	<?php
}
add_action( 'wp_head', 'oscss_seo_resource_hints', 0 );

/**
 * 4. クリーンアップ: 不要なWordPressデフォルトタグ・Emojiの除去
 */
function oscss_cleanup_wp_head() {
	// 不要なメタ・リンクの削除
	remove_action( 'wp_head', 'wp_generator' );
	remove_action( 'wp_head', 'rsd_link' );
	remove_action( 'wp_head', 'wlwmanifest_link' );
	remove_action( 'wp_head', 'wp_shortlink_wp_head', 10 );
	remove_action( 'wp_head', 'feed_links', 2 );
	remove_action( 'wp_head', 'feed_links_extra', 3 );

	// Emojiスクリプト・スタイルの無効化（高速化）
	remove_action( 'wp_head', 'print_emoji_detection_script', 7 );
	remove_action( 'admin_print_scripts', 'print_emoji_detection_script' );
	remove_action( 'wp_print_styles', 'print_emoji_styles' );
	remove_action( 'admin_print_styles', 'print_emoji_styles' );
	remove_filter( 'the_content_feed', 'wp_staticize_emoji' );
	remove_filter( 'comment_text_rss', 'wp_staticize_emoji' );
	remove_filter( 'wp_mail', 'wp_staticize_emoji_for_email' );
}
add_action( 'init', 'oscss_cleanup_wp_head' );

/**
 * 5. 旧カテゴリースラッグの 301 リダイレクト（SEO評価の継承・404防止）
 */
function oscss_legacy_category_redirect() {
	if ( is_admin() ) {
		return;
	}

	$request_uri = isset( $_SERVER['REQUEST_URI'] ) ? rawurldecode( $_SERVER['REQUEST_URI'] ) : '';

	// 旧ことばのあや -> 新 kotoba-no-aya
	if ( strpos( $request_uri, '/category/aya-of-words' ) !== false ) {
		wp_safe_redirect( home_url( '/category/kotoba-no-aya/' ), 301 );
		exit;
	}

	// 旧くらべてみました (日本語スラッグ等) -> 新 comparing
	if ( strpos( $request_uri, '/category/くらべてみました' ) !== false || strpos( $request_uri, '/category/comparing-japanese' ) !== false ) {
		wp_safe_redirect( home_url( '/category/comparing/' ), 301 );
		exit;
	}

	// 旧カルチャーショック (日本語スラッグ) -> 新 culture-shock
	if ( strpos( $request_uri, '/category/カルチャーショック' ) !== false ) {
		wp_safe_redirect( home_url( '/category/culture-shock/' ), 301 );
		exit;
	}
}
add_action( 'template_redirect', 'oscss_legacy_category_redirect' );
