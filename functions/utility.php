<?php
/**
 * Utility functions for oscss-wp-nihongo
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * 投稿のサムネイルURLを取得（フォールバック付き）
 *
 * @param int|WP_Post|null $post 投稿IDまたはオブジェクト
 * @param string           $size 画像サイズ
 * @return string 画像URL
 */
function oscss_get_thumbnail_url( $post = null, $size = 'medium_large' ) {
	$post_id = get_post( $post ) ? get_post( $post )->ID : get_the_ID();
	if ( has_post_thumbnail( $post_id ) ) {
		$url = get_the_post_thumbnail_url( $post_id, $size );
		if ( $url ) {
			return $url;
		}
	}
	// デフォルトプレースホルダー画像
	return OSCSS_THEME_URI . '/assets/images/placeholder.svg';
}

/**
 * サイト統一のモダンなインラインSVGアイコンを出力
 *
 * @param string $name アイコン名（calendar, eye, clock, fire, tag など）
 * @param int    $size アイコンサイズ（px）
 * @return string SVGマークアップ
 */
function oscss_get_icon( $name, $size = 14 ) {
	$icons = array(
		'calendar' => '<svg class="c-icon c-icon--calendar" width="' . (int)$size . '" height="' . (int)$size . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>',
		'eye'      => '<svg class="c-icon c-icon--eye" width="' . (int)$size . '" height="' . (int)$size . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>',
		'clock'    => '<svg class="c-icon c-icon--clock" width="' . (int)$size . '" height="' . (int)$size . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>',
		'fire'     => '<svg class="c-icon c-icon--fire" width="' . (int)$size . '" height="' . (int)$size . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 3z"></path></svg>',
		'tag'      => '<svg class="c-icon c-icon--tag" width="' . (int)$size . '" height="' . (int)$size . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>',
	);

	return isset( $icons[ $name ] ) ? $icons[ $name ] : '';
}

/**
 * 投稿日・更新日のHTMLを出力
 */
function oscss_posted_on() {
	$time_string = '<time class="entry-date published" datetime="%1$s">%2$s</time>';
	if ( get_the_time( 'U' ) !== get_the_modified_time( 'U' ) ) {
		$time_string = '<time class="entry-date published" datetime="%1$s">%2$s</time><time class="updated" datetime="%3$s">（更新: %4$s）</time>';
	}

	$time_string = sprintf(
		$time_string,
		esc_attr( get_the_date( DATE_W3C ) ),
		esc_html( get_the_date() ),
		esc_attr( get_the_modified_date( DATE_W3C ) ),
		esc_html( get_the_modified_date() )
	);

	echo '<span class="c-post-meta__item c-post-meta__date"><span class="c-post-meta__icon" aria-hidden="true">' . oscss_get_icon( 'calendar', 13 ) . '</span> ' . $time_string . '</span>'; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
}

/**
 * カテゴリーバッジを出力
 */
function oscss_entry_category() {
	$categories = get_the_category();
	if ( ! empty( $categories ) ) {
		echo '<div class="c-post-meta__categories">';
		foreach ( $categories as $category ) {
			printf(
				'<a href="%1$s" class="c-badge c-badge--category">%2$s</a>',
				esc_url( get_category_link( $category->term_id ) ),
				esc_html( $category->name )
			);
		}
		echo '</div>';
	}
}

/**
 * パンくずリストを出力
 */
function oscss_breadcrumb() {
	if ( is_front_page() ) {
		return;
	}

	echo '<nav class="c-breadcrumb" aria-label="パンくずリスト">';
	echo '<ol class="c-breadcrumb__list" itemscope itemtype="https://schema.org/BreadcrumbList">';

	// ホーム
	echo '<li class="c-breadcrumb__item" itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">';
	echo '<a class="c-breadcrumb__link" itemprop="item" href="' . esc_url( home_url( '/' ) ) . '"><span itemprop="name">ホーム</span></a>';
	echo '<meta itemprop="position" content="1" />';
	echo '</li>';

	$position = 2;

	if ( is_single() ) {
		$categories = get_the_category();
		if ( ! empty( $categories ) ) {
			$cat = $categories[0];
			echo '<li class="c-breadcrumb__item" itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">';
			echo '<a class="c-breadcrumb__link" itemprop="item" href="' . esc_url( get_category_link( $cat->term_id ) ) . '"><span itemprop="name">' . esc_html( $cat->name ) . '</span></a>';
			echo '<meta itemprop="position" content="' . esc_attr( (string) $position ) . '" />';
			echo '</li>';
			$position++;
		}
		echo '<li class="c-breadcrumb__item c-breadcrumb__item--current" itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem" aria-current="page">';
		echo '<span itemprop="name">' . esc_html( wp_trim_words( get_the_title(), 20, '...' ) ) . '</span>';
		echo '<meta itemprop="position" content="' . esc_attr( (string) $position ) . '" />';
		echo '</li>';
	} elseif ( is_page() ) {
		global $post;
		if ( $post->post_parent ) {
			$ancestors = array_reverse( get_post_ancestors( $post->ID ) );
			foreach ( $ancestors as $ancestor ) {
				echo '<li class="c-breadcrumb__item" itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">';
				echo '<a class="c-breadcrumb__link" itemprop="item" href="' . esc_url( get_permalink( $ancestor ) ) . '"><span itemprop="name">' . esc_html( get_the_title( $ancestor ) ) . '</span></a>';
				echo '<meta itemprop="position" content="' . esc_attr( (string) $position ) . '" />';
				echo '</li>';
				$position++;
			}
		}
		echo '<li class="c-breadcrumb__item c-breadcrumb__item--current" itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem" aria-current="page">';
		echo '<span itemprop="name">' . esc_html( get_the_title() ) . '</span>';
		echo '<meta itemprop="position" content="' . esc_attr( (string) $position ) . '" />';
		echo '</li>';
	} elseif ( is_category() ) {
		echo '<li class="c-breadcrumb__item c-breadcrumb__item--current" itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem" aria-current="page">';
		echo '<span itemprop="name">' . esc_html( single_cat_title( '', false ) ) . '</span>';
		echo '<meta itemprop="position" content="' . esc_attr( (string) $position ) . '" />';
		echo '</li>';
	} elseif ( is_archive() ) {
		echo '<li class="c-breadcrumb__item c-breadcrumb__item--current" itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem" aria-current="page">';
		echo '<span itemprop="name">' . esc_html( get_the_archive_title() ) . '</span>';
		echo '<meta itemprop="position" content="' . esc_attr( (string) $position ) . '" />';
		echo '</li>';
	} elseif ( is_search() ) {
		echo '<li class="c-breadcrumb__item c-breadcrumb__item--current" itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem" aria-current="page">';
		echo '<span itemprop="name">検索結果: ' . esc_html( get_search_query() ) . '</span>';
		echo '<meta itemprop="position" content="' . esc_attr( (string) $position ) . '" />';
		echo '</li>';
	} elseif ( is_404() ) {
		echo '<li class="c-breadcrumb__item c-breadcrumb__item--current" itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem" aria-current="page">';
		echo '<span itemprop="name">ページが見つかりません</span>';
		echo '<meta itemprop="position" content="' . esc_attr( (string) $position ) . '" />';
		echo '</li>';
	}

	echo '</ol>';
	echo '</nav>';
}

/**
 * カスタムコメント出力コールバック
 *
 * @param WP_Comment $comment コメントオブジェクト
 * @param array      $args    引数
 * @param int        $depth   階層の深さ
 */
function oscss_custom_comment( $comment, $args, $depth ) {
	$tag = ( 'div' === $args['style'] ) ? 'div' : 'li';
	?>
	<<?php echo esc_attr( $tag ); ?> id="comment-<?php comment_ID(); ?>" <?php comment_class( empty( $args['has_children'] ) ? 'c-comment' : 'c-comment c-comment--parent' ); ?>>
		<article id="div-comment-<?php comment_ID(); ?>" class="c-comment__body">
			<header class="c-comment__header">
				<div class="c-comment__avatar">
					<?php
					if ( 0 != $args['avatar_size'] ) {
						echo get_avatar( $comment, $args['avatar_size'] );
					}
					?>
				</div>
				<div class="c-comment__meta">
					<div class="c-comment__author">
						<?php printf( '<span class="c-comment__author-name">%s</span>', get_comment_author_link() ); ?>
						<?php
						$post = get_post( $comment->comment_post_ID );
						if ( $post && $comment->user_id === $post->post_author ) {
							echo '<span class="c-badge c-badge--accent" style="font-size: 11px; padding: 2px 6px; margin-left: 6px;">著者</span>';
						}
						?>
					</div>
					<div class="c-comment__date">
						<a href="<?php echo esc_url( get_comment_link( $comment->comment_ID ) ); ?>">
							<time datetime="<?php comment_time( 'c' ); ?>">
								<?php printf( esc_html__( '%1$s %2$s', 'oscss-wp-nihongo' ), get_comment_date(), get_comment_time() ); ?>
							</time>
						</a>
					</div>
				</div>
			</header>

			<?php if ( '0' == $comment->comment_approved ) : ?>
				<p class="c-comment__awaiting-moderation"><?php esc_html_e( '※ あなたのコメントは承認待ちです。', 'oscss-wp-nihongo' ); ?></p>
			<?php endif; ?>

			<div class="c-comment__content c-prose">
				<?php comment_text(); ?>
			</div>

			<div class="c-comment__reply">
				<?php
				comment_reply_link(
					array_merge(
						$args,
						array(
							'add_below' => 'div-comment',
							'depth'     => $depth,
							'max_depth' => $args['max_depth'],
							'before'    => '<span class="c-comment__reply-link">',
							'after'     => '</span>',
						)
					)
				);
				?>
			</div>
		</article>
	<?php
}

/**
 * 投稿の閲覧数を取得
 *
 * @param int|null $post_id 投稿ID（nullの場合は現在の投稿）
 * @return int 閲覧数
 */
function oscss_get_post_views( $post_id = null ) {
	if ( ! $post_id ) {
		$post_id = get_the_ID();
	}
	$views = get_post_meta( $post_id, '_oscss_post_views', true );
	return ! empty( $views ) ? (int) $views : 0;
}

/**
 * 投稿の閲覧数を1カウントアップ
 *
 * @param int $post_id 投稿ID
 * @return int 更新後の閲覧数
 */
function oscss_set_post_views( $post_id ) {
	if ( ! $post_id || ! is_numeric( $post_id ) ) {
		return 0;
	}
	$post_id = (int) $post_id;
	$views = (int) get_post_meta( $post_id, '_oscss_post_views', true );
	$views++;
	update_post_meta( $post_id, '_oscss_post_views', $views );
	return $views;
}

/**
 * 閲覧数メタ表示HTMLを出力
 *
 * @param int|null $post_id 投稿ID
 */
function oscss_posted_views( $post_id = null ) {
	$views = oscss_get_post_views( $post_id );
	printf(
		'<span class="c-post-meta__item c-post-meta__views" title="%1$s"><span class="c-post-meta__icon" aria-hidden="true">%2$s</span> %3$s views</span>',
		esc_attr( sprintf( __( '閲覧数: %d回', 'oscss-wp-nihongo' ), $views ) ),
		oscss_get_icon( 'eye', 13 ),
		esc_html( number_format_i18n( $views ) )
	);
}

/**
 * 現在の投稿一覧並び順（latest / views）を取得
 * 優先順位: 1. URLパラメータ ?sort= 2. Cookie oscss_post_sort 3. デフォルト 'latest'
 *
 * @return string 'latest' または 'views'
 */
function oscss_get_current_sort() {
	if ( isset( $_GET['sort'] ) ) {
		$sort = sanitize_key( $_GET['sort'] );
		if ( in_array( $sort, array( 'latest', 'views' ), true ) ) {
			return $sort;
		}
	}

	if ( isset( $_COOKIE['oscss_post_sort'] ) ) {
		$cookie_sort = sanitize_key( $_COOKIE['oscss_post_sort'] );
		if ( in_array( $cookie_sort, array( 'latest', 'views' ), true ) ) {
			return $cookie_sort;
		}
	}

	return 'latest';
}

/**
 * 一覧画面用のソート切り替えタブHTMLを出力
 *
 * @param string $current_sort 現在のソート（'latest' または 'views'）
 * @param string $anchor       ページ内アンカー（例: '#latest-posts'）
 */
function oscss_render_sort_tabs( $current_sort = 'latest', $anchor = '' ) {
	// 現在のURLを取得し、sortパラメータを差し替えるURLを生成
	$current_url = remove_query_arg( 'sort' );
	if ( is_front_page() ) {
		$current_url = home_url( '/' );
	}

	$latest_url = add_query_arg( 'sort', 'latest', $current_url ) . $anchor;
	$views_url  = add_query_arg( 'sort', 'views', $current_url ) . $anchor;

	$is_latest = ( 'views' !== $current_sort );
	$is_views  = ( 'views' === $current_sort );
	?>
	<div class="c-sort-tabs" role="tablist" aria-label="<?php esc_attr_e( '記事の並び替え', 'oscss-wp-nihongo' ); ?>">
		<a href="<?php echo esc_url( $latest_url ); ?>"
		   class="c-sort-tab <?php echo $is_latest ? 'is-active' : ''; ?>"
		   role="tab"
		   aria-selected="<?php echo $is_latest ? 'true' : 'false'; ?>"
		   data-sort="latest">
			<span class="c-sort-tab__icon" aria-hidden="true"><?php echo oscss_get_icon( 'clock', 14 ); ?></span>
			<span class="c-sort-tab__text"><?php esc_html_e( '新着順', 'oscss-wp-nihongo' ); ?></span>
		</a>
		<a href="<?php echo esc_url( $views_url ); ?>"
		   class="c-sort-tab <?php echo $is_views ? 'is-active' : ''; ?>"
		   role="tab"
		   aria-selected="<?php echo $is_views ? 'true' : 'false'; ?>"
		   data-sort="views">
			<span class="c-sort-tab__icon" aria-hidden="true"><?php echo oscss_get_icon( 'fire', 14 ); ?></span>
			<span class="c-sort-tab__text"><?php esc_html_e( '閲覧数順', 'oscss-wp-nihongo' ); ?></span>
		</a>
	</div>
	<?php
}

/**
 * 現在のページの正規化（Canonical）URLを取得
 *
 * @return string
 */
function oscss_get_canonical_url() {
	if ( is_front_page() ) {
		return home_url( '/' );
	} elseif ( is_home() ) {
		$page_for_posts = get_option( 'page_for_posts' );
		return $page_for_posts ? get_permalink( $page_for_posts ) : home_url( '/' );
	} elseif ( is_single() || is_page() ) {
		return get_permalink();
	} elseif ( is_category() ) {
		return get_category_link( get_queried_object_id() );
	} elseif ( is_tag() ) {
		return get_tag_link( get_queried_object_id() );
	} elseif ( is_author() ) {
		return get_author_posts_url( get_queried_object_id() );
	} elseif ( is_archive() ) {
		return get_post_type_archive_link( get_post_type() );
	} else {
		$schema = is_ssl() ? 'https://' : 'http://';
		$host   = isset( $_SERVER['HTTP_HOST'] ) ? sanitize_text_field( wp_unslash( $_SERVER['HTTP_HOST'] ) ) : '';
		$uri    = isset( $_SERVER['REQUEST_URI'] ) ? sanitize_text_field( wp_unslash( $_SERVER['REQUEST_URI'] ) ) : '';
		return esc_url_raw( $schema . $host . $uri );
	}
}

/**
 * 記事や固定ページのクリーンなテキスト要約（メタタグ・OGP用）を取得
 *
 * @param int|WP_Post|null $post 投稿オブジェクトまたはID
 * @param int              $length 切り詰め文字数
 * @return string
 */
function oscss_get_clean_excerpt( $post = null, $length = 120 ) {
	$post = get_post( $post );
	if ( ! $post ) {
		return '';
	}

	$text = '';
	if ( ! empty( $post->post_excerpt ) ) {
		$text = $post->post_excerpt;
	} else {
		$text = $post->post_content;
		// ショートコード削除
		$text = strip_shortcodes( $text );
		// HTMLタグ除去
		$text = wp_strip_all_tags( $text );
		// Markdown記号除去 (#, *, _, `, >, etc.)
		$text = preg_replace( '/[#*_`>\[\]\(\)]+/', '', $text );
		// 余計な改行・連続空白を単一スペース化
		$text = preg_replace( '/\s+/', ' ', $text );
	}

	$text = trim( $text );
	if ( mb_strlen( $text, 'UTF-8' ) > $length ) {
		$text = mb_substr( $text, 0, $length, 'UTF-8' ) . '...';
	}

	return $text;
}

/**
 * 記事の読了目安時間（分）を算出（日本語 500文字/分 基準）
 *
 * @param int|WP_Post|null $post 投稿オブジェクトまたはID
 * @return int 読了目安時間（分）
 */
function oscss_get_reading_time( $post = null ) {
	$post = get_post( $post );
	if ( ! $post ) {
		return 1;
	}

	$content = strip_shortcodes( $post->post_content );
	$content = wp_strip_all_tags( $content );
	$content = preg_replace( '/\s+/', '', $content );
	$char_count = mb_strlen( $content, 'UTF-8' );

	$minutes = (int) ceil( $char_count / 500 );
	return max( 1, $minutes );
}

/**
 * 読了目安時間のHTMLを出力
 *
 * @param int|WP_Post|null $post 投稿オブジェクトまたはID
 */
function oscss_posted_reading_time( $post = null ) {
	$time = oscss_get_reading_time( $post );
	printf(
		'<span class="c-post-meta__item c-post-meta__reading-time" title="%1$s"><span class="c-post-meta__icon" aria-hidden="true">%2$s</span> 読了目安 約%3$d分</span>',
		esc_attr( sprintf( __( '読了目安: 約%d分', 'oscss-wp-nihongo' ), $time ) ),
		oscss_get_icon( 'clock', 13 ),
		(int) $time
	);
}

/**
 * 連載カテゴリーの定義・メタ情報一覧を取得
 *
 * @return array
 */
function oscss_get_series_categories() {
	return array(
		'comparing' => array(
			'slugs'       => array( 'comparing', 'くらべてみました' ),
			'name'        => 'くらべてみました',
			'icon'        => '🔍',
			'badge_class' => 'c-badge--vs',
			'desc'        => '「ごめんなさい」と「すみません」など、似ているようで異なる表現の違いを徹底比較。',
			'lead'        => '似ている言葉や文化の違いを比較',
		),
		'kotoba-no-aya' => array(
			'slugs'       => array( 'kotoba-no-aya', 'aya-of-words', 'ことばのあや' ),
			'name'        => 'ことばのあや',
			'icon'        => '🗣️',
			'badge_class' => 'c-badge--aya',
			'desc'        => '終助詞「ね」「よ」「よね」の使い方など、相手とスムーズに会話するためのニュアンスを解説。',
			'lead'        => '助詞や言葉のニュアンス解説',
		),
		'culture-shock' => array(
			'slugs'       => array( 'culture-shock', 'カルチャーショック' ),
			'name'        => 'カルチャーショック',
			'icon'        => '🌏',
			'badge_class' => 'c-badge--culture',
			'desc'        => '日本の習慣や食文化、香港と日本のコミュニケーション感覚の違いをリアルに綴ります。',
			'lead'        => '日本と海外の習慣・日常の発見',
		),
	);
}

/**
 * 連載カテゴリーのアーカイブURLを取得（スラッグ柔軟解決）
 *
 * @param string $series_key 'comparing' | 'kotoba-no-aya' | 'culture-shock'
 * @return string カテゴリーURL
 */
function oscss_get_series_category_url( $series_key ) {
	$series = oscss_get_series_categories();
	if ( ! isset( $series[ $series_key ] ) ) {
		return home_url( '/' );
	}

	$slugs = $series[ $series_key ]['slugs'];
	foreach ( $slugs as $slug ) {
		$term = get_category_by_slug( $slug );
		if ( $term ) {
			return get_category_link( $term->term_id );
		}
		// 名前の直接検索フォールバック
		$term_by_name = get_term_by( 'name', $slug, 'category' );
		if ( $term_by_name ) {
			return get_category_link( $term_by_name->term_id );
		}
	}

	// 見つからなかった場合のURLフォールバック
	return home_url( '/category/' . rawurlencode( $slugs[0] ) . '/' );
}


