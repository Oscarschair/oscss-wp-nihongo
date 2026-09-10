<?php
/**
 * Author box template part (オスカー様プロフィール)
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
?>
<div class="c-author-box" itemscope itemtype="https://schema.org/Person">
	<div class="c-author-box__avatar-wrap">
		<img src="<?php echo esc_url( OSCSS_THEME_URI . '/assets/images/my-icon.png' ); ?>" 
		     alt="<?php esc_attr_e( 'オスカー', 'oscss-wp-nihongo' ); ?>" 
		     class="c-author-box__avatar" 
		     width="80" 
		     height="80" 
		     itemprop="image"
		     onerror="this.src='<?php echo esc_url( home_url( '/wp-content/uploads/2023/02/my-icon1.jpg' ) ); ?>';" 
		     loading="lazy">
	</div>
	<div class="c-author-box__content">
		<span class="c-author-box__label">Written by</span>
		<h3 class="c-author-box__name" itemprop="name">オスカー</h3>
		<p class="c-author-box__bio" itemprop="description">
			香港出身の日本語学習者・日本在住。日本語の「ことばのあや」や文化の違い、日常で感じたカルチャーショックを外国人視点から分かりやすく発信しています。
		</p>
		<a href="https://oscarchair.jp/" target="_blank" rel="author me external noopener noreferrer" class="c-author-box__link" itemprop="url">
			<span>🌐 メインサイト（クルマのAIノート / ポートフォリオ）を見る</span> &rarr;
		</a>
	</div>
</div>
