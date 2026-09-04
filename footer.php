<?php
/**
 * The template for displaying the footer
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
?>
</div><!-- /.l-site-content -->

<footer class="l-footer" id="site-footer">
	<div class="l-container">
		<?php if ( is_active_sidebar( 'footer-1' ) || is_active_sidebar( 'footer-2' ) ) : ?>
			<div class="l-footer__widgets">
				<?php if ( is_active_sidebar( 'footer-1' ) ) : ?>
					<div class="l-footer__widget-col">
						<?php dynamic_sidebar( 'footer-1' ); ?>
					</div>
				<?php endif; ?>

				<?php if ( is_active_sidebar( 'footer-2' ) ) : ?>
					<div class="l-footer__widget-col">
						<?php dynamic_sidebar( 'footer-2' ); ?>
					</div>
				<?php endif; ?>
			</div>
		<?php endif; ?>

		<?php if ( has_nav_menu( 'footer' ) ) : ?>
			<nav class="l-footer__nav" aria-label="<?php esc_attr_e( 'フッターメニュー', 'oscss-wp-nihongo' ); ?>">
				<?php
				wp_nav_menu(
					array(
						'theme_location' => 'footer',
						'menu_class'     => 'l-footer__menu',
						'container'      => false,
						'depth'          => 1,
						'fallback_cb'    => false,
					)
				);
				?>
			</nav>
		<?php endif; ?>

		<div class="l-footer__bottom">
			<p class="l-footer__copyright">
				&copy; <?php echo esc_html( gmdate( 'Y' ) ); ?> <?php bloginfo( 'name' ); ?>. All Rights Reserved.
			</p>
		</div>
	</div>
</footer>

<button type="button" class="c-back-to-top" id="back-to-top" aria-label="<?php esc_attr_e( 'ページ上部へ戻る', 'oscss-wp-nihongo' ); ?>">
	<svg class="c-back-to-top__icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
		<polyline points="18 15 12 9 6 15"></polyline>
	</svg>
</button>

<?php wp_footer(); ?>
</body>
</html>
