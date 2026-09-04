<?php
/**
 * Pagination template part
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

the_posts_pagination(
	array(
		'mid_size'           => 2,
		'prev_text'          => '<span aria-hidden="true">&larr;</span> ' . __( '前へ', 'oscss-wp-nihongo' ),
		'next_text'          => __( '次へ', 'oscss-wp-nihongo' ) . ' <span aria-hidden="true">&rarr;</span>',
		'screen_reader_text' => __( '投稿ナビゲーション', 'oscss-wp-nihongo' ),
		'class'              => 'c-pagination',
	)
);
