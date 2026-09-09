<?php
/**
 * The template for displaying the footer
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

$series_cats = oscss_get_series_categories();
?>
</div><!-- /.l-site-content -->

<footer class="l-footer" id="site-footer">
	<div class="l-container">
		<div class="l-footer__grid">
			<!-- Col 1: Branding & Profile -->
			<div class="l-footer__col l-footer__col--brand">
				<div class="l-footer__brand-header">
					<img src="<?php echo esc_url( OSCSS_THEME_URI . '/assets/images/my-icon.png' ); ?>" alt="<?php esc_attr_e( 'オスカー（車 浩文）', 'oscss-wp-nihongo' ); ?>" class="l-footer__avatar" width="48" height="48" style="width: 48px; height: 48px; border-radius: 50%; object-fit: cover;" loading="lazy">
					<div class="l-footer__brand-titles">
						<div class="l-footer__brand-title"><?php bloginfo( 'name' ); ?></div>
						<p class="l-footer__brand-tagline"><?php bloginfo( 'description' ); ?></p>
					</div>
				</div>
				<p class="l-footer__brand-desc">
					香港出身のWebディレクター・オスカーが、日本語の「ことばのあや」や文化の違い、日常で感じたカルチャーショックを外国人視点から分かりやすくお届けする学習ノートです。
				</p>
				<div class="l-footer__brand-links">
					<a href="https://oscarchair.jp/" target="_blank" rel="noopener noreferrer" class="l-footer__ext-link">
						<span>🌐 クルマのAIノート（メインサイト）</span> &rarr;
					</a>
				</div>
			</div>

			<!-- Col 2: Categories / Series -->
			<div class="l-footer__col l-footer__col--categories">
				<h3 class="l-footer__heading"><?php esc_html_e( '連載テーマ・カテゴリー', 'oscss-wp-nihongo' ); ?></h3>
				<ul class="l-footer__category-list">
					<?php foreach ( $series_cats as $key => $cat_info ) : ?>
						<li>
							<a href="<?php echo esc_url( oscss_get_series_category_url( $key ) ); ?>" class="l-footer__category-link">
								<span class="l-footer__badge <?php echo esc_attr( $cat_info['badge_class'] ); ?>"><?php echo esc_html( $cat_info['name'] ); ?></span>
								<span class="l-footer__category-text"><?php echo esc_html( $cat_info['lead'] ); ?></span>
							</a>
						</li>
					<?php endforeach; ?>
				</ul>
			</div>

			<!-- Col 3: Search & Widgets -->
			<div class="l-footer__col l-footer__col--widgets">
				<?php if ( is_active_sidebar( 'footer-1' ) || is_active_sidebar( 'footer-2' ) ) : ?>
					<div class="l-footer__sidebar-widgets">
						<?php
						ob_start();
						if ( is_active_sidebar( 'footer-1' ) ) {
							dynamic_sidebar( 'footer-1' );
						}
						if ( is_active_sidebar( 'footer-2' ) ) {
							dynamic_sidebar( 'footer-2' );
						}
						$sidebar_html = ob_get_clean();

						// 「最近のコメント」を含むウィジェットブロックを完全に除去
						$sidebar_html = preg_replace( '/<div[^>]*class="[^"]*c-widget[^"]*"[^>]*>[\s\S]*?(?:wp-block-latest-comments|最近のコメント|widget_recent_comments)[\s\S]*?<\/ol>\s*<\/div>\s*<\/div>\s*<\/div>/u', '', $sidebar_html );
						$sidebar_html = preg_replace( '/<div[^>]*id="block-4"[^>]*>[\s\S]*?<\/div>\s*<\/div>\s*<\/div>/u', '', $sidebar_html );
						$sidebar_html = preg_replace( '/<h[23][^>]*>[^<]*最近のコメント[^<]*<\/h[23]>/u', '', $sidebar_html );
						$sidebar_html = preg_replace( '/<ol[^>]*class="[^"]*wp-block-latest-comments[^"]*"[\s\S]*?<\/ol>/u', '', $sidebar_html );

						echo $sidebar_html; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
						?>
					</div>
				<?php else : ?>
					<h3 class="l-footer__heading"><?php esc_html_e( 'サイト内検索', 'oscss-wp-nihongo' ); ?></h3>
					<form role="search" method="get" class="c-search-form" action="<?php echo esc_url( home_url( '/' ) ); ?>">
						<div class="c-search-form__inner">
							<label for="footer-search-input" class="screen-reader-text"><?php esc_html_e( 'キーワード検索', 'oscss-wp-nihongo' ); ?></label>
							<input type="search" id="footer-search-input" class="c-search-form__input" placeholder="<?php esc_attr_e( 'キーワードで検索...', 'oscss-wp-nihongo' ); ?>" value="<?php echo get_search_query(); ?>" name="s" required>
							<button type="submit" class="c-search-form__submit" aria-label="<?php esc_attr_e( '検索', 'oscss-wp-nihongo' ); ?>"><?php esc_html_e( '検索', 'oscss-wp-nihongo' ); ?></button>
						</div>
					</form>
				<?php endif; ?>
			</div>
		</div>

		<div class="l-footer__bottom">
			<ul class="l-footer__bottom-links">
				<li><a href="<?php echo esc_url( home_url( '/' ) ); ?>">HOME</a></li>
				<?php foreach ( $series_cats as $key => $cat_info ) : ?>
					<li><a href="<?php echo esc_url( oscss_get_series_category_url( $key ) ); ?>"><?php echo esc_html( $cat_info['name'] ); ?></a></li>
				<?php endforeach; ?>
				<li><a href="https://oscarchair.jp/" target="_blank" rel="noopener noreferrer">クルマのAIノートへ</a></li>
			</ul>
			<p class="l-footer__copyright">
				&copy; <?php echo esc_html( gmdate( 'Y' ) ); ?> <?php bloginfo( 'name' ); ?>. All Rights Reserved.
			</p>
		</div>
	</div>
</footer>

<button type="button" class="c-back-to-top" id="back-to-top" aria-label="<?php esc_attr_e( 'ページ上部へ戻る', 'oscss-wp-nihongo' ); ?>">
	<svg class="c-back-to-top__icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
		<polyline points="18 15 12 9 6 15"></polyline>
	</svg>
</button>

<?php wp_footer(); ?>
</body>
</html>
