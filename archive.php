<?php
/**
 * The template for displaying archive pages
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

get_header();
?>

<main class="l-main">
	<div class="l-container">
		<?php oscss_breadcrumb(); ?>

		<header class="c-page-header">
			<h1 class="c-page-header__title">
				<?php the_archive_title(); ?>
			</h1>
			<?php
			$description = get_the_archive_description();
			if ( $description ) :
				?>
				<div class="c-page-header__desc">
					<?php echo wp_kses_post( $description ); ?>
				</div>
			<?php endif; ?>
		</header>

		<?php if ( have_posts() ) : ?>
			<div class="c-card-grid">
				<?php
				while ( have_posts() ) :
					the_post();
					get_template_part( 'template-parts/post-card' );
				endwhile;
				?>
			</div>

			<?php get_template_part( 'template-parts/pagination' ); ?>

		<?php else : ?>
			<div class="c-no-posts">
				<p><?php esc_html_e( 'このカテゴリー・タグに該当する記事は見つかりませんでした。', 'oscss-wp-nihongo' ); ?></p>
			</div>
		<?php endif; ?>
	</div>
</main>

<?php
get_footer();
