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
$series_cats = oscss_get_series_categories();
?>

<main class="l-main c-page-404">
	<div class="l-container">
		<?php oscss_breadcrumb(); ?>

		<!-- 404 メインカード -->
		<div class="c-error-hero">
			<div class="c-error-hero__inner">
				<div class="c-error-hero__visual">
					<div class="c-error-hero__character-wrap">
						<img src="<?php echo esc_url( OSCSS_THEME_URI . '/assets/images/hero-oscar-v2.png' ); ?>" 
						     alt="<?php esc_attr_e( '困惑するオスカー', 'oscss-wp-nihongo' ); ?>" 
						     class="c-error-hero__character" 
						     width="280" 
						     height="280" 
						     loading="eager" />
						<span class="c-error-hero__bubble" aria-hidden="true">あれれ...？🤔</span>
					</div>
				</div>

				<div class="c-error-hero__content">
					<div class="c-error-hero__badge">404 NOT FOUND</div>
					<h1 class="c-error-hero__title">お探しのページが見つかりませんでした</h1>
					<p class="c-error-hero__lead">
						アクセスいただいたページは、URLが変更されたか、削除・移動された可能性があります。<br>
						キーワード検索や、以下のカテゴリー・おすすめ記事から探してみてください！
					</p>

					<!-- 検索ボックス -->
					<div class="c-error-hero__search">
						<?php get_search_form(); ?>
					</div>

					<!-- カテゴリクイックリンク -->
					<div class="c-error-hero__categories">
						<span class="c-error-hero__cat-label"><?php esc_html_e( 'カテゴリーから探す:', 'oscss-wp-nihongo' ); ?></span>
						<div class="c-error-hero__cat-list">
							<?php foreach ( $series_cats as $key => $cat_info ) : ?>
								<a href="<?php echo esc_url( oscss_get_series_category_url( $key ) ); ?>" class="c-badge c-badge--category-link <?php echo esc_attr( $cat_info['badge_class'] ); ?>">
									<?php echo esc_html( $cat_info['icon'] . ' ' . $cat_info['name'] ); ?>
								</a>
							<?php endforeach; ?>
						</div>
					</div>

					<!-- アクションボタン -->
					<div class="c-error-hero__actions">
						<a href="<?php echo esc_url( home_url( '/' ) ); ?>" class="c-btn c-btn--primary">
							<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="margin-right: 6px;">
								<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
								<polyline points="9 22 9 12 15 12 15 22"></polyline>
							</svg>
							<?php esc_html_e( 'トップページへ戻る', 'oscss-wp-nihongo' ); ?>
						</a>
					</div>
				</div>
			</div>
		</div>

		<!-- おすすめ・新着記事セクション -->
		<section class="c-error-recommendations">
			<div class="c-section-header">
				<h2 class="c-section-header__title">💡 こちらの日本語学習ノートもおすすめ</h2>
				<p class="c-section-header__desc">最新の解説記事をピックアップしてご紹介します</p>
			</div>

			<div class="c-card-grid">
				<?php
				$recent_query = new WP_Query(
					array(
						'post_type'           => 'post',
						'posts_per_page'      => 3,
						'post_status'         => 'publish',
						'ignore_sticky_posts' => 1,
					)
				);

				if ( $recent_query->have_posts() ) :
					while ( $recent_query->have_posts() ) :
						$recent_query->the_post();
						get_template_part( 'template-parts/post-card' );
					endwhile;
					wp_reset_postdata();
				endif;
				?>
			</div>
		</section>
	</div>
</main>

<?php
get_footer();
