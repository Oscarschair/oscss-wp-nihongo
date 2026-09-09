<?php
/**
 * The template for displaying comments
 *
 * @package oscss-wp-nihongo
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

if ( post_password_required() ) {
	return;
}
?>

<section id="comments" class="c-comments-area" data-ad-exclude="true">
	<?php if ( have_comments() ) : ?>
		<div class="c-comments-header">
			<h2 class="c-comments-title">
				<span class="c-comments-title__icon">💬</span>
				<?php
				$comment_count = get_comments_number();
				printf(
					/* translators: 1: number of comments */
					esc_html( _nx( 'コメント (%1$s件)', 'コメント (%1$s件)', $comment_count, 'comments title', 'oscss-wp-nihongo' ) ),
					number_format_i18n( $comment_count )
				);
				?>
			</h2>
		</div>

		<ol class="c-comment-list">
			<?php
			wp_list_comments(
				array(
					'style'       => 'ol',
					'short_ping'  => true,
					'avatar_size' => 48,
					'callback'    => 'oscss_custom_comment',
				)
			);
			?>
		</ol>

		<?php
		the_comments_navigation(
			array(
				'prev_text' => '<span class="c-comments-nav__label">&larr; ' . esc_html__( '古いコメント', 'oscss-wp-nihongo' ) . '</span>',
				'next_text' => '<span class="c-comments-nav__label">' . esc_html__( '新しいコメント', 'oscss-wp-nihongo' ) . ' &rarr;</span>',
			)
		);
		?>

		<?php if ( ! comments_open() ) : ?>
			<p class="c-comments-closed"><?php esc_html_e( '現在コメントの受け付けは終了しています。', 'oscss-wp-nihongo' ); ?></p>
		<?php endif; ?>

	<?php endif; ?>

	<?php
	// コメントフォームのカスタマイズ
	$commenter = wp_get_current_commenter();
	$req       = get_option( 'require_name_email' );
	$aria_req  = ( $req ? " aria-required='true' required" : '' );

	$fields = array(
		'author'  => '<div class="c-comment-form-group c-comment-form-author">' .
			'<label for="author" class="c-comment-form-label">' . esc_html__( 'お名前 / ニックネーム', 'oscss-wp-nihongo' ) . ( $req ? ' <span class="c-required">*</span>' : '' ) . '</label>' .
			'<input id="author" name="author" type="text" class="c-form-input" value="' . esc_attr( $commenter['comment_author'] ) . '" size="30" maxlength="245" placeholder="例: 日本語学習者"' . $aria_req . ' />' .
			'</div>',
		'email'   => '<div class="c-comment-form-group c-comment-form-email">' .
			'<label for="email" class="c-comment-form-label">' . esc_html__( 'メールアドレス', 'oscss-wp-nihongo' ) . ( $req ? ' <span class="c-required">*</span>' : '' ) . ' <span class="c-comment-form-note">(非公開)</span></label>' .
			'<input id="email" name="email" type="email" class="c-form-input" value="' . esc_attr( $commenter['comment_author_email'] ) . '" size="30" maxlength="100" aria-describedby="email-notes" placeholder="name@example.com"' . $aria_req . ' />' .
			'</div>',
		'url'     => '<div class="c-comment-form-group c-comment-form-url">' .
			'<label for="url" class="c-comment-form-label">' . esc_html__( 'ウェブサイト (任意)', 'oscss-wp-nihongo' ) . '</label>' .
			'<input id="url" name="url" type="url" class="c-form-input" value="' . esc_attr( $commenter['comment_author_url'] ) . '" size="30" maxlength="200" placeholder="https://example.com" />' .
			'</div>',
		'cookies' => '<div class="c-comment-form-cookies">' .
			'<input id="wp-comment-cookies-consent" name="wp-comment-cookies-consent" type="checkbox" class="c-form-checkbox" value="yes"' . ( empty( $commenter['comment_author_email'] ) ? '' : ' checked="checked"' ) . ' />' .
			'<label for="wp-comment-cookies-consent" class="c-comment-form-cookies-label">' . esc_html__( '次回のコメントで使用するためブラウザーに名前、メールアドレス、サイトを保存する', 'oscss-wp-nihongo' ) . '</label>' .
			'</div>',
	);

	comment_form(
		array(
			'fields'               => $fields,
			'comment_field'        => '<div class="c-comment-form-group c-comment-form-comment">' .
				'<label for="comment" class="c-comment-form-label">' . esc_html__( 'コメント内容', 'oscss-wp-nihongo' ) . ' <span class="c-required">*</span></label>' .
				'<textarea id="comment" name="comment" class="c-form-textarea" cols="45" rows="5" maxlength="65525" placeholder="記事へのご意見や感想、質問などをお気軽にどうぞ！" required="required"></textarea>' .
				'</div>',
			'title_reply'          => '<span class="c-reply-title__icon">✍️</span> ' . esc_html__( 'コメントを残す', 'oscss-wp-nihongo' ),
			'title_reply_to'       => '<span class="c-reply-title__icon">↩️</span> ' . esc_html__( '%s に返信する', 'oscss-wp-nihongo' ),
			'title_reply_before'   => '<h3 id="reply-title" class="c-comment-reply-title">',
			'title_reply_after'    => '</h3>',
			'cancel_reply_before'  => ' <span class="c-cancel-reply">',
			'cancel_reply_after'   => '</span>',
			'cancel_reply_link'    => esc_html__( '返信をキャンセル', 'oscss-wp-nihongo' ),
			'comment_notes_before' => '<p class="c-comment-notes">' . esc_html__( 'メールアドレスが公開されることはありません。※ が付いている欄は必須項目です。', 'oscss-wp-nihongo' ) . '</p>',
			'class_container'      => 'c-comment-respond',
			'class_form'           => 'c-comment-form',
			'class_submit'         => 'c-btn c-btn--primary c-comment-submit',
			'submit_button'        => '<button type="submit" name="%1$s" id="%2$s" class="%3$s"><span>' . esc_html__( 'コメントを送信する', 'oscss-wp-nihongo' ) . ' &rarr;</span></button>',
			'submit_field'         => '<div class="c-comment-form-submit">%1$s %2$s</div>',
		)
	);
	?>
</section>
