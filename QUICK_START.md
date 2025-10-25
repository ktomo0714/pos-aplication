# クイックスタートガイド

POSアプリケーションを最速で動かすための手順

## 🚀 5分で起動

### 1. データベースの準備（2分）

```bash
# 1. env.sampleの内容を確認（既に設定済み）
cat env.sample

# 2. データベースとサンプルデータを作成
python setup_database.py
```

### 2. バックエンドの起動（1分）

新しいターミナルを開いて:

```bash
cd backend
pip install -r requirements.txt
python main.py
```

✅ ブラウザで確認: http://localhost:8000/docs

### 3. フロントエンドの起動（2分）

別の新しいターミナルを開いて:

```bash
cd frontend
npm install
npm start
```

✅ ブラウザで確認: http://localhost:3000

---

## 📱 使い方

### 商品を検索して購入

1. **商品コードを入力**
   ```
   4901234567890  → ソフコン（300円）
   4901234567891  → 福島県ほうれん草（188円）
   4901234567892  → タイガー歯ブラシ青（200円）
   4901234567893  → 四ツ谷サイダー（160円）
   ```

2. **「商品コード読み込み」をクリック**
   - 商品名称と単価が表示されます

3. **「追加」をクリック**
   - 右側の購入リストに追加されます

4. **複数商品を追加後、「購入」をクリック**
   - 合計金額が表示されます
   - データベースに取引が記録されます

---

## 🔍 動作確認

### APIを直接テスト

```bash
# 商品検索
curl http://localhost:8000/api/products/4901234567890

# 購入処理
curl -X POST http://localhost:8000/api/purchase \
  -H "Content-Type: application/json" \
  -d '{
    "EMP_CD": "9999999999",
    "STORE_CD": "30",
    "POS_NO": "90",
    "items": [
      {
        "PRD_ID": 1,
        "PRD_CODE": "4901234567890",
        "PRD_NAME": "ソフコン",
        "PRD_PRICE": 300
      }
    ]
  }'
```

### データベースを確認

MySQLクライアントで接続:

```sql
-- 商品一覧
SELECT * FROM product_master;

-- 取引一覧
SELECT * FROM transaction;

-- 取引明細
SELECT * FROM transaction_detail;
```

---

## 🌐 Azureにデプロイ

詳細は `DEPLOYMENT.md` を参照してください。

簡易版:

```bash
# 1. GitHubにプッシュ
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/pos-app.git
git push -u origin main

# 2. GitHub Secretsを設定
# Settings > Secrets and variables > Actions

# 3. 自動デプロイが開始されます！
```

---

## 💡 開発のヒント

### ホットリロード

- **バックエンド**: コード変更時に自動再起動
  ```bash
  uvicorn main:app --reload
  ```

- **フロントエンド**: コード変更時に自動更新（npm startで有効）

### デバッグ

**バックエンド:**
- FastAPIの自動生成ドキュメント: http://localhost:8000/docs
- ログ出力: `print()` または `logging`

**フロントエンド:**
- ブラウザのDevTools（F12）
- React Developer Tools（Chrome拡張機能）

### VSCode推奨拡張機能

- Python
- Pylance
- ES7+ React/Redux/React-Native snippets
- REST Client
- GitLens

---

## ❓ よくある質問

**Q: ポート8000が既に使用されています**
```bash
# 別のポートで起動
uvicorn main:app --port 8001
```

**Q: npm installが遅い**
```bash
# npmキャッシュをクリア
npm cache clean --force
```

**Q: データベース接続エラー**
```bash
# 1. env.sampleの内容を確認
# 2. MySQLが起動しているか確認
# 3. ファイアウォール設定を確認
```

**Q: CORSエラーが出る**
- バックエンドが起動しているか確認
- `backend/main.py` のCORS設定を確認

---

## 📞 サポート

問題が解決しない場合:

1. `README.md` の「トラブルシューティング」を確認
2. `DEPLOYMENT.md` の詳細手順を確認
3. GitHubのIssuesで質問

---

## 🎉 完了！

これでPOSアプリケーションが動作しています！

次のステップ:
- [ ] 独自の商品を追加
- [ ] UIをカスタマイズ
- [ ] Azureにデプロイ
- [ ] 機能を拡張

