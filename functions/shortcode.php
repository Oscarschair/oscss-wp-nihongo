<?php
/**
 * Shortcodes for oscss-wp-nihongo
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * CTAボタングループ / ボタンショートコード
 * 例: [oscss_btn url="/contact/" text="お問い合わせはこちら" style="primary"]
 */
function oscss_btn_shortcode( $atts ) {
	$atts = shortcode_atts(
		array(
			'url'    => '#',
			'text'   => '詳細を見る',
			'style'  => 'primary', // primary, secondary, outline
			'target' => '_self',
			'align'  => 'left',    // left, center, right
		),
		$atts,
		'oscss_btn'
	);

	$url    = esc_url( $atts['url'] );
	$text   = esc_html( $atts['text'] );
	$style  = sanitize_html_class( $atts['style'] );
	$target = esc_attr( $atts['target'] );
	$align  = sanitize_html_class( $atts['align'] );

	$rel = ( '_blank' === $target ) ? ' rel="noopener noreferrer"' : '';

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
 * アラート / コールアウトボックスショートコード
 * 例: [oscss_alert type="info"]重要なお知らせです[/oscss_alert]
 */
function oscss_alert_shortcode( $atts, $content = null ) {
	$atts = shortcode_atts(
		array(
			'type'  => 'info', // info, success, warning, danger
			'title' => '',
		),
		$atts,
		'oscss_alert'
	);

	$type  = sanitize_html_class( $atts['type'] );
	$title = ! empty( $atts['title'] ) ? '<h4 class="c-alert__title">' . esc_html( $atts['title'] ) . '</h4>' : '';

	return sprintf(
		'<div class="c-alert c-alert--%1$s">%2$s<div class="c-alert__content">%3$s</div></div>',
		$type,
		$title,
		do_shortcode( wp_kses_post( $content ) )
	);
}
add_shortcode( 'oscss_alert', 'oscss_alert_shortcode' );
