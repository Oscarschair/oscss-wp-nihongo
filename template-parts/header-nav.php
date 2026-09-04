<?php
/**
 * Header navigation template part
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
?>
<div class="c-nav-wrapper">
	<button type="button" class="c-hamburger" id="hamburger-btn" aria-expanded="false" aria-controls="primary-nav" aria-label="<?php esc_attr_e( 'メニューを開く', 'oscss-wp-nihongo' ); ?>">
		<span class="c-hamburger__line"></span>
		<span class="c-hamburger__line"></span>
		<span class="c-hamburger__line"></span>
	</button>

	<nav class="l-header__nav" id="primary-nav" aria-label="<?php esc_attr_e( 'メインメニュー', 'oscss-wp-nihongo' ); ?>">
		<?php
		if ( has_nav_menu( 'primary' ) ) {
			wp_nav_menu(
				array(
					'theme_location' => 'primary',
					'menu_class'     => 'l-header__menu',
					'container'      => false,
					'depth'          => 2,
				)
			);
		} else {
			// デフォルトフォールバックメニュー
			?>
			<ul class="l-header__menu">
				<li class="menu-item"><a href="<?php echo esc_url( home_url( '/' ) ); ?>">ホーム</a></li>
				<?php
				wp_list_pages(
					array(
						'title_li' => '',
						'depth'    => 1,
						'number'   => 5,
					)
				);
				?>
			</ul>
			<?php
		}
		?>
	</nav>
</div>
