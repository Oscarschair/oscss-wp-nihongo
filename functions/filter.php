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

/**
 * 記事本文内の古いアイコン画像を最新の高画質 my-icon.png に置換
 */
function oscss_replace_content_avatar_icons( $content ) {
	$new_icon = OSCSS_THEME_URI . '/assets/images/my-icon.png';
	return str_replace(
		array(
			'https://nihongo.oscarchair.jp/wp-content/uploads/2023/02/my-icon1.jpg',
			'/wp-content/uploads/2023/02/my-icon1.jpg',
		),
		$new_icon,
		$content
	);
}
add_filter( 'the_content', 'oscss_replace_content_avatar_icons', 20 );

/**
 * タイトルタグの区切り文字を「 | 」に統一
 */
function oscss_document_title_separator( $sep ) {
	return '|';
}
add_filter( 'document_title_separator', 'oscss_document_title_separator' );

/**
 * タイトルタグのパーツ最適化（トップページ・アーカイブ等）
 */
function oscss_document_title_parts( $title ) {
	if ( is_front_page() || is_home() ) {
		$title['tagline'] = get_bloginfo( 'description', 'display' );
	}
	return $title;
}
add_filter( 'document_title_parts', 'oscss_document_title_parts' );

/**
 * フッターやサイドバーウィジェットから「最近のコメント」ブロックおよびその見出しを除外
 */
function oscss_remove_recent_comments_block( $block_content, $block ) {
	if ( ! is_admin() ) {
		// 最近のコメントブロックを除外
		if ( isset( $block['blockName'] ) && 'core/latest-comments' === $block['blockName'] ) {
			return '';
		}
		// 「最近のコメント」見出しブロックを除外
		if ( isset( $block['blockName'] ) && 'core/heading' === $block['blockName'] ) {
			if ( strpos( $block_content, '最近のコメント' ) !== false || stripos( $block_content, 'Recent Comments' ) !== false ) {
				return '';
			}
		}
	}
	return $block_content;
}
add_filter( 'render_block', 'oscss_remove_recent_comments_block', 10, 2 );

/**
 * クラシックウィジェットから「最近のコメント」を除外
 */
function oscss_disable_recent_comments_widget( $sidebars_widgets ) {
	if ( is_admin() ) {
		return $sidebars_widgets;
	}
	foreach ( $sidebars_widgets as $sidebar_id => $widgets ) {
		if ( is_array( $widgets ) ) {
			foreach ( $widgets as $key => $widget_id ) {
				if ( strpos( $widget_id, 'recent-comments' ) !== false ) {
					unset( $sidebars_widgets[ $sidebar_id ][ $key ] );
				}
			}
		}
	}
	return $sidebars_widgets;
}
add_filter( 'sidebars_widgets', 'oscss_disable_recent_comments_widget' );

/**
 * ウィジェットブロックコンテンツから「最近のコメント」を含むブロック全体を除外
 */
function oscss_filter_widget_block_content( $content, $id, $sidebar_id ) {
	if ( ! is_admin() ) {
		if ( strpos( $content, 'wp-block-latest-comments' ) !== false || strpos( $content, '最近のコメント' ) !== false || strpos( $content, 'widget_recent_comments' ) !== false ) {
			return '';
		}
	}
	return $content;
}
add_filter( 'widget_block_content', 'oscss_filter_widget_block_content', 10, 3 );

/**
 * 本文中の <section> タグに data-ad-exclude="true" を自動付与し、AdSense自動広告の侵入を防止
 */
function oscss_exclude_ads_from_sections( $content ) {
	if ( empty( $content ) ) {
		return $content;
	}
	return preg_replace_callback(
		'/<section([^>]*)>/i',
		function( $matches ) {
			if ( strpos( $matches[1], 'data-ad-exclude' ) === false ) {
				return '<section' . $matches[1] . ' data-ad-exclude="true">';
			}
			return $matches[0];
		},
		$content
	);
}
add_filter( 'the_content', 'oscss_exclude_ads_from_sections', 25 );
