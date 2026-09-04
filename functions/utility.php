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

	echo '<span class="c-post-meta__item c-post-meta__date"><span class="c-post-meta__icon" aria-hidden="true">📅</span> ' . $time_string . '</span>'; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
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
