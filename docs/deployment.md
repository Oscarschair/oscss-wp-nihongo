# デプロイ・環境構築・運用手順書 (Deployment Guide)

本ドキュメントでは、WordPressカスタムテーマ「oscss-wp-nihongo」のインストール、有効化、ローカル開発環境での利用、およびデプロイ手順を説明します。

---

## 1. テーマのインストールと有効化

### 手順
1. 本リポジトリのディレクトリ（`oscss-wp-nihongo`）を WordPress の `wp-content/themes/` 配下に配置します。
   ```bash
   # 例: WordPressインストールディレクトリ配下のテーマフォルダにクローンまたはコピー
   cp -r oscss-wp-nihongo /path/to/wordpress/wp-content/themes/
   ```
2. WordPress管理画面にログインし、**外観 > テーマ** へ移動します。
3. **「oscss-wp-nihongo」** を選択し、「有効化」をクリックします。

---

## 2. 推奨設定

### ナビゲーションメニュー
- 管理画面の **外観 > メニュー** より、メニューを作成し、テーマ位置 **「メインナビゲーション（Primary Navigation）」** に割り当ててください。

### アイキャッチ画像
- 投稿作成時に「アイキャッチ画像」を設定すると、トップページやアーカイブの記事カード、および個別投稿のヘッダーに自動的に最適化されて表示されます。

---

## 3. ファイル構造と更新手順

- スタイルの変更: `assets/css/tokens.css`（変数）および `assets/css/main.css` を編集します。
- スクリプトの変更: `assets/js/main.js` を編集します。
- 関数の追加: `functions/` 配下の適切なファイル（`action.php`, `filter.php`, `utility.php`, `shortcode.php`）に追加します。
