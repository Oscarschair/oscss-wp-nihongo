<?php
/**
 * Template Name: 記事一覧ページ
 * Description: すべての学習ノート（投稿）をソート・カテゴリー絞り込み・ページネーション付きで一覧表示するテンプレート
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

get_header();

// 現在のパラメータ取得
$current_sort = oscss_get_current_sort();
$current_cat_slug = isset( $_GET['cat'] ) ? sanitize_text_field( wp_unslash( $_GET['cat'] ) ) : '';

// ページネーション番号の取得
$paged = ( get_query_var( 'paged' ) ) ? get_query_var( 'paged' ) : ( ( get_query_var( 'page' ) ) ? get_query_var( 'page' ) : 1 );

// クエリ引数構築
$query_args = array(
	'post_type'           => 'post',
	'post_status'         => 'publish',
	'posts_per_page'      => 12,
	'paged'               => $paged,
	'ignore_sticky_posts' => 1,
);

// カテゴリー絞り込み
if ( ! empty( $current_cat_slug ) ) {
	$query_args['category_name'] = $current_cat_slug;
}

// ソート順
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

$articles_query = new WP_Query( $query_args );

// カテゴリー一覧情報（タブ用）
$series_cats = oscss_get_series_categories();
?>

<main class="l-main">
	<div class="l-container">
		<?php oscss_breadcrumb(); ?>

		<header class="c-page-header c-page-header--with-controls">
			<div class="c-page-header__text">
				<h1 class="c-page-header__title">
					📚 <?php esc_html_e( '学習ノート一覧', 'oscss-wp-nihongo' ); ?>
				</h1>
				<p class="c-page-header__desc">
					<?php
					if ( ! empty( $current_cat_slug ) && isset( $series_cats[ $current_cat_slug ] ) ) {
						printf(
							/* translators: 1: カテゴリー名, 2: 記事総数 */
							esc_html__( '「%1$s」の学習ノート（全 %2$d 件）', 'oscss-wp-nihongo' ),
							esc_html( $series_cats[ $current_cat_slug ]['name'] ),
							(int) $articles_query->found_posts
						);
					} else {
						printf(
							/* translators: %d: 記事総数 */
							esc_html__( '日常の気づきと文化の比較を綴った全 %d 件の学習ノート', 'oscss-wp-nihongo' ),
							(int) $articles_query->found_posts
						);
					}
					?>
				</p>
			</div>

			<div class="c-page-header__controls">
				<?php oscss_render_sort_tabs( $current_sort ); ?>
			</div>
		</header>

		<!-- カテゴリー絞り込みフィルタータブ -->
		<nav class="c-category-filter-nav" aria-label="<?php esc_attr_e( 'カテゴリーで絞り込む', 'oscss-wp-nihongo' ); ?>">
			<ul class="c-category-filter-list">
				<li class="c-category-filter-item">
					<a href="<?php echo esc_url( remove_query_arg( array( 'cat', 'paged' ) ) ); ?>"
					   class="c-category-filter-btn <?php echo empty( $current_cat_slug ) ? 'is-active' : ''; ?>">
						<?php esc_html_e( 'すべて', 'oscss-wp-nihongo' ); ?>
					</a>
				</li>
				<?php foreach ( $series_cats as $slug => $cat_data ) : ?>
					<?php
					$filter_url = add_query_arg( array( 'cat' => $slug ), remove_query_arg( 'paged' ) );
					$is_active  = ( $current_cat_slug === $slug );
					?>
					<li class="c-category-filter-item">
						<a href="<?php echo esc_url( $filter_url ); ?>"
						   class="c-category-filter-btn c-category-filter-btn--<?php echo esc_attr( isset( $cat_data['color_key'] ) ? $cat_data['color_key'] : 'default' ); ?> <?php echo $is_active ? 'is-active' : ''; ?>">
							<span class="c-category-filter-icon" aria-hidden="true"><?php echo esc_html( $cat_data['icon'] ); ?></span>
							<?php echo esc_html( $cat_data['name'] ); ?>
						</a>
					</li>
				<?php endforeach; ?>
			</ul>
		</nav>

		<?php if ( $articles_query->have_posts() ) : ?>
			<div class="c-card-grid">
				<?php
				while ( $articles_query->have_posts() ) :
					$articles_query->the_post();
					get_template_part( 'template-parts/post-card' );
				endwhile;
				wp_reset_postdata();
				?>
			</div>

			<!-- ページネーション -->
			<?php
			$total_pages = $articles_query->max_num_pages;
			if ( $total_pages > 1 ) :
				$current_page = max( 1, $paged );
				$paginate_links = paginate_links(
					array(
						'base'      => esc_url( add_query_arg( 'paged', '%#%' ) ),
						'format'    => '',
						'current'   => $current_page,
						'total'     => $total_pages,
						'type'      => 'array',
						'prev_text' => '&larr; ' . __( '前へ', 'oscss-wp-nihongo' ),
						'next_text' => __( '次へ', 'oscss-wp-nihongo' ) . ' &rarr;',
					)
				);

				if ( ! empty( $paginate_links ) ) :
					?>
					<nav class="c-pagination" aria-label="<?php esc_attr_e( 'ページ送り', 'oscss-wp-nihongo' ); ?>">
						<ul class="c-pagination__list">
							<?php foreach ( $paginate_links as $link ) : ?>
								<li class="c-pagination__item">
									<?php echo wp_kses_post( $link ); ?>
								</li>
							<?php endforeach; ?>
						</ul>
					</nav>
					<?php
				endif;
			endif;
			?>

		<?php else : ?>
			<div class="c-no-posts">
				<p><?php esc_html_e( '該当する学習ノートは見つかりませんでした。', 'oscss-wp-nihongo' ); ?></p>
				<p><a href="<?php echo esc_url( get_permalink() ); ?>" class="c-btn c-btn--outline"><?php esc_html_e( 'すべての記事を表示する', 'oscss-wp-nihongo' ); ?></a></p>
			</div>
		<?php endif; ?>
	</div>
</main>

<?php
get_footer();
