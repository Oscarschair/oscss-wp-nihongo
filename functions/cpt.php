<?php
/**
 * Custom Post Types for oscss-wp-nihongo
 * 4コマ漫画 (manga) カスタム投稿タイプおよび相互内部リンク機能
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * 4コマ漫画カスタム投稿タイプの登録
 */
function oscss_register_manga_cpt() {
	$labels = array(
		'name'                  => _x( '4コマ漫画', 'Post type general name', 'oscss-wp-nihongo' ),
		'singular_name'         => _x( '4コマ漫画', 'Post type singular name', 'oscss-wp-nihongo' ),
		'menu_name'             => _x( '4コマ漫画', 'Admin Menu text', 'oscss-wp-nihongo' ),
		'name_admin_bar'        => _x( '4コマ漫画', 'Add New on Toolbar', 'oscss-wp-nihongo' ),
		'add_new'               => __( '新規追加', 'oscss-wp-nihongo' ),
		'add_new_item'          => __( '新規4コマ漫画を追加', 'oscss-wp-nihongo' ),
		'new_item'              => __( '新しい4コマ漫画', 'oscss-wp-nihongo' ),
		'edit_item'             => __( '4コマ漫画を編集', 'oscss-wp-nihongo' ),
		'view_item'             => __( '4コマ漫画を表示', 'oscss-wp-nihongo' ),
		'all_items'             => __( 'すべての4コマ漫画', 'oscss-wp-nihongo' ),
		'search_items'          => __( '4コマ漫画を検索', 'oscss-wp-nihongo' ),
		'parent_item_colon'     => __( '親の4コマ漫画:', 'oscss-wp-nihongo' ),
		'not_found'             => __( '4コマ漫画が見つかりませんでした。', 'oscss-wp-nihongo' ),
		'not_found_in_trash'    => __( 'ゴミ箱内に4コマ漫画は見つかりませんでした。', 'oscss-wp-nihongo' ),
		'featured_image'        => _x( 'サムネイル画像', 'Overrides the "Featured Image" phrase', 'oscss-wp-nihongo' ),
		'set_featured_image'    => _x( 'サムネイル画像を設定', 'Overrides the "Set featured image" phrase', 'oscss-wp-nihongo' ),
		'remove_featured_image' => _x( 'サムネイル画像を削除', 'Overrides the "Remove featured image" phrase', 'oscss-wp-nihongo' ),
		'use_featured_image'    => _x( 'サムネイル画像として使用', 'Overrides the "Use as featured image" phrase', 'oscss-wp-nihongo' ),
	);

	$args = array(
		'labels'             => $labels,
		'public'             => true,
		'publicly_queryable' => true,
		'show_ui'            => true,
		'show_in_menu'       => true,
		'query_var'          => true,
		'rewrite'            => array( 'slug' => 'manga', 'with_front' => false ),
		'capability_type'    => 'post',
		'has_archive'        => true,
		'hierarchical'       => false,
		'menu_position'      => 5,
		'menu_icon'          => 'dashicons-format-gallery',
		'show_in_rest'       => true, // Gutenberg & REST API対応
		'supports'           => array( 'title', 'editor', 'author', 'thumbnail', 'excerpt', 'custom-fields', 'revisions' ),
		'taxonomies'         => array( 'category', 'post_tag' ), // 既存の連載カテゴリー・タグを共有
	);

	register_post_type( 'manga', $args );
}
add_action( 'init', 'oscss_register_manga_cpt' );

/**
 * 4コマ漫画詳細ページ：元記事への相互リンクを本文末尾に自動挿入
 */
function oscss_append_manga_connected_post( $content ) {
	if ( ! is_singular( 'manga' ) || ! in_the_loop() || ! is_main_query() ) {
		return $content;
	}

	$connected_id = get_post_meta( get_the_ID(), 'connected_post_id', true );
	if ( empty( $connected_id ) ) {
		return $content;
	}

	$post = get_post( $connected_id );
	if ( ! $post || $post->post_status !== 'publish' ) {
		return $content;
	}

	$title = get_the_title( $connected_id );
	$url   = get_permalink( $connected_id );
	$thumb = get_the_post_thumbnail_url( $connected_id, 'medium' );

	$html  = '<div class="c-manga-connected-post">';
	$html .= '<div class="c-manga-connected-post__badge">📖 この4コマの元記事（解説）を読む</div>';
	$html .= '<a href="' . esc_url( $url ) . '" class="c-manga-connected-post__card">';
	if ( $thumb ) {
		$html .= '<div class="c-manga-connected-post__thumb"><img src="' . esc_url( $thumb ) . '" alt="' . esc_attr( $title ) . '" loading="lazy"></div>';
	}
	$html .= '<div class="c-manga-connected-post__info">';
	$html .= '<h4 class="c-manga-connected-post__title">' . esc_html( wp_strip_all_tags( $title ) ) . '</h4>';
	$html .= '<p class="c-manga-connected-post__desc">言葉の背景や詳しいニュアンスをブログ記事で徹底解説しています！</p>';
	$html .= '<span class="c-manga-connected-post__link-btn">詳しく読む →</span>';
	$html .= '</div></a></div>';

	return $content . $html;
}
add_filter( 'the_content', 'oscss_append_manga_connected_post', 20 );

/**
 * 通常投稿詳細ページ：関連する4コマ漫画への逆リンクを本文末尾に自動挿入
 */
function oscss_append_post_connected_manga( $content ) {
	if ( ! is_singular( 'post' ) || ! in_the_loop() || ! is_main_query() ) {
		return $content;
	}

	$current_id = get_the_ID();
	$manga_posts = get_posts( array(
		'post_type'   => 'manga',
		'meta_key'    => 'connected_post_id',
		'meta_value'  => $current_id,
		'post_status' => 'publish',
		'numberposts' => 1,
	) );

	if ( empty( $manga_posts ) ) {
		return $content;
	}

	$manga = $manga_posts[0];
	$manga_title = get_the_title( $manga->ID );
	$manga_url   = get_permalink( $manga->ID );
	$manga_thumb = get_the_post_thumbnail_url( $manga->ID, 'medium' );

	$html  = '<div class="c-post-connected-manga">';
	$html .= '<div class="c-post-connected-manga__badge">🎨 この記事の4コマ漫画版を見る！</div>';
	$html .= '<a href="' . esc_url( $manga_url ) . '" class="c-post-connected-manga__card">';
	if ( $manga_thumb ) {
		$html .= '<div class="c-post-connected-manga__thumb"><img src="' . esc_url( $manga_thumb ) . '" alt="' . esc_attr( $manga_title ) . '" loading="lazy"></div>';
	}
	$html .= '<div class="c-post-connected-manga__info">';
	$html .= '<h4 class="c-post-connected-manga__title">' . esc_html( wp_strip_all_tags( $manga_title ) ) . '</h4>';
	$html .= '<p class="c-post-connected-manga__desc">オスカーと仲間たちの日常をコミカルな4コマ漫画でお楽しみください！</p>';
	$html .= '<span class="c-post-connected-manga__link-btn">4コマ漫画を見る →</span>';
	$html .= '</div></a></div>';

	return $content . $html;
}
add_filter( 'the_content', 'oscss_append_post_connected_manga', 25 );
