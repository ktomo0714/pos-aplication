#!/bin/bash
# Azure App Service スタートアップスクリプト

# 仮想環境をアクティベート（存在する場合）
if [ -d "antenv" ]; then
    source antenv/bin/activate
fi

# 依存関係のインストール
pip install --upgrade pip
pip install -r requirements.txt

# Uvicornでアプリケーションを起動
# Azure App Serviceは環境変数 PORT を提供
python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

