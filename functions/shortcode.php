<?php
/**
 * Shortcodes for oscss-wp-nihongo (オスカーの日本語学習帳)
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * 1. くらべてみました VS比較カード
 * 例: [nihongo_vs word1="ごめんなさい" desc1="自分が悪いと認めて謝罪するとき" word2="すみません" desc2="相手に迷惑をかけたとき・呼びかけ"]
 */
function oscss_nihongo_vs_shortcode( $atts ) {
	$atts = shortcode_atts(
		array(
			'title' => '表現の違いをくらべてみました',
			'word1' => '言葉A',
			'desc1' => '',
			'word2' => '言葉B',
			'desc2' => '',
		),
		$atts,
		'nihongo_vs'
	);

	$title = wp_kses_post( $atts['title'] );
	$word1 = wp_kses_post( $atts['word1'] );
	$desc1 = wp_kses_post( $atts['desc1'] );
	$word2 = wp_kses_post( $atts['word2'] );
	$desc2 = wp_kses_post( $atts['desc2'] );

	return sprintf(
		'<div class="c-nihongo-vs">
			<div class="c-nihongo-vs__header">🔍 %1$s</div>
			<div class="c-nihongo-vs__grid">
				<div class="c-nihongo-vs__col">
					<span class="c-nihongo-vs__badge c-nihongo-vs__badge--left">表現 1</span>
					<div class="c-nihongo-vs__word">%2$s</div>
					<div class="c-nihongo-vs__desc">%3$s</div>
				</div>
				<div class="c-nihongo-vs__col">
					<span class="c-nihongo-vs__badge c-nihongo-vs__badge--right">表現 2</span>
					<div class="c-nihongo-vs__word">%4$s</div>
					<div class="c-nihongo-vs__desc">%5$s</div>
				</div>
			</div>
		</div>',
		$title,
		$word1,
		$desc1,
		$word2,
		$desc2
	);
}
add_shortcode( 'nihongo_vs', 'oscss_nihongo_vs_shortcode' );

/**
 * 2. ことばのあや ニュアンス解説ボックス
 * 例: [nihongo_nuance word="終助詞「よ」" meaning="情報提供や注意喚起" example="「駅はこの先にあるよ」"]
 */
function oscss_nihongo_nuance_shortcode( $atts ) {
	$atts = shortcode_atts(
		array(
			'word'    => 'ことばのあや',
			'meaning' => '',
			'example' => '',
		),
		$atts,
		'nihongo_nuance'
	);

	$word    = wp_kses_post( $atts['word'] );
	$meaning = wp_kses_post( $atts['meaning'] );
	$example = wp_kses_post( $atts['example'] );

	$html  = '<div class="c-nihongo-nuance">';
	$html .= '<div class="c-nihongo-nuance__word">💡 ' . $word . '</div>';
	if ( $meaning ) {
		$html .= '<div class="c-nihongo-nuance__body"><strong>意味・機能:</strong> ' . $meaning . '</div>';
	}
	if ( $example ) {
		$html .= '<div class="c-nihongo-nuance__body" style="margin-top:6px;"><strong>例文:</strong> <em>' . $example . '</em></div>';
	}
	$html .= '</div>';

	return $html;
}
add_shortcode( 'nihongo_nuance', 'oscss_nihongo_nuance_shortcode' );

/**
 * 3. 著者プロフィールボックス
 * 例: [oscss_author_box]
 */
function oscss_author_box_shortcode() {
	ob_start();
	get_template_part( 'template-parts/author-box' );
	return ob_get_clean();
}
add_shortcode( 'oscss_author_box', 'oscss_author_box_shortcode' );

/**
 * 4. CTAボタンショートコード
 */
function oscss_btn_shortcode( $atts ) {
	$atts = shortcode_atts(
		array(
			'url'    => '#',
			'text'   => '詳細を見る',
			'style'  => 'primary',
			'target' => '_self',
			'align'  => 'left',
		),
		$atts,
		'oscss_btn'
	);

	$url    = esc_url( $atts['url'] );
	$text   = esc_html( $atts['text'] );
	$style  = sanitize_html_class( $atts['style'] );
	$target = esc_attr( $atts['target'] );
	$align  = sanitize_html_class( $atts['align'] );
	$rel    = ( '_blank' === $target ) ? ' rel="noopener noreferrer"' : '';

	return sprintf(
		'<div class="c-btn-wrapper u-text-%1$s"><a href="%2$s" class="c-btn c-btn--%3$s" target="%4$s"%5$s>%6$s</a></div>',
		$align,
		$url,
		$style,
		$target,
		$rel,
		$text
	);
}
add_shortcode( 'oscss_btn', 'oscss_btn_shortcode' );

/**
 * 5. インライン関連記事ブログカードショートコード
 * 例: [oscss_related slug="street-japanese-convenience-store-register-survival-guide" label="あわせて読みたい"]
 *     [oscss_related id="123"]
 */
function oscss_related_post_shortcode( $atts ) {
	$atts = shortcode_atts(
		array(
			'id'    => '',
			'slug'  => '',
			'label' => 'あわせて読みたい',
		),
		$atts,
		'oscss_related'
	);

	$target_post = null;
	if ( ! empty( $atts['id'] ) ) {
		$target_post = get_post( (int) $atts['id'] );
		// 未公開（future等）の場合は非表示にする
		if ( $target_post && 'publish' !== $target_post->post_status ) {
			$target_post = null;
		}
	} elseif ( ! empty( $atts['slug'] ) ) {
		$posts = get_posts(
			array(
				'name'        => sanitize_title( $atts['slug'] ),
				'post_type'   => 'post',
				'post_status' => 'publish', // 公開済みのみ取得（予約投稿中は非表示）
				'numberposts' => 1,
			)
		);
		if ( ! empty( $posts ) ) {
			$target_post = $posts[0];
		}
	}

	if ( ! $target_post ) {
		return ''; // 未公開または存在しない場合は空文字（完全非表示）
	}

	$post_id   = $target_post->ID;
	$permalink = get_permalink( $post_id );
	$title     = get_the_title( $post_id );
	$thumb_url = oscss_get_thumbnail_url( $post_id, 'medium' );
	$excerpt   = oscss_get_clean_excerpt( $target_post, 90 );
	$label     = wp_kses_post( $atts['label'] );

	return sprintf(
		'<aside class="c-blog-card-wrap">
			<a href="%1$s" class="c-blog-card">
				<div class="c-blog-card__inner">
					<div class="c-blog-card__media">
						<img src="%2$s" alt="%3$s" class="c-blog-card__img" loading="lazy" width="140" height="100">
					</div>
					<div class="c-blog-card__body">
						<span class="c-blog-card__label">📖 %4$s</span>
						<div class="c-blog-card__title">%5$s</div>
						<div class="c-blog-card__desc">%6$s</div>
					</div>
				</div>
			</a>
		</aside>',
		esc_url( $permalink ),
		esc_url( $thumb_url ),
		esc_attr( oscss_get_clean_title( $post_id ) ),
		$label,
		wp_kses_post( $title ),
		esc_html( $excerpt )
	);
}
add_shortcode( 'oscss_related', 'oscss_related_post_shortcode' );

/**
 * 6. 連載シリーズ自動バックナンバーショートコード
 * 例: [oscss_series]
 *     [oscss_series category="street-japanese" title="🗺️ 「街角サバイバル」連載シリーズ"]
 *
 * 公開済み（publish）の記事のみを日付昇順（第1弾、第2弾…）で自動表示。
 * 予約投稿中（future）の記事は絶対に表示されず、公開日を迎えた瞬間に自動でリストに追加されます。
 */
function oscss_series_list_shortcode( $atts ) {
	$current_id = get_the_ID();

	// デフォルトで現在の投稿の最初のカテゴリーを取得
	$default_cat = '';
	if ( $current_id ) {
		$cats = wp_get_post_categories( $current_id );
		if ( ! empty( $cats ) ) {
			$term = get_term( $cats[0] );
			if ( $term && ! is_wp_error( $term ) ) {
				$default_cat = $term->slug;
			}
		}
	}

	$atts = shortcode_atts(
		array(
			'category' => $default_cat,
			'title'    => '🗺️ 連載バックナンバー（公開済みエピソード）',
		),
		$atts,
		'oscss_series'
	);

	if ( empty( $atts['category'] ) ) {
		return '';
	}

	// 公開済み（publish）の記事のみを日付昇順で取得
	$posts = get_posts(
		array(
			'category_name' => sanitize_title( $atts['category'] ),
			'post_status'   => 'publish',
			'orderby'       => 'date',
			'order'         => 'ASC',
			'numberposts'   => 50,
		)
	);

	if ( empty( $posts ) ) {
		return '';
	}

	$title      = wp_kses_post( $atts['title'] );
	$items_html = '';
	$index      = 1;

	foreach ( $posts as $p ) {
		$is_current = ( $p->ID === $current_id );
		$item_title = wp_kses_post( get_the_title( $p->ID ) );
		$url        = esc_url( get_permalink( $p->ID ) );

		if ( $is_current ) {
			$items_html .= sprintf(
				'<li class="c-series-list__item c-series-list__item--current"><span class="c-series-list__badge">第%d弾</span><span class="c-series-list__text">%s</span><span class="c-series-list__current-label">（今読んでいる記事）</span></li>',
				$index,
				$item_title
			);
		} else {
			$items_html .= sprintf(
				'<li class="c-series-list__item"><span class="c-series-list__badge">第%d弾</span><a href="%s" class="c-series-list__link">%s</a></li>',
				$index,
				$url,
				$item_title
			);
		}
		$index++;
	}

	return sprintf(
		'<aside class="c-series-box"><div class="c-series-box__header">%s</div><ul class="c-series-list">%s</ul></aside>',
		$title,
		$items_html
	);
}
add_shortcode( 'oscss_series', 'oscss_series_list_shortcode' );


