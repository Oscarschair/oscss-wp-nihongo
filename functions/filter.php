<?php
/**
 * Filter hooks for oscss-wp-nihongo
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * 抜粋の文字数を日本語用に最適化（80文字）
 */
function oscss_excerpt_length( $length ) {
	return 80;
}
add_filter( 'excerpt_length', 'oscss_excerpt_length', 999 );

/**
 * 抜粋末尾の記号
 */
function oscss_excerpt_more( $more ) {
	return '...';
}
add_filter( 'excerpt_more', 'oscss_excerpt_more' );

/**
 * Bodyクラスの追加
 */
function oscss_body_classes( $classes ) {
	// サイドバーの有無判定用
	if ( ! is_active_sidebar( 'sidebar-1' ) ) {
		$classes[] = 'no-sidebar';
	}

	// ページ種類ごとのクラス
	if ( is_front_page() ) {
		$classes[] = 'is-front-page';
	} elseif ( is_single() ) {
		$classes[] = 'is-single-post';
	} elseif ( is_page() ) {
		$classes[] = 'is-page';
	}

	return $classes;
}
add_filter( 'body_class', 'oscss_body_classes' );

/**
 * アーカイブタイトルから「カテゴリー:」や「タグ:」のプレフィックスを除去
 */
function oscss_archive_title( $title ) {
	if ( is_category() ) {
		$title = single_cat_title( '', false );
	} elseif ( is_tag() ) {
		$title = single_tag_title( '', false );
	} elseif ( is_author() ) {
		$title = '<span class="vcard">' . get_the_author() . '</span>';
	} elseif ( is_post_type_archive() ) {
		$title = post_type_archive_title( '', false );
	} elseif ( is_tax() ) {
		$title = single_term_title( '', false );
	}
	return $title;
}
add_filter( 'get_the_archive_title', 'oscss_archive_title' );
