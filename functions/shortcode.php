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
