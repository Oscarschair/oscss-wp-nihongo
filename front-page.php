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

$series_cats = oscss_get_series_categories();
?>

<main class="l-main">
	<!-- Hero Section -->
	<section class="c-hero" data-ad-exclude="true">
		<div class="l-container c-hero__inner">
			<div class="c-hero__content">
				<span class="c-badge c-badge--accent">🇭🇰 外国人視点の日本語学習ブログ</span>
				<h1 class="c-hero__title">
					ことばのあやと、<br>
					日常のカルチャーショックを<br>
					外国人視点で読み解く。
				</h1>
				<p class="c-hero__lead">
					「オスカーの日本語学習帳」は、香港出身のオスカーが、日本語特有のニュアンスや文化の違い、日常の気づきを分かりやすく綴るメディアです。
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
	<section class="c-features" id="categories" data-ad-exclude="true">
		<div class="l-container">
			<div class="c-section-header">
				<h2 class="c-section-header__title">主な連載テーマ</h2>
				<p class="c-section-header__desc">教科書には載っていないリアルな発見。日本での日常がもっと面白くなる4つのアプローチ</p>
			</div>

			<div class="c-features__grid">
				<?php foreach ( $series_cats as $key => $cat_info ) : ?>
					<a href="<?php echo esc_url( oscss_get_series_category_url( $key ) ); ?>" class="c-feature-box c-feature-box--<?php echo esc_attr( isset( $cat_info['color_key'] ) ? $cat_info['color_key'] : 'default' ); ?>" aria-label="<?php echo esc_attr( sprintf( __( '「%s」の記事一覧へ', 'oscss-wp-nihongo' ), $cat_info['name'] ) ); ?>">
						<div class="c-feature-box__header">
							<div class="c-feature-box__icon c-feature-box__icon--<?php echo esc_attr( isset( $cat_info['color_key'] ) ? $cat_info['color_key'] : 'default' ); ?>" aria-hidden="true"><?php echo esc_html( $cat_info['icon'] ); ?></div>
							<?php if ( ! empty( $cat_info['tag'] ) ) : ?>
								<span class="c-feature-box__tag c-feature-box__tag--<?php echo esc_attr( $cat_info['color_key'] ); ?>">
									<?php echo esc_html( $cat_info['tag'] ); ?>
								</span>
							<?php endif; ?>
						</div>
						<div class="c-feature-box__body">
							<h3 class="c-feature-box__title"><?php echo esc_html( $cat_info['name'] ); ?></h3>
							<?php if ( ! empty( $cat_info['hook'] ) ) : ?>
								<p class="c-feature-box__hook"><?php echo esc_html( $cat_info['hook'] ); ?></p>
							<?php endif; ?>
							<p class="c-feature-box__text"><?php echo esc_html( $cat_info['desc'] ); ?></p>
						</div>
						<?php if ( ! empty( $cat_info['examples'] ) ) : ?>
							<div class="c-feature-box__examples">
								<span class="c-feature-box__examples-label">気になるテーマ例</span>
								<div class="c-feature-box__pills">
									<?php foreach ( $cat_info['examples'] as $ex ) : ?>
										<span class="c-feature-box__pill"><?php echo esc_html( $ex ); ?></span>
									<?php endforeach; ?>
								</div>
							</div>
						<?php endif; ?>
						<div class="c-feature-box__footer">
							<span class="c-feature-box__cta">
								連載を読む <span class="c-feature-box__arrow" aria-hidden="true">&rarr;</span>
							</span>
						</div>
					</a>
				<?php endforeach; ?>
			</div>
		</div>
	</section>

	<!-- Latest Posts Section -->
	<section class="c-latest-posts" id="latest-posts" data-ad-exclude="true">
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
