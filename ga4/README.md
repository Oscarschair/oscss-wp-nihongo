# GA4 カスタム定義・イベント計測管理ディレクトリ (`/ga4`)

本ディレクトリは、「オスカーの日本語学習帳（`https://nihongo.oscarchair.jp/`）」の Google Analytics 4（GA4）プロパティに登録されたカスタムディメンション・カスタム指標・計算指標・キーイベントの正本定義データを管理します。

---

## 📌 対象アカウント・プロパティ情報

| 項目 | 設定値 |
| :--- | :--- |
| **GA4 アカウント** | オスカーの日本語学習帳 (`accounts/257613185`) |
| **GA4 プロパティ** | `nihongo.oscarchair.jp` (`properties/354369646`) |
| **データストリーム** | `nihongo.oscarchair.jp` (`dataStreams/4639754830`) |
| **測定ID** | `G-3QBPY87VPP` |
| **連携GTMコンテナ** | `GTM-K6NZHVDJ` (`accounts/6004690865/containers/265349373` / エクスポート定義: `../gtm/GTM.json`) |

---

## 📂 管理ファイル一覧

| ファイル名 | 内容 |
| :--- | :--- |
| `custom_dimensions.json` | GA4 Admin API で登録・取得したカスタムディメンション一覧（イベントスコープ・ユーザースコープ） |
| `custom_metrics.json` | GA4 Admin API で登録・取得したカスタム指標一覧（キーイベント4種＋一般イベント15種） |
| `calculated_metrics.json` | GA4 Admin API で登録・取得した計算指標一覧（回遊率・読了率・ルビ利用率・CTR・送客率） |
| `key_events.json` | GA4 Admin API で登録・取得したキーイベント一覧 |
| `custom_definitions_all.json` | プロパティ設定・データストリーム・全カスタム定義・計算指標・キーイベントを統合したマスターJSON |
