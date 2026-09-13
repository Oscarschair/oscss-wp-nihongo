<?php
/**
 * The template for displaying all single posts
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

get_header();
?>

<main class="l-main">
	<div class="l-container l-container--narrow">
		<?php oscss_breadcrumb(); ?>

		<?php
		while ( have_posts() ) :
			the_post();
			?>
			<article id="post-<?php the_ID(); ?>" <?php post_class( 'c-entry' ); ?> data-post-id="<?php the_ID(); ?>">
				<header class="c-entry__header">
					<div class="c-entry__meta">
						<?php oscss_entry_category(); ?>
						<?php oscss_posted_on(); ?>
						<?php oscss_posted_reading_time(); ?>
						<?php oscss_posted_views(); ?>
					</div>

					<h1 class="c-entry__title"><?php the_title(); ?></h1>

					<?php if ( has_post_thumbnail() ) : ?>
						<div class="c-entry__thumbnail">
							<?php
							the_post_thumbnail(
								'full',
								array(
									'class'         => 'c-entry__thumbnail-img',
									'loading'       => 'eager',
									'fetchpriority' => 'high',
									'alt'           => the_title_attribute( array( 'echo' => false ) ),
								)
							);
							?>
						</div>
					<?php endif; ?>
				</header>

				<div class="c-entry__content c-prose">
					<?php
					the_content();

					wp_link_pages(
						array(
							'before' => '<div class="c-page-links">' . esc_html__( 'ページ:', 'oscss-wp-nihongo' ),
							'after'  => '</div>',
						)
					);
					?>
				</div>

				<!-- 著者プロフィール（オスカー様） -->
				<?php get_template_part( 'template-parts/author-box' ); ?>

				<footer class="c-entry__footer">
					<?php
					$tags = get_the_tags();
					if ( ! empty( $tags ) ) :
						?>
						<div class="c-entry__tags">
							<span class="c-entry__tags-label"><?php echo oscss_get_icon( 'tag', 14 ); ?> タグ:</span>
							<?php foreach ( $tags as $tag ) : ?>
								<a href="<?php echo esc_url( get_tag_link( $tag->term_id ) ); ?>" class="c-badge c-badge--tag">
									#<?php echo esc_html( $tag->name ); ?>
								</a>
							<?php endforeach; ?>
						</div>
					<?php endif; ?>

					<!-- あわせて読みたい関連記事（内部リンク強化） -->
					<?php get_template_part( 'template-parts/related-posts' ); ?>

					<nav class="c-post-nav" aria-label="<?php esc_attr_e( '投稿ナビゲーション', 'oscss-wp-nihongo' ); ?>">
						<div class="c-post-nav__prev">
							<?php
							previous_post_link(
								'%link',
								'<span class="c-post-nav__label">&larr; 前の記事</span><span class="c-post-nav__title">%title</span>'
							);
							?>
						</div>
						<div class="c-post-nav__next">
							<?php
							next_post_link(
								'%link',
								'<span class="c-post-nav__label">次の記事 &rarr;</span><span class="c-post-nav__title">%title</span>'
							);
							?>
						</div>
					</nav>
				</footer>
			</article>

			<?php
			if ( comments_open() || get_comments_number() ) :
				comments_template();
			endif;
			?>

		<?php endwhile; ?>
	</div>
</main>

<?php
get_footer();
