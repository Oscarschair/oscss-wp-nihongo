<?php
/**
 * Template Name: 記事一覧ページ
 * Description: すべての学習ノート（投稿）をソート・カテゴリー絞り込み・JLPT絞り込み・ページネーション付きで一覧表示するテンプレート
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

get_header();

// 現在のパラメータ取得
$current_sort     = oscss_get_current_sort();
$current_cat_slug = isset( $_GET['cat'] ) ? sanitize_text_field( wp_unslash( $_GET['cat'] ) ) : '';
$current_jlpt     = isset( $_GET['jlpt'] ) ? strtolower( sanitize_text_field( wp_unslash( $_GET['jlpt'] ) ) ) : '';

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

// JLPTフィルター条件の構築 (n2, n3, n4)
$jlpt_query_clause = array();
if ( ! empty( $current_jlpt ) && in_array( $current_jlpt, array( 'n2', 'n3', 'n4' ), true ) ) {
	$jlpt_query_clause = array(
		'key'     => '_oscss_jlpt_level',
		'value'   => strtoupper( $current_jlpt ),
		'compare' => 'LIKE',
	);
}

// ソート順およびmeta_query結合
if ( 'views' === $current_sort ) {
	if ( ! empty( $jlpt_query_clause ) ) {
		$query_args['meta_query'] = array(
			'relation'     => 'AND',
			'views_clause' => array(
				'key'     => '_oscss_post_views',
				'type'    => 'NUMERIC',
				'compare' => 'EXISTS',
			),
			'jlpt_clause'  => $jlpt_query_clause,
		);
		$query_args['orderby'] = array(
			'views_clause' => 'DESC',
			'date'         => 'DESC',
		);
	} else {
		$query_args['meta_key'] = '_oscss_post_views';
		$query_args['orderby']  = array(
			'meta_value_num' => 'DESC',
			'date'           => 'DESC',
		);
	}
} else {
	if ( ! empty( $jlpt_query_clause ) ) {
		$query_args['meta_query'] = array( $jlpt_query_clause );
	}
	$query_args['orderby'] = 'date';
	$query_args['order']   = 'DESC';
}

$articles_query = new WP_Query( $query_args );

// カテゴリー一覧情報（タブ用）
$series_cats = oscss_get_series_categories();

// JLPTレベル定義
$jlpt_levels = array(
	'n2' => array(
		'label' => 'JLPT N2',
		'desc'  => '上級・ビジネス表現',
		'icon'  => '🎯',
	),
	'n3' => array(
		'label' => 'JLPT N3',
		'desc'  => '中級・日常会話・ニュアンス',
		'icon'  => '🎯',
	),
	'n4' => array(
		'label' => 'JLPT N4',
		'desc'  => '初中級・街角実践日本語',
		'icon'  => '🎯',
	),
);
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
					$desc_parts = array();
					if ( ! empty( $current_cat_slug ) && isset( $series_cats[ $current_cat_slug ] ) ) {
						$desc_parts[] = sprintf( '「%s」', $series_cats[ $current_cat_slug ]['name'] );
					}
					if ( ! empty( $current_jlpt ) && isset( $jlpt_levels[ $current_jlpt ] ) ) {
						$desc_parts[] = sprintf( '【%s】', $jlpt_levels[ $current_jlpt ]['label'] );
					}

					if ( ! empty( $desc_parts ) ) {
						printf(
							/* translators: 1: 条件文字列, 2: 記事総数 */
							esc_html__( '%1$s の学習ノート（全 %2$d 件）', 'oscss-wp-nihongo' ),
							esc_html( implode( ' × ', $desc_parts ) ),
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

		<!-- フィルターグループ（カテゴリー ＆ JLPT） -->
		<div class="c-article-filters">
			<!-- カテゴリー絞り込みフィルタータブ -->
			<div class="c-filter-row">
				<span class="c-filter-row__label">🏷️ <?php esc_html_e( 'カテゴリー', 'oscss-wp-nihongo' ); ?>:</span>
				<ul class="c-category-filter-list">
					<li class="c-category-filter-item">
						<?php $all_cat_url = remove_query_arg( array( 'cat', 'paged' ) ); ?>
						<a href="<?php echo esc_url( $all_cat_url ); ?>"
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
			</div>

			<!-- JLPT目安レベル絞り込みフィルタータブ -->
			<div class="c-filter-row c-filter-row--jlpt">
				<span class="c-filter-row__label">🎯 <?php esc_html_e( 'JLPT目安', 'oscss-wp-nihongo' ); ?>:</span>
				<ul class="c-category-filter-list c-jlpt-filter-list">
					<li class="c-category-filter-item">
						<?php $all_jlpt_url = remove_query_arg( array( 'jlpt', 'paged' ) ); ?>
						<a href="<?php echo esc_url( $all_jlpt_url ); ?>"
						   class="c-category-filter-btn c-jlpt-filter-btn <?php echo empty( $current_jlpt ) ? 'is-active' : ''; ?>">
							<?php esc_html_e( 'すべてのレベル', 'oscss-wp-nihongo' ); ?>
						</a>
					</li>
					<?php foreach ( $jlpt_levels as $lvl_key => $lvl_data ) : ?>
						<?php
						$filter_jlpt_url = add_query_arg( array( 'jlpt' => $lvl_key ), remove_query_arg( 'paged' ) );
						$is_lvl_active   = ( $current_jlpt === $lvl_key );
						?>
						<li class="c-category-filter-item">
							<a href="<?php echo esc_url( $filter_jlpt_url ); ?>"
							   class="c-category-filter-btn c-jlpt-filter-btn c-jlpt-filter-btn--<?php echo esc_attr( $lvl_key ); ?> <?php echo $is_lvl_active ? 'is-active' : ''; ?>"
							   title="<?php echo esc_attr( $lvl_data['desc'] ); ?>">
								<span class="c-category-filter-icon" aria-hidden="true"><?php echo esc_html( $lvl_data['icon'] ); ?></span>
								<?php echo esc_html( $lvl_data['label'] ); ?>
							</a>
						</li>
					<?php endforeach; ?>
				</ul>
			</div>
		</div>

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
