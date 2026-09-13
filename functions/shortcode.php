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

	$title = esc_html( $atts['title'] );
	$word1 = esc_html( $atts['word1'] );
	$desc1 = wp_kses_post( $atts['desc1'] );
	$word2 = esc_html( $atts['word2'] );
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

	$word    = esc_html( $atts['word'] );
	$meaning = esc_html( $atts['meaning'] );
	$example = esc_html( $atts['example'] );

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
	} elseif ( ! empty( $atts['slug'] ) ) {
		$posts = get_posts(
			array(
				'name'        => sanitize_title( $atts['slug'] ),
				'post_type'   => 'post',
				'post_status' => array( 'publish', 'future' ),
				'numberposts' => 1,
			)
		);
		if ( ! empty( $posts ) ) {
			$target_post = $posts[0];
		}
	}

	if ( ! $target_post ) {
		return '';
	}

	$post_id   = $target_post->ID;
	$permalink = get_permalink( $post_id );
	$title     = get_the_title( $post_id );
	$thumb_url = oscss_get_thumbnail_url( $post_id, 'medium' );
	$excerpt   = oscss_get_clean_excerpt( $target_post, 90 );
	$label     = esc_html( $atts['label'] );

	return sprintf(
		'<aside class="c-blog-card-wrap">
			<a href="%1$s" class="c-blog-card">
				<div class="c-blog-card__inner">
					<div class="c-blog-card__media">
						<img src="%2$s" alt="%3$s" class="c-blog-card__img" loading="lazy" width="140" height="100">
					</div>
					<div class="c-blog-card__body">
						<span class="c-blog-card__label">📖 %4$s</span>
						<div class="c-blog-card__title">%3$s</div>
						<div class="c-blog-card__desc">%5$s</div>
					</div>
				</div>
			</a>
		</aside>',
		esc_url( $permalink ),
		esc_url( $thumb_url ),
		esc_attr( $title ),
		$label,
		esc_html( $excerpt )
	);
}
add_shortcode( 'oscss_related', 'oscss_related_post_shortcode' );

