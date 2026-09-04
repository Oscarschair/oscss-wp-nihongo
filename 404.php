<?php
/**
 * The template for displaying 404 pages (not found)
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

		<div class="c-error-404">
			<div class="c-error-404__badge">404 Error</div>
			<h1 class="c-error-404__title">お探しのページが見つかりませんでした</h1>
			<p class="c-error-404__text">
				申し訳ありません。アクセスいただいたページは、移動または削除されたか、URLが正しくない可能性があります。<br>
				以下の検索フォーム、またはトップページから再度お探しください。
			</p>

			<div class="c-error-404__search">
				<?php get_search_form(); ?>
			</div>

			<div class="c-error-404__actions">
				<a href="<?php echo esc_url( home_url( '/' ) ); ?>" class="c-btn c-btn--primary">
					トップページへ戻る
				</a>
			</div>
		</div>
	</div>
</main>

<?php
get_footer();
