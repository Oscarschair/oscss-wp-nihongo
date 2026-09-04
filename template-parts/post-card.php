<?php
/**
 * Post card template part
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
?>
<article id="post-<?php the_ID(); ?>" <?php post_class( 'c-card' ); ?>>
	<div class="c-card__media">
		<a href="<?php the_permalink(); ?>" class="c-card__media-link" tabindex="-1" aria-hidden="true">
			<?php if ( has_post_thumbnail() ) : ?>
				<?php the_post_thumbnail( 'oscss-card', array( 'class' => 'c-card__img', 'loading' => 'lazy' ) ); ?>
			<?php else : ?>
				<div class="c-card__placeholder">
					<span><?php bloginfo( 'name' ); ?></span>
				</div>
			<?php endif; ?>
		</a>
		<?php oscss_entry_category(); ?>
	</div>

	<div class="c-card__body">
		<div class="c-card__meta">
			<?php oscss_posted_on(); ?>
		</div>

		<h3 class="c-card__title">
			<a href="<?php the_permalink(); ?>" class="c-card__title-link">
				<?php the_title(); ?>
			</a>
		</h3>

		<div class="c-card__excerpt">
			<?php the_excerpt(); ?>
		</div>

		<div class="c-card__footer">
			<a href="<?php the_permalink(); ?>" class="c-card__more">
				<?php esc_html_e( '続きを読む', 'oscss-wp-nihongo' ); ?>
				<span class="c-card__more-icon" aria-hidden="true">&rarr;</span>
			</a>
		</div>
	</div>
</article>
