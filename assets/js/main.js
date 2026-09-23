/**
 * Main JavaScript for oscss-wp-nihongo
 * Accessible navigation, header scroll detection, back-to-top
 */

(function () {
	'use strict';

	document.addEventListener('DOMContentLoaded', function () {
		initNavigation();
		initHeaderScroll();
		initBackToTop();
		initSmoothScroll();
		initSortTabs();
		initViewTracker();
		cleanWidgets();
		initAdSenseSectionGuard();
		initSideRailAdsGuard();
	});

	/**
	 * サイドレール広告（Side Rail Ads）の画面幅判定制御
	 * メインコンテンツ(1120px) + 左右広告(各160px) = 1440px
	 * 1440px未満ではコンテンツへの被り・浸食を防ぐため非表示にし、1440px以上でのみ両側に表示
	 */
	function initSideRailAdsGuard() {
		var handleSideRails = function () {
			var isWideScreen = window.innerWidth >= 1440;
			var fixedAds = document.querySelectorAll(
				'.google-auto-placed[style*="fixed"], ' +
				'ins.adsbygoogle[data-ad-format*="rail"], ' +
				'div[id^="google_ads_iframe"][style*="fixed"]'
			);

			fixedAds.forEach(function (el) {
				if (isWideScreen) {
					el.style.removeProperty('display');
					el.style.removeProperty('visibility');
					el.style.setProperty('z-index', '80', 'important');
				} else {
					el.style.setProperty('display', 'none', 'important');
					el.style.setProperty('visibility', 'hidden', 'important');
				}
			});
		};

		handleSideRails();
		window.addEventListener('resize', handleSideRails);
		setTimeout(handleSideRails, 1500);
		setTimeout(handleSideRails, 3500);

		if (window.MutationObserver) {
			var observer = new MutationObserver(handleSideRails);
			observer.observe(document.body, { childList: true, subtree: true });
		}
	}

	/**
	 * Sectionタグおよび指定コンポーネント内へのAdSense自動広告侵入の動的排除ガード
	 */
	function initAdSenseSectionGuard() {
		var removeAdsFromSections = function () {
			var forbiddenSelectors = [
				'section ins.adsbygoogle',
				'section .google-auto-placed',
				'[data-ad-exclude="true"] ins.adsbygoogle',
				'[data-ad-exclude="true"] .google-auto-placed',
				'.c-hero ins.adsbygoogle',
				'.c-features ins.adsbygoogle',
				'.c-latest-posts ins.adsbygoogle',
				'.c-card-grid ins.adsbygoogle',
				'.c-author-box ins.adsbygoogle'
			];

			var forbiddenAds = document.querySelectorAll(forbiddenSelectors.join(', '));
			forbiddenAds.forEach(function (ad) {
				ad.remove();
			});
		};

		removeAdsFromSections();
		setTimeout(removeAdsFromSections, 1000);
		setTimeout(removeAdsFromSections, 3000);
		setTimeout(removeAdsFromSections, 5000);

		if (window.MutationObserver) {
			var observer = new MutationObserver(function () {
				removeAdsFromSections();
			});
			observer.observe(document.body, {
				childList: true,
				subtree: true
			});
		}
	}


	/**
	 * フッターウィジェットの最適化（最近のコメント除去 ＆ 最近の投稿ツールチップ付与）
	 */
	function cleanWidgets() {
		var footerWidgets = document.querySelectorAll('.l-footer__sidebar-widgets');
		footerWidgets.forEach(function (container) {
			// 1. 最近のコメント関連のブロック・見出しを削除
			var commentBlocks = container.querySelectorAll('.wp-block-latest-comments, .widget_recent_comments');
			commentBlocks.forEach(function (el) {
				// 直前の見出し要素も削除
				var prev = el.previousElementSibling;
				if (prev && (prev.matches('h2, h3, .wp-block-heading, .widget-title') || prev.textContent.indexOf('コメント') !== -1)) {
					prev.remove();
				}
				el.remove();
			});

			// 見出し単体で残っている「最近のコメント」も探索して削除
			var headings = container.querySelectorAll('h2, h3, .wp-block-heading, .widget-title');
			headings.forEach(function (h) {
				if (h.textContent.indexOf('最近のコメント') !== -1 || h.textContent.indexOf('Recent Comments') !== -1) {
					var next = h.nextElementSibling;
					if (next && (next.matches('ul, ol, .wp-block-latest-comments') || next.querySelector('a'))) {
						next.remove();
					}
					h.remove();
				}
			});

			// 2. 最近の投稿のリンクに title 属性を付与（省略時もホバーで全文確認可能に）
			var postLinks = container.querySelectorAll('.wp-block-latest-posts li a, .widget_recent_entries li a, li a');
			postLinks.forEach(function (a) {
				if (!a.getAttribute('title') && a.textContent.trim()) {
					a.setAttribute('title', a.textContent.trim());
				}
			});
		});
	}


	/**
	 * ページ内アンカースムーズスクロール
	 */
	function initSmoothScroll() {
		var links = document.querySelectorAll('a[href^="#"]:not([href="#"])');
		links.forEach(function (link) {
			link.addEventListener('click', function (e) {
				var targetId = link.getAttribute('href');
				if (!targetId || targetId === '#') return;
				
				var targetElement = document.querySelector(targetId);
				if (targetElement) {
					e.preventDefault();
					var header = document.getElementById('site-header');
					var headerHeight = header ? header.offsetHeight : 0;
					var elementPosition = targetElement.getBoundingClientRect().top;
					var offsetPosition = elementPosition + window.pageYOffset - headerHeight - 20;

					window.scrollTo({
						top: offsetPosition,
						behavior: 'smooth'
					});
				}
			});
		});
	}

	/**
	 * モバイルナビゲーション（ハンバーガーメニュー）
	 */
	function initNavigation() {
		var hamburgerBtn = document.getElementById('hamburger-btn');
		var primaryNav = document.getElementById('primary-nav');

		if (!hamburgerBtn || !primaryNav) {
			return;
		}

		hamburgerBtn.addEventListener('click', function () {
			var isExpanded = hamburgerBtn.getAttribute('aria-expanded') === 'true';
			hamburgerBtn.setAttribute('aria-expanded', !isExpanded);
			primaryNav.classList.toggle('is-open', !isExpanded);

			if (!isExpanded) {
				hamburgerBtn.setAttribute('aria-label', 'メニューを閉じる');
			} else {
				hamburgerBtn.setAttribute('aria-label', 'メニューを開く');
			}
		});

		// メニュー外クリックで閉じる
		document.addEventListener('click', function (event) {
			if (
				primaryNav.classList.contains('is-open') &&
				!primaryNav.contains(event.target) &&
				!hamburgerBtn.contains(event.target)
			) {
				hamburgerBtn.setAttribute('aria-expanded', 'false');
				hamburgerBtn.setAttribute('aria-label', 'メニューを開く');
				primaryNav.classList.remove('is-open');
			}
		});

		// サブメニューを持つメニュー項目のタップ制御
		var parentMenuItems = primaryNav.querySelectorAll('.menu-item-has-children > a');
		parentMenuItems.forEach(function (item) {
			item.addEventListener('click', function (e) {
				// 画面幅がモバイル時、またはリンク先が空や#の場合はサブメニューをトグル
				var href = item.getAttribute('href');
				if (window.innerWidth < 768 || !href || href === '#' || href === 'http://nothing') {
					if (!href || href === '#' || href === 'http://nothing') {
						e.preventDefault();
					}
					var parentLi = item.parentElement;
					parentLi.classList.toggle('is-open');
				}
			});
		});
	}

	/**
	 * ヘッダーのスクロール連動シャドウ付与
	 */
	function initHeaderScroll() {
		var header = document.getElementById('site-header');
		if (!header) {
			return;
		}

		var handleScroll = function () {
			if (window.scrollY > 20) {
				header.classList.add('is-scrolled');
			} else {
				header.classList.remove('is-scrolled');
			}
		};

		window.addEventListener('scroll', handleScroll, { passive: true });
		handleScroll();
	}

	/**
	 * バックトゥトップボタン
	 */
	function initBackToTop() {
		var backToTopBtn = document.getElementById('back-to-top');
		if (!backToTopBtn) {
			return;
		}

		var handleScroll = function () {
			if (window.scrollY > 300) {
				backToTopBtn.classList.add('is-visible');
			} else {
				backToTopBtn.classList.remove('is-visible');
			}
		};

		window.addEventListener('scroll', handleScroll, { passive: true });
		handleScroll();

		backToTopBtn.addEventListener('click', function () {
			window.scrollTo({
				top: 0,
				behavior: 'smooth'
			});
		});
	}

	/**
	 * 記事閲覧数の非同期トラッキング（リロード・アクセスごとに表示回数をカウントアップ）
	 */
	function initViewTracker() {
		if (typeof oscssSettings === 'undefined' || !oscssSettings.isSingle || !oscssSettings.postId) {
			return;
		}

		var postId = oscssSettings.postId;
		var trackUrl = oscssSettings.restUrl + 'track-view/' + postId + '?_=' + Date.now();

		fetch(trackUrl, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-WP-Nonce': oscssSettings.nonce || ''
			}
		})
		.then(function (response) {
			return response.json();
		})
		.then(function (data) {
			if (data && data.success && typeof data.views !== 'undefined') {
				// 画面上の views 表示を即座に最新カウントへ更新
				var viewElements = document.querySelectorAll('.c-post-meta__views');
				viewElements.forEach(function (el) {
					var icon = el.querySelector('.c-post-meta__icon');
					var svgEye = '<svg class="c-icon c-icon--eye" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>';
					var iconHtml = icon ? icon.outerHTML + ' ' : '<span class="c-post-meta__icon" aria-hidden="true">' + svgEye + '</span> ';
					el.innerHTML = iconHtml + data.views.toLocaleString() + ' views';
				});
			}
		})
		.catch(function (err) {
			// サイレントにキャッチ（ユーザー体験を損なわない）
			console.debug('View tracking notice:', err);
		});
	}

	/**
	 * 投稿ソート切り替えタブとセッション・Cookie記憶
	 */
	function initSortTabs() {
		var sortTabs = document.querySelectorAll('.c-sort-tab');
		if (!sortTabs.length) {
			return;
		}

		sortTabs.forEach(function (tab) {
			tab.addEventListener('click', function () {
				var sortVal = tab.getAttribute('data-sort');
				if (sortVal) {
					// Cookieに30日間保存
					document.cookie = 'oscss_post_sort=' + encodeURIComponent(sortVal) + '; path=/; max-age=' + (30 * 86400) + '; SameSite=Lax';
					// sessionStorageにも保存
					try {
						sessionStorage.setItem('oscss_post_sort', sortVal);
					} catch (e) {}
				}
			});
		});
	}
})();

