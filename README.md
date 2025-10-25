# POSアプリケーション

Azure App ServiceとAzure Database for MySQLを使用したPOSアプリケーション

## 📋 概要

このアプリケーションは、商品マスタ検索と購入処理を行うPOSシステムです。
- **フロントエンド**: React (Node.js)
- **バックエンド**: FastAPI (Python)
- **データベース**: Azure Database for MySQL
- **デプロイ**: Azure App Service + GitHub Actions

## 🏗️ プロジェクト構造

```
POSアプリ/
├── frontend/                    # フロントエンド（React）
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js              # メインコンポーネント
│   │   ├── App.css             # スタイル
│   │   ├── index.js
│   │   └── index.css
│   └── package.json
│
├── backend/                     # バックエンド（FastAPI）
│   ├── main.py                 # APIエンドポイント
│   ├── requirements.txt        # Python依存パッケージ
│   ├── startup.sh              # Azure起動スクリプト
│   └── .deployment
│
├── .github/
│   └── workflows/
│       ├── frontend-deploy.yml # フロントエンド自動デプロイ
│       └── backend-deploy.yml  # バックエンド自動デプロイ
│
├── setup_database.py           # データベース初期化スクリプト
├── env.sample                  # 環境変数サンプル
└── README.md
```

## 🚀 セットアップ手順

### 1. リポジトリのクローン

```bash
git clone <your-repository-url>
cd POSアプリ
```

### 2. データベースのセットアップ

```bash
# env.sampleをコピーして.envを作成（ルートディレクトリ）
cp env.sample .env

# .envファイルを編集してデータベース接続情報を設定
# DB_HOST=your-mysql-server.mysql.database.azure.com
# DB_DATABASE=kondo2-pos
# DB_USER=your-username
# DB_PASSWORD=your-password

# データベースとテーブルを作成
python setup_database.py
```

### 3. バックエンドのローカル実行

```bash
cd backend

# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt

# 環境変数を設定（env.sampleの内容をコピー）
# Windowsの場合:
set DB_HOST=your-mysql-server.mysql.database.azure.com
set DB_DATABASE=kondo2-pos
set DB_USER=your-username
set DB_PASSWORD=your-password

# Linuxの場合:
export DB_HOST=your-mysql-server.mysql.database.azure.com
export DB_DATABASE=kondo2-pos
export DB_USER=your-username
export DB_PASSWORD=your-password

# アプリケーション起動
python main.py
# または
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# ブラウザで http://localhost:8000/docs にアクセスしてAPIドキュメントを確認
```

### 4. フロントエンドのローカル実行

```bash
cd frontend

# 依存パッケージのインストール
npm install

# 環境変数の設定（.env.localファイルを作成）
echo "REACT_APP_API_URL=http://localhost:8000" > .env.local

# アプリケーション起動
npm start

# ブラウザで http://localhost:3000 にアクセス
```

## 🌐 Azure App Service へのデプロイ

### 前提条件

1. Azureアカウント
2. Azure App Service x2（フロントエンド・バックエンド用）
3. Azure Database for MySQL
4. GitHubアカウント

### デプロイ手順

#### 1. Azure App Service の作成

**バックエンド用:**
```bash
# Azure CLIでApp Serviceを作成
az webapp create \
  --resource-group <your-resource-group> \
  --plan <your-app-service-plan> \
  --name <backend-app-name> \
  --runtime "PYTHON:3.11"
```

**フロントエンド用:**
```bash
az webapp create \
  --resource-group <your-resource-group> \
  --plan <your-app-service-plan> \
  --name <frontend-app-name> \
  --runtime "NODE:18-lts"
```

#### 2. GitHub Secrets の設定

GitHubリポジトリの Settings > Secrets and variables > Actions で以下を設定:

**Publish Profiles:**
- `AZURE_BACKEND_PUBLISH_PROFILE`: バックエンドのPublish Profile
- `AZURE_FRONTEND_PUBLISH_PROFILE`: フロントエンドのPublish Profile

**データベース接続情報:**
- `DB_HOST`: MySQLサーバーのホスト名
- `DB_DATABASE`: データベース名（kondo2-pos）
- `DB_USER`: ユーザー名
- `DB_PASSWORD`: パスワード
- `DB_PORT`: ポート番号（3306）

**API URL:**
- `REACT_APP_API_URL`: バックエンドのURL（例: https://your-backend-app.azurewebsites.net）

#### 3. ワークフローファイルの更新

`.github/workflows/backend-deploy.yml` と `.github/workflows/frontend-deploy.yml` の `AZURE_WEBAPP_NAME` を実際のApp Service名に変更:

```yaml
env:
  AZURE_WEBAPP_NAME: your-actual-app-name
```

#### 4. デプロイ実行

```bash
# mainブランチにプッシュすると自動的にデプロイが開始
git add .
git commit -m "Initial commit"
git push origin main
```

GitHubの Actions タブでデプロイの進行状況を確認できます。

## 📱 API仕様

### 1. 商品マスタ検索

**エンドポイント:** `GET /api/products/{code}`

**リクエスト:**
```
GET /api/products/4901234567890
```

**レスポンス:**
```json
{
  "PRD_ID": 1,
  "CODE": "4901234567890",
  "NAME": "ソフコン",
  "PRICE": 300
}
```

商品が見つからない場合:
```json
{
  "PRD_ID": null,
  "CODE": null,
  "NAME": null,
  "PRICE": null
}
```

### 2. 購入処理

**エンドポイント:** `POST /api/purchase`

**リクエスト:**
```json
{
  "EMP_CD": "9999999999",
  "STORE_CD": "30",
  "POS_NO": "90",
  "items": [
    {
      "PRD_ID": 1,
      "PRD_CODE": "4901234567890",
      "PRD_NAME": "ソフコン",
      "PRD_PRICE": 300
    },
    {
      "PRD_ID": 2,
      "PRD_CODE": "4901234567891",
      "PRD_NAME": "福島県ほうれん草",
      "PRD_PRICE": 188
    }
  ]
}
```

**レスポンス:**
```json
{
  "success": true,
  "total_amount": 488,
  "transaction_id": 1,
  "message": "購入処理が正常に完了しました"
}
```

## 🗄️ データベーススキーマ

### product_master (商品マスタ)
| カラム名 | 型 | 説明 |
|---------|-----|------|
| PRD_ID | INT | 商品一意キー (PK, AUTO_INCREMENT) |
| CODE | CHAR(13) | 商品コード (UNIQUE) |
| NAME | VARCHAR(50) | 商品名称 |
| PRICE | INT | 商品単価 |

### transaction (取引)
| カラム名 | 型 | 説明 |
|---------|-----|------|
| TRD_ID | INT | 取引一意キー (PK, AUTO_INCREMENT) |
| DATETIME | TIMESTAMP | 取引日時 |
| EMP_CD | CHAR(10) | レシ担当者コード |
| STORE_CD | CHAR(5) | 店舗コード |
| POS_NO | CHAR(3) | POS機ID |
| TOTAL_AMT | INT | 合計金額 |

### transaction_detail (取引明細)
| カラム名 | 型 | 説明 |
|---------|-----|------|
| TRD_ID | INT | 取引一意キー (PK, FK) |
| DTL_ID | INT | 取引明細一意キー (PK) |
| PRD_ID | INT | 商品一意キー (FK) |
| PRD_CODE | CHAR(13) | 商品コード |
| PRD_NAME | VARCHAR(50) | 商品名称 |
| PRD_PRICE | INT | 商品単価 |

## 🔧 トラブルシューティング

### データベース接続エラー

1. ファイアウォール設定を確認
   - Azure Portal > MySQL > 接続のセキュリティ
   - 接続元IPアドレスが許可されているか確認

2. 接続情報を確認
   - ホスト名、ユーザー名、パスワードが正しいか確認

### CORS エラー

バックエンドの `main.py` でCORS設定を確認:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-app.azurewebsites.net"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### GitHub Actions デプロイエラー

1. Secrets が正しく設定されているか確認
2. Publish Profile が最新か確認（期限切れの場合は再取得）
3. App Service の状態を確認

## 📝 開発メモ

### ローカル開発時の注意点

- バックエンドとフロントエンドを同時に起動する必要があります
- バックエンド: http://localhost:8000
- フロントエンド: http://localhost:3000

### サンプルデータ

`setup_database.py` を実行すると以下のサンプル商品が登録されます:
- 4901234567890: ソフコン (300円)
- 4901234567891: 福島県ほうれん草 (188円)
- 4901234567892: タイガー歯ブラシ青 (200円)
- 4901234567893: 四ツ谷サイダー (160円)

## 📄 ライセンス

このプロジェクトは教育目的で作成されています。

## 👥 作成者

Tech0 Gen10 Step4 POS課題

