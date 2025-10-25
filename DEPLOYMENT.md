# デプロイガイド

## Azure App Service へのデプロイ手順（詳細版）

### 前提条件

- Azureサブスクリプション
- Azure CLIのインストール
- GitHubアカウント
- Node.js 18.x 以上
- Python 3.11 以上

---

## 📋 ステップ1: Azureリソースの作成

### 1-1. リソースグループの作成

```bash
az group create \
  --name pos-app-rg \
  --location japaneast
```

### 1-2. App Service Plan の作成

```bash
# Basic B1 プラン（開発・テスト用）
az appservice plan create \
  --name pos-app-plan \
  --resource-group pos-app-rg \
  --sku B1 \
  --is-linux

# または、Free F1 プラン
az appservice plan create \
  --name pos-app-plan \
  --resource-group pos-app-rg \
  --sku F1 \
  --is-linux
```

### 1-3. バックエンド App Service の作成

```bash
az webapp create \
  --resource-group pos-app-rg \
  --plan pos-app-plan \
  --name pos-backend-app-<your-unique-id> \
  --runtime "PYTHON:3.11"
```

### 1-4. フロントエンド App Service の作成

```bash
az webapp create \
  --resource-group pos-app-rg \
  --plan pos-app-plan \
  --name pos-frontend-app-<your-unique-id> \
  --runtime "NODE:18-lts"
```

### 1-5. MySQL データベース（既に作成済みの場合はスキップ）

```bash
az mysql flexible-server create \
  --resource-group pos-app-rg \
  --name pos-mysql-server-<your-unique-id> \
  --location japaneast \
  --admin-user tech0gen10student \
  --admin-password <your-password> \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 20 \
  --version 8.0.21

# データベースの作成
az mysql flexible-server db create \
  --resource-group pos-app-rg \
  --server-name pos-mysql-server-<your-unique-id> \
  --database-name kondo2-pos
```

---

## 📋 ステップ2: Azure App Service の設定

### 2-1. バックエンドの環境変数設定

```bash
az webapp config appsettings set \
  --resource-group pos-app-rg \
  --name pos-backend-app-<your-unique-id> \
  --settings \
    DB_HOST="<your-mysql-server>.mysql.database.azure.com" \
    DB_DATABASE="kondo2-pos" \
    DB_USER="tech0gen10student" \
    DB_PASSWORD="<your-password>" \
    DB_PORT="3306" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true"
```

### 2-2. バックエンドのスタートアップコマンド設定

```bash
az webapp config set \
  --resource-group pos-app-rg \
  --name pos-backend-app-<your-unique-id> \
  --startup-file "startup.sh"
```

### 2-3. フロントエンドの環境変数設定

```bash
az webapp config appsettings set \
  --resource-group pos-app-rg \
  --name pos-frontend-app-<your-unique-id> \
  --settings \
    REACT_APP_API_URL="https://pos-backend-app-<your-unique-id>.azurewebsites.net"
```

---

## 📋 ステップ3: GitHub の設定

### 3-1. GitHubリポジトリの作成

1. GitHubにログイン
2. 新しいリポジトリを作成（例: pos-app）
3. ローカルリポジトリと連携

```bash
cd "c:\Users\ktomo\OneDrive\デスクトップ\POSアプリ"
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/pos-app.git
git push -u origin main
```

### 3-2. Publish Profile の取得

**バックエンド:**
```bash
az webapp deployment list-publishing-profiles \
  --resource-group pos-app-rg \
  --name pos-backend-app-<your-unique-id> \
  --xml
```

**フロントエンド:**
```bash
az webapp deployment list-publishing-profiles \
  --resource-group pos-app-rg \
  --name pos-frontend-app-<your-unique-id> \
  --xml
```

出力されたXML全体をコピーしておく

### 3-3. GitHub Secrets の設定

GitHubリポジトリで: Settings > Secrets and variables > Actions > New repository secret

以下のSecretsを追加:

| Secret名 | 値 |
|---------|-----|
| `AZURE_BACKEND_PUBLISH_PROFILE` | バックエンドのPublish Profile（XML全体） |
| `AZURE_FRONTEND_PUBLISH_PROFILE` | フロントエンドのPublish Profile（XML全体） |
| `DB_HOST` | MySQLサーバーのホスト名 |
| `DB_DATABASE` | kondo2-pos |
| `DB_USER` | tech0gen10student |
| `DB_PASSWORD` | データベースのパスワード |
| `DB_PORT` | 3306 |
| `REACT_APP_API_URL` | https://pos-backend-app-<your-unique-id>.azurewebsites.net |

### 3-4. ワークフローファイルの更新

`.github/workflows/backend-deploy.yml`:
```yaml
env:
  AZURE_WEBAPP_NAME: pos-backend-app-<your-unique-id>
```

`.github/workflows/frontend-deploy.yml`:
```yaml
env:
  AZURE_WEBAPP_NAME: pos-frontend-app-<your-unique-id>
```

---

## 📋 ステップ4: デプロイ実行

### 4-1. 変更をプッシュ

```bash
git add .
git commit -m "Update app names for deployment"
git push origin main
```

### 4-2. GitHub Actionsの確認

1. GitHubリポジトリの「Actions」タブを開く
2. ワークフローの実行状況を確認
3. エラーがある場合はログを確認して修正

### 4-3. デプロイ確認

**バックエンド:**
```
https://pos-backend-app-<your-unique-id>.azurewebsites.net/docs
```

**フロントエンド:**
```
https://pos-frontend-app-<your-unique-id>.azurewebsites.net
```

---

## 🔧 トラブルシューティング

### エラー1: データベース接続エラー

**原因:** ファイアウォール設定

**解決策:**
```bash
# Azureサービスからのアクセスを許可
az mysql flexible-server firewall-rule create \
  --resource-group pos-app-rg \
  --name pos-mysql-server-<your-unique-id> \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# 特定のIPアドレスを許可
az mysql flexible-server firewall-rule create \
  --resource-group pos-app-rg \
  --name pos-mysql-server-<your-unique-id> \
  --rule-name AllowMyIP \
  --start-ip-address <your-ip> \
  --end-ip-address <your-ip>
```

### エラー2: CORS エラー

**原因:** フロントエンドからバックエンドへのアクセスがブロックされている

**解決策:** `backend/main.py` のCORS設定を更新
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pos-frontend-app-<your-unique-id>.azurewebsites.net",
        "http://localhost:3000"  # ローカル開発用
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### エラー3: Publish Profile が無効

**原因:** Publish Profileの期限切れ

**解決策:**
1. Publish Profileを再取得
2. GitHub Secretsを更新

### エラー4: Node.js ビルドエラー

**原因:** メモリ不足

**解決策:**
```bash
# App Serviceのプランをアップグレード
az appservice plan update \
  --name pos-app-plan \
  --resource-group pos-app-rg \
  --sku B2
```

---

## 📊 モニタリング

### ログの確認

**バックエンド:**
```bash
az webapp log tail \
  --resource-group pos-app-rg \
  --name pos-backend-app-<your-unique-id>
```

**フロントエンド:**
```bash
az webapp log tail \
  --resource-group pos-app-rg \
  --name pos-frontend-app-<your-unique-id>
```

### Application Insights の有効化（オプション）

```bash
# Application Insightsの作成
az monitor app-insights component create \
  --app pos-app-insights \
  --location japaneast \
  --resource-group pos-app-rg

# App ServiceにApplication Insightsを接続
az monitor app-insights component connect-webapp \
  --app pos-app-insights \
  --resource-group pos-app-rg \
  --web-app pos-backend-app-<your-unique-id>
```

---

## 🔄 継続的デプロイメント

### 自動デプロイの仕組み

1. `main`ブランチに変更をプッシュ
2. GitHub Actionsが自動的にトリガーされる
3. 変更されたディレクトリ（frontend/ または backend/）に応じて該当するワークフローが実行
4. ビルドとデプロイが自動実行
5. デプロイ完了

### 手動デプロイ

GitHub Actionsタブから「Run workflow」ボタンで手動実行可能

---

## 💰 コスト管理

### 推奨プラン

**開発・テスト環境:**
- App Service Plan: F1 (Free) または B1 (Basic)
- MySQL: Burstable B1ms

**本番環境:**
- App Service Plan: S1 (Standard) 以上
- MySQL: GeneralPurpose D2ds_v4 以上

### コスト削減のヒント

1. 使用していない時間帯はApp Serviceを停止
2. App Service Planを共有
3. 開発環境はローカルで実行

---

## 📝 チェックリスト

デプロイ前の確認事項:

- [ ] Azureリソース（App Service x2, MySQL）が作成済み
- [ ] データベースにテーブルとサンプルデータが投入済み
- [ ] GitHub Secretsが全て設定済み
- [ ] ワークフローファイルのアプリ名が正しい
- [ ] MySQLのファイアウォール設定が適切
- [ ] CORSの設定が適切
- [ ] 環境変数が正しく設定されている

デプロイ後の確認事項:

- [ ] バックエンドのヘルスチェック (`/api/health`) が正常
- [ ] バックエンドのAPIドキュメント (`/docs`) が表示される
- [ ] フロントエンドが正常に表示される
- [ ] 商品検索機能が動作する
- [ ] 購入処理が正常に完了する
- [ ] データベースに取引データが記録される

