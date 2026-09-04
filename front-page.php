<?php
/**
 * The template for displaying the front page
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

get_header();
?>

<main class="l-main">
	<!-- Hero Section -->
	<section class="c-hero">
		<div class="l-container c-hero__inner">
			<div class="c-hero__content">
				<span class="c-badge c-badge--accent">WordPress Theme</span>
				<h1 class="c-hero__title">
					美しく、読みやすく。<br>
					日本語に最適化された<br>
					モダンWordPressテーマ
				</h1>
				<p class="c-hero__lead">
					「oscss-wp-nihongo」は、8pt Gridシステムと徹底した日本語組版最適化により、洗練されたデザインと抜群の可読性を両立するカスタムテーマです。
				</p>
				<div class="c-hero__actions">
					<a href="#features" class="c-btn c-btn--primary">特徴を見る</a>
					<a href="#latest-posts" class="c-btn c-btn--outline">最新記事へ</a>
				</div>
			</div>
			<div class="c-hero__visual">
				<div class="c-hero__card-preview">
					<div class="c-hero__preview-badge">✨ High Performance</div>
					<div class="c-hero__preview-body">
						<div class="c-hero__preview-line c-hero__preview-line--title"></div>
						<div class="c-hero__preview-line"></div>
						<div class="c-hero__preview-line c-hero__preview-line--short"></div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- Features Section -->
	<section class="c-features" id="features">
		<div class="l-container">
			<div class="c-section-header">
				<h2 class="c-section-header__title">テーマの特長</h2>
				<p class="c-section-header__desc">モダンWeb標準と日本語アクセシビリティを追求した設計</p>
			</div>

			<div class="c-features__grid">
				<div class="c-feature-box">
					<div class="c-feature-box__icon">✍️</div>
					<h3 class="c-feature-box__title">日本語タイポグラフィ</h3>
					<p class="c-feature-box__text">適切な行間（1.75倍）と文字間隔、禁則処理、美しく読みやすいフォントスタックを標準搭載。</p>
				</div>

				<div class="c-feature-box">
					<div class="c-feature-box__icon">📐</div>
					<h3 class="c-feature-box__title">8pt Grid システム</h3>
					<p class="c-feature-box__text">余白・要素サイズを8の倍数で統一し、デバイスサイズを問わず美しい調和とリズムを維持。</p>
				</div>

				<div class="c-feature-box">
					<div class="c-feature-box__icon">🧩</div>
					<h3 class="c-feature-box__title">モジュラーPHP設計</h3>
					<p class="c-feature-box__text">functions/ 配下を責務ごとに分離し、肥大化を防ぎ長期的な保守性と拡張性を担保。</p>
				</div>
			</div>
		</div>
	</section>

	<!-- Latest Posts Section -->
	<section class="c-latest-posts" id="latest-posts">
		<div class="l-container">
			<div class="c-section-header">
				<h2 class="c-section-header__title">最新記事</h2>
				<p class="c-section-header__desc">ブログやお知らせの最新トピックス</p>
			</div>

			<?php
			$recent_posts = new WP_Query(
				array(
					'posts_per_page'      => 6,
					'post_status'         => 'publish',
					'ignore_sticky_posts' => 1,
				)
			);

			if ( $recent_posts->have_posts() ) :
				?>
				<div class="c-card-grid">
					<?php
					while ( $recent_posts->have_posts() ) :
						$recent_posts->the_post();
						get_template_part( 'template-parts/post-card' );
					endwhile;
					wp_reset_postdata();
					?>
				</div>
			<?php else : ?>
				<p class="u-text-center">投稿はまだありません。</p>
			<?php endif; ?>
		</div>
	</section>
</main>

<?php
get_footer();
