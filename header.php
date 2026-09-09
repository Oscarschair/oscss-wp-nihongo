<?php
/**
 * The header for our theme
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
?>
<!DOCTYPE html>
<html <?php language_attributes(); ?> prefix="og: https://ogp.me/ns# fb: https://ogp.me/ns/fb# website: https://ogp.me/ns/website#">
<head>
	<meta charset="<?php bloginfo( 'charset' ); ?>">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<link rel="profile" href="https://gmpg.org/xfn/11">
	<?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<a class="c-skip-link screen-reader-text" href="#primary-content">
	<?php esc_html_e( 'メインコンテンツへスキップ', 'oscss-wp-nihongo' ); ?>
</a>

<header class="l-header" id="site-header">
	<div class="l-container l-header__inner">
		<div class="l-header__branding">
			<?php
			if ( has_custom_logo() ) {
				the_custom_logo();
			} else {
				?>
				<a href="<?php echo esc_url( home_url( '/' ) ); ?>" class="l-header__logo-text" rel="home">
					<?php bloginfo( 'name' ); ?>
				</a>
				<?php
			}
			$description = get_bloginfo( 'description', 'display' );
			if ( $description || is_customize_preview() ) :
				?>
				<p class="l-header__description"><?php echo esc_html( $description ); ?></p>
			<?php endif; ?>
		</div>

		<?php get_template_part( 'template-parts/header-nav' ); ?>
	</div>
</header>

<div class="l-site-content" id="primary-content">
