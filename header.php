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
	<!-- Google Tag Manager -->
	<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
	new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
	j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
	'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
	})(window,document,'script','dataLayer','GTM-K6NZHVDJ');</script>
	<!-- End Google Tag Manager -->
	<meta charset="<?php bloginfo( 'charset' ); ?>">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<script>
		try {
			if (localStorage.getItem('oscss_ruby_state') === 'off') {
				document.documentElement.classList.add('is-ruby-hidden');
			}
		} catch (e) {}
	</script>
	<?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>
	<!-- Google Tag Manager (noscript) -->
	<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-K6NZHVDJ"
	height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
	<!-- End Google Tag Manager (noscript) -->
<?php wp_body_open(); ?>

<a class="c-skip-link screen-reader-text" href="#primary-content">
	<?php esc_html_e( 'メインコンテンツへスキップ', 'oscss-wp-nihongo' ); ?>
</a>

<header class="l-header" id="site-header">
	<div class="l-container l-header__inner">
		<div class="l-header__branding">
			<a href="<?php echo esc_url( home_url( '/' ) ); ?>" class="l-header__logo-text" rel="home">
				<span class="l-header__logo-main"><?php bloginfo( 'name' ); ?></span>
				<span class="l-header__logo-sub">Oscar’s Japanese Notebook</span>
			</a>
			<?php
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
