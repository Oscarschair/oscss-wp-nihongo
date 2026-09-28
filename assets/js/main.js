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
		initRubyToggle();
		initSmoothScroll();
		initSortTabs();
		initViewTracker();
		cleanWidgets();
		initAdSenseSectionGuard();
		initSideRailAdsGuard();
		initFullscreenAdBlocker();
	});

	/**
	 * 全画面広告（Vignette / インタースティシャル広告）の完全遮断ガード
	 * スクロール時や画面遷移時に画面全体（60%以上）を覆う固定ポップアップ広告を即座に非表示化
	 */
	function initFullscreenAdBlocker() {
		var killFullscreenAds = function () {
			var overlays = document.querySelectorAll(
				'div[style*="position: fixed"], ' +
				'div[style*="position:fixed"], ' +
				'ins.adsbygoogle-noablate, ' +
				'ins[data-anchor-status], ' +
				'.google-auto-placed:has(> ins[data-anchor-status]), ' +
				'iframe[id^="aswift_"][style*="fixed"]'
			);

			overlays.forEach(function (el) {
				// PC表示時のサイドレール広告枠（左右端の縦長枠）は除外して許可
				if (window.innerWidth >= 1024 && (el.matches('[data-ad-format*="rail"]') || el.matches('.google-auto-placed:has(ins[data-ad-format*="rail"])'))) {
					return;
				}

				// アンカー広告（画面上下・アイキャッチ等に被る固定バー）を即座に排除
				if (el.matches('ins[data-anchor-status]') || el.matches('.google-auto-placed:has(> ins[data-anchor-status])') || el.querySelector('ins[data-anchor-status]')) {
					el.style.setProperty('display', 'none', 'important');
					el.style.setProperty('visibility', 'hidden', 'important');
					el.style.setProperty('pointer-events', 'none', 'important');
					return;
				}

				var rect = el.getBoundingClientRect();
				// 画面幅および高さの65%以上を覆う巨大な固定要素（全画面広告）を検出
				if (rect.width >= window.innerWidth * 0.65 && rect.height >= window.innerHeight * 0.65) {
					// Google AdSense関連の要素か確認
					var isGoogle = el.id.indexOf('aswift') !== -1 ||
					               el.id.indexOf('google') !== -1 ||
					               el.className.indexOf('google') !== -1 ||
					               el.className.indexOf('adsbygoogle') !== -1 ||
					               el.querySelector('iframe[id*="aswift"], iframe[id*="google"]');
					if (isGoogle) {
						el.style.setProperty('display', 'none', 'important');
						el.style.setProperty('visibility', 'hidden', 'important');
						el.style.setProperty('pointer-events', 'none', 'important');
						el.style.setProperty('opacity', '0', 'important');
						el.style.setProperty('height', '0', 'important');
						el.style.setProperty('width', '0', 'important');
					}
				}
			});
		};

		killFullscreenAds();
		window.addEventListener('scroll', killFullscreenAds, { passive: true });
		window.addEventListener('resize', killFullscreenAds, { passive: true });

		if (window.MutationObserver) {
			var obs = new MutationObserver(killFullscreenAds);
			obs.observe(document.documentElement, { childList: true, subtree: true });
		}
	}

	/**
	 * サイドレール広告（Side Rail Ads）の画面幅判定制御
	 * PC（1024px以上）: 両側広告あってOK
	 * SP（1024px未満）: 画面両端の固定広告・サイドレール・オーバーレイ広告を完全排除
	 */
	function initSideRailAdsGuard() {
		var handleSideRails = function () {
			var isPcScreen = window.innerWidth >= 1024;
			var sideRailAndFixedAds = document.querySelectorAll(
				'.google-auto-placed[style*="fixed"], ' +
				'ins.adsbygoogle[data-ad-format*="rail"], ' +
				'div[id^="google_ads_iframe"][style*="fixed"], ' +
				'html > ins.adsbygoogle, ' +
				'html > .adsbygoogle-noablate, ' +
				'body > ins.adsbygoogle-noablate, ' +
				'div[id*="aswift"][style*="fixed"], ' +
				'iframe[id^="aswift_"][style*="fixed"]'
			);

			sideRailAndFixedAds.forEach(function (el) {
				if (isPcScreen) {
					// PCでは両側広告を表示
					el.style.removeProperty('display');
					el.style.removeProperty('visibility');
					el.style.removeProperty('opacity');
					el.style.removeProperty('pointer-events');
					el.style.setProperty('z-index', '80', 'important');
				} else {
					// SPでは両側の広告を完全排除
					el.style.setProperty('display', 'none', 'important');
					el.style.setProperty('visibility', 'hidden', 'important');
					el.style.setProperty('opacity', '0', 'important');
					el.style.setProperty('pointer-events', 'none', 'important');
				}
			});
		};

		handleSideRails();
		window.addEventListener('resize', handleSideRails);
		setTimeout(handleSideRails, 1000);
		setTimeout(handleSideRails, 2500);
		setTimeout(handleSideRails, 4500);

		if (window.MutationObserver) {
			var observer = new MutationObserver(handleSideRails);
			observer.observe(document.body, { childList: true, subtree: true });
			if (document.documentElement) {
				observer.observe(document.documentElement, { childList: true, subtree: true });
			}
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
				'section iframe[id^="aswift_"]',
				'section div[id^="google_ads_iframe"]',
				'.c-entry__section ins.adsbygoogle',
				'.c-entry__section .google-auto-placed',
				'.c-entry__section iframe[id^="aswift_"]',
				'.c-entry__section div[id^="google_ads_iframe"]',
				'.c-entry__section .adsbygoogle',
				'[data-ad-exclude="true"] ins.adsbygoogle',
				'[data-ad-exclude="true"] .google-auto-placed',
				'[data-ad-exclude="true"] iframe[id^="aswift_"]',
				'[data-ad-exclude="true"] div[id^="google_ads_iframe"]',
				'.c-vocab-box ins.adsbygoogle',
				'.c-vocab-box .google-auto-placed',
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

	/**
	 * ふりがな（ルビ）ON/OFF切り替え機能 ＆ Sticky追従制御
	 */
	function initRubyToggle() {
		var STORAGE_KEY = 'oscss_ruby_state';
		var toggleButtons = document.querySelectorAll('.js-ruby-toggle');
		var stickyWrapper = document.getElementById('ruby-sticky-toggle');

		// 初期状態（デフォルトはON。過去にOFFが明示的に保存されている場合のみOFF）
		var savedState = null;
		try {
			savedState = localStorage.getItem(STORAGE_KEY);
		} catch (e) {}

		var isHidden = (savedState === 'off');

		function updateUI(hidden) {
			if (hidden) {
				document.documentElement.classList.add('is-ruby-hidden');
				document.body.classList.add('is-ruby-hidden');
			} else {
				document.documentElement.classList.remove('is-ruby-hidden');
				document.body.classList.remove('is-ruby-hidden');
			}

			toggleButtons.forEach(function (btn) {
				var statusEl = btn.querySelector('.c-ruby-toggle__status');
				if (statusEl) {
					statusEl.textContent = hidden ? 'OFF' : 'ON';
				}
				btn.setAttribute('aria-pressed', hidden ? 'false' : 'true');
			});
		}

		// 初期状態の反映
		if (isHidden) {
			updateUI(true);
		}

		// クリックによるトグル切り替え
		toggleButtons.forEach(function (btn) {
			btn.addEventListener('click', function (e) {
				e.preventDefault();
				var currentlyHidden = document.body.classList.contains('is-ruby-hidden');
				var nextHidden = !currentlyHidden;

				updateUI(nextHidden);

				try {
					localStorage.setItem(STORAGE_KEY, nextHidden ? 'off' : 'on');
				} catch (e) {}
			});
		});

		// Stickyボタンのスクロール追従表示（スクロール150px以上でふわっと出現）
		if (stickyWrapper) {
			var handleStickyScroll = function () {
				if (window.scrollY > 150) {
					stickyWrapper.classList.add('is-visible');
				} else {
					stickyWrapper.classList.remove('is-visible');
				}
			};

			window.addEventListener('scroll', handleStickyScroll, { passive: true });
			handleStickyScroll();
		}
	}
})();

