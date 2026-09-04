<?php
/**
 * The template for displaying the front page (オスカーの日本語学習帳)
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

get_header();

// 各カテゴリへのリンクを取得
$cat_kurabete = get_category_by_slug( 'くらべてみました' );
$cat_kurabete_url = $cat_kurabete ? get_category_link( $cat_kurabete->term_id ) : home_url( '/category/%e3%81%8f%e3%82%89%e3%81%b9%e3%81%a6%e3%81%bf%e3%81%be%e3%81%97%e3%81%9f/' );

$cat_aya = get_category_by_slug( 'aya-of-words' );
if ( ! $cat_aya ) {
	$cat_aya = get_category_by_slug( 'ことばのあや' );
}
$cat_aya_url = $cat_aya ? get_category_link( $cat_aya->term_id ) : home_url( '/category/aya-of-words/' );

$cat_culture = get_category_by_slug( 'カルチャーショック' );
$cat_culture_url = $cat_culture ? get_category_link( $cat_culture->term_id ) : home_url( '/category/%e3%82%ab%e3%83%ab%e3%83%81%e3%83%a3%e3%83%bc%e3%82%b7%e3%83%a7%e3%83%83%e3%82%af/' );
?>

<main class="l-main">
	<!-- Hero Section -->
	<section class="c-hero">
		<div class="l-container c-hero__inner">
			<div class="c-hero__content">
				<span class="c-badge c-badge--accent">🇭🇰 外国人視点の日本語学習ブログ</span>
				<h1 class="c-hero__title">
					ことばのあやと、<br>
					日常のカルチャーショックを<br>
					外国人視点で読み解く。
				</h1>
				<p class="c-hero__lead">
					「オスカーの日本語学習帳」は、香港出身のWebディレクターが、日本語特有のニュアンスや文化の違い、日常の気づきを分かりやすく綴るメディアです。
				</p>
				<div class="c-hero__actions">
					<a href="#categories" class="c-btn c-btn--primary">テーマ別に見る</a>
					<a href="#latest-posts" class="c-btn c-btn--outline">最新記事を読む</a>
				</div>
			</div>
			<div class="c-hero__visual">
				<div class="c-hero__character">
					<picture>
						<source srcset="<?php echo esc_url( OSCSS_THEME_URI . '/assets/images/hero-oscar-v2.webp' ); ?>" type="image/webp">
						<img src="<?php echo esc_url( OSCSS_THEME_URI . '/assets/images/hero-oscar-v2.png' ); ?>" alt="<?php esc_attr_e( '日本語を楽しく学ぶオスカー', 'oscss-wp-nihongo' ); ?>" class="c-hero__character-img" width="560" height="420" loading="eager" fetchpriority="high">
					</picture>
				</div>
			</div>
		</div>
	</section>

	<!-- Features / Categories Section -->
	<section class="c-features" id="categories">
		<div class="l-container">
			<div class="c-section-header">
				<h2 class="c-section-header__title">主な連載テーマ</h2>
				<p class="c-section-header__desc">外国人視点だからこそ見えてくる、日本語の面白さと奥深さ</p>
			</div>

			<div class="c-features__grid">
				<a href="<?php echo esc_url( $cat_kurabete_url ); ?>" class="c-feature-box" aria-label="「くらべてみました」の記事一覧へ">
					<div class="c-feature-box__icon">🔍</div>
					<h3 class="c-feature-box__title">くらべてみました</h3>
					<p class="c-feature-box__text">「ごめんなさい」と「すみません」など、似ているようで異なる表現の違いを徹底比較。</p>
					<span class="c-feature-box__cta">
						記事一覧を見る <span class="c-feature-box__arrow">&rarr;</span>
					</span>
				</a>

				<a href="<?php echo esc_url( $cat_aya_url ); ?>" class="c-feature-box" aria-label="「ことばのあや」の記事一覧へ">
					<div class="c-feature-box__icon">🗣️</div>
					<h3 class="c-feature-box__title">ことばのあや</h3>
					<p class="c-feature-box__text">終助詞「ね」「よ」の使い方など、相手とスムーズに会話するためのニュアンスを解説。</p>
					<span class="c-feature-box__cta">
						記事一覧を見る <span class="c-feature-box__arrow">&rarr;</span>
					</span>
				</a>

				<a href="<?php echo esc_url( $cat_culture_url ); ?>" class="c-feature-box" aria-label="「カルチャーショック」の記事一覧へ">
					<div class="c-feature-box__icon">🌏</div>
					<h3 class="c-feature-box__title">カルチャーショック</h3>
					<p class="c-feature-box__text">日本の習慣や食文化、香港と日本のコミュニケーション感覚の違いをリアルに綴ります。</p>
					<span class="c-feature-box__cta">
						記事一覧を見る <span class="c-feature-box__arrow">&rarr;</span>
					</span>
				</a>
			</div>
		</div>
	</section>

	<!-- Latest Posts Section -->
	<section class="c-latest-posts" id="latest-posts">
		<div class="l-container">
			<?php $current_sort = oscss_get_current_sort(); ?>
			<div class="c-section-header c-section-header--with-controls">
				<div class="c-section-header__text">
					<h2 class="c-section-header__title">
						<?php echo ( 'views' === $current_sort ) ? esc_html__( '人気の記事一覧', 'oscss-wp-nihongo' ) : esc_html__( '記事一覧', 'oscss-wp-nihongo' ); ?>
					</h2>
					<p class="c-section-header__desc">
						<?php echo ( 'views' === $current_sort ) ? esc_html__( '読者によく読まれている学習ノート（閲覧数順）', 'oscss-wp-nihongo' ) : esc_html__( '最近公開された学習ノート（新着順）', 'oscss-wp-nihongo' ); ?>
					</p>
				</div>
				<div class="c-section-header__controls">
					<?php oscss_render_sort_tabs( $current_sort, '#latest-posts' ); ?>
				</div>
			</div>

			<?php
			$query_args = array(
				'posts_per_page'      => 12,
				'post_status'         => 'publish',
				'ignore_sticky_posts' => 1,
			);

			if ( 'views' === $current_sort ) {
				$query_args['meta_key'] = '_oscss_post_views';
				$query_args['orderby']  = array(
					'meta_value_num' => 'DESC',
					'date'           => 'DESC',
				);
			} else {
				$query_args['orderby'] = 'date';
				$query_args['order']   = 'DESC';
			}

			$recent_posts = new WP_Query( $query_args );

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
