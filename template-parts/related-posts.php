<?php
/**
 * Related posts template part for single post
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

$current_id = get_the_ID();
$categories = wp_get_post_categories( $current_id );

if ( empty( $categories ) ) {
	return;
}

// 同一カテゴリーの関連記事を3件取得（現在の記事を除外）
$args = array(
	'category__in'        => $categories,
	'post__not_in'        => array( $current_id ),
	'posts_per_page'      => 3,
	'ignore_sticky_posts' => 1,
	'orderby'             => 'date',
	'order'               => 'DESC',
);

$related_query = new WP_Query( $args );

// 3件未満の場合は最新記事で補完
if ( $related_query->post_count < 3 ) {
	$needed   = 3 - $related_query->post_count;
	$exclude  = array_merge( array( $current_id ), wp_list_pluck( $related_query->posts, 'ID' ) );
	$fallback = get_posts(
		array(
			'posts_per_page' => $needed,
			'post__not_in'   => $exclude,
			'orderby'        => 'date',
			'order'          => 'DESC',
		)
	);
	if ( ! empty( $fallback ) ) {
		$related_query->posts = array_merge( $related_query->posts, $fallback );
		$related_query->post_count = count( $related_query->posts );
	}
}

if ( ! empty( $related_query->posts ) ) :
	?>
	<section class="c-related-posts" aria-labelledby="related-posts-title">
		<div class="c-related-posts__header">
			<h2 id="related-posts-title" class="c-related-posts__title">
				<span class="c-related-posts__icon" aria-hidden="true">📖</span>
				<?php esc_html_e( 'あわせて読みたい関連記事', 'oscss-wp-nihongo' ); ?>
			</h2>
			<p class="c-related-posts__subtitle">
				<?php esc_html_e( 'こちらの記事もチェックして、リアルな日本語と文化の理解を深めましょう！', 'oscss-wp-nihongo' ); ?>
			</p>
		</div>

		<div class="c-card-grid c-related-posts__grid">
			<?php
			foreach ( $related_query->posts as $post ) :
				setup_postdata( $post );
				get_template_part( 'template-parts/post-card' );
			endforeach;
			wp_reset_postdata();
			?>
		</div>
	</section>
	<?php
endif;
