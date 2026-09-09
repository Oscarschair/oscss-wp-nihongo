<?php
/**
 * Custom Search Form Template
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
?>
<form role="search" method="get" class="c-search-form" action="<?php echo esc_url( home_url( '/' ) ); ?>">
	<div class="c-search-form__inner">
		<label class="screen-reader-text" for="s"><?php esc_html_e( 'キーワード検索', 'oscss-wp-nihongo' ); ?></label>
		<div class="c-search-form__input-wrap">
			<svg class="c-search-form__icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
				<circle cx="11" cy="11" r="8"></circle>
				<line x1="21" y1="21" x2="16.65" y2="16.65"></line>
			</svg>
			<input type="search" id="s" class="c-search-form__input" placeholder="<?php esc_attr_e( '気になる日本語やキーワードを入力...', 'oscss-wp-nihongo' ); ?>" value="<?php echo get_search_query(); ?>" name="s" />
		</div>
		<button type="submit" class="c-search-form__submit">
			<?php esc_html_e( '検索する', 'oscss-wp-nihongo' ); ?>
		</button>
	</div>
</form>
