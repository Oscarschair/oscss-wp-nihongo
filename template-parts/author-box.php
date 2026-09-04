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
<div class="c-author-box">
	<div class="c-author-box__avatar-wrap">
		<img src="<?php echo esc_url( OSCSS_THEME_URI . '/assets/images/my-icon.png' ); ?>" alt="オスカー（車 浩文）" class="c-author-box__avatar" onerror="this.src='<?php echo esc_url( home_url( '/wp-content/uploads/2023/02/my-icon1.jpg' ) ); ?>';" loading="lazy">
	</div>
	<div class="c-author-box__content">
		<span class="c-author-box__label">Written by</span>
		<h3 class="c-author-box__name">車 浩文（オスカー / HIROFUMI KURUMA）</h3>
		<p class="c-author-box__bio">
			香港出身のWebディレクター・アナリスト。日本語の「ことばのあや」や文化の違い、日常で感じたカルチャーショックを外国人視点から分かりやすく発信しています。
		</p>
		<a href="https://oscarchair.jp/" target="_blank" rel="noopener noreferrer" class="c-author-box__link">
			<span>🌐 メインサイト（Webディレクター学習帳 / ポートフォリオ）を見る</span> &rarr;
		</a>
	</div>
</div>
