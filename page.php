<?php
/**
 * The template for displaying all pages
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
			<article id="post-<?php the_ID(); ?>" <?php post_class( 'c-entry' ); ?>>
				<header class="c-entry__header">
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
			</article>
		<?php endwhile; ?>
	</div>
</main>

<?php
get_footer();
