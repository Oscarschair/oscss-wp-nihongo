<?php
/**
 * The template for displaying the footer
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
?>
</div><!-- /.l-site-content -->

<footer class="l-footer" id="site-footer">
	<div class="l-container">
		<div class="l-footer__grid">
			<!-- Col 1: Branding & Profile -->
			<div class="l-footer__col l-footer__col--brand">
				<div class="l-footer__brand-header">
					<img src="<?php echo esc_url( OSCSS_THEME_URI . '/assets/images/my-icon.png' ); ?>" alt="オスカー" class="l-footer__avatar" width="48" height="48" style="width: 48px; height: 48px; border-radius: 50%; object-fit: cover;" loading="lazy">
					<div class="l-footer__brand-titles">
						<h2 class="l-footer__brand-title"><?php bloginfo( 'name' ); ?></h2>
						<p class="l-footer__brand-tagline"><?php bloginfo( 'description' ); ?></p>
					</div>
				</div>
				<p class="l-footer__brand-desc">
					香港出身のWebディレクター・オスカーが、日本語の「ことばのあや」や文化の違い、日常で感じたカルチャーショックを外国人視点から分かりやすくお届けする学習ノートです。
				</p>
				<div class="l-footer__brand-links">
					<a href="https://oscarchair.jp/" target="_blank" rel="noopener noreferrer" class="l-footer__ext-link">
						<span>🌐 オスカーの学習帳（メインサイト）</span> &rarr;
					</a>
				</div>
			</div>

			<!-- Col 2: Categories / Series -->
			<div class="l-footer__col l-footer__col--categories">
				<h3 class="l-footer__heading">連載テーマ・カテゴリー</h3>
				<ul class="l-footer__category-list">
					<li>
						<a href="<?php echo esc_url( home_url( '/category/kotoba-no-aya/' ) ); ?>" class="l-footer__category-link">
							<span class="l-footer__badge l-footer__badge--aya">ことばのあや</span>
							<span class="l-footer__category-text">助詞や言葉のニュアンス解説</span>
						</a>
					</li>
					<li>
						<a href="<?php echo esc_url( home_url( '/category/comparing/' ) ); ?>" class="l-footer__category-link">
							<span class="l-footer__badge l-footer__badge--vs">くらべてみました</span>
							<span class="l-footer__category-text">似ている言葉や文化の違いを比較</span>
						</a>
					</li>
					<li>
						<a href="<?php echo esc_url( home_url( '/category/culture-shock/' ) ); ?>" class="l-footer__category-link">
							<span class="l-footer__badge l-footer__badge--culture">カルチャーショック</span>
							<span class="l-footer__category-text">日本と海外の習慣・日常の発見</span>
						</a>
					</li>
				</ul>
			</div>

			<!-- Col 3: Search & Widgets -->
			<div class="l-footer__col l-footer__col--widgets">
				<?php if ( is_active_sidebar( 'footer-1' ) || is_active_sidebar( 'footer-2' ) ) : ?>
					<div class="l-footer__sidebar-widgets">
						<?php
						if ( is_active_sidebar( 'footer-1' ) ) {
							dynamic_sidebar( 'footer-1' );
						}
						if ( is_active_sidebar( 'footer-2' ) ) {
							dynamic_sidebar( 'footer-2' );
						}
						?>
					</div>
				<?php else : ?>
					<h3 class="l-footer__heading">サイト内検索</h3>
					<form role="search" method="get" class="c-search-form" action="<?php echo esc_url( home_url( '/' ) ); ?>">
						<div class="c-search-form__inner">
							<input type="search" class="c-search-form__input" placeholder="キーワードで検索..." value="<?php echo get_search_query(); ?>" name="s" required>
							<button type="submit" class="c-search-form__submit" aria-label="検索">検索</button>
						</div>
					</form>
				<?php endif; ?>
			</div>
		</div>

		<div class="l-footer__bottom">
			<ul class="l-footer__bottom-links">
				<li><a href="<?php echo esc_url( home_url( '/' ) ); ?>">HOME</a></li>
				<li><a href="<?php echo esc_url( home_url( '/category/kotoba-no-aya/' ) ); ?>">ことばのあや</a></li>
				<li><a href="<?php echo esc_url( home_url( '/category/comparing/' ) ); ?>">くらべてみました</a></li>
				<li><a href="<?php echo esc_url( home_url( '/category/culture-shock/' ) ); ?>">カルチャーショック</a></li>
				<li><a href="https://oscarchair.jp/" target="_blank" rel="noopener noreferrer">オスカーの学習帳へ</a></li>
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
