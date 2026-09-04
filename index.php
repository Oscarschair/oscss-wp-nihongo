<?php
/**
 * The main template file
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
				<?php
				if ( is_home() && ! is_front_page() ) {
					single_post_title();
				} else {
					esc_html_e( '最新記事一覧', 'oscss-wp-nihongo' );
				}
				?>
			</h1>
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
				<p><?php esc_html_e( '投稿が見つかりませんでした。', 'oscss-wp-nihongo' ); ?></p>
				<?php get_search_form(); ?>
			</div>
		<?php endif; ?>
	</div>
</main>

<?php
get_footer();
