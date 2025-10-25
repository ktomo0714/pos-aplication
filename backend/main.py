"""
POSアプリケーション バックエンドAPI
FastAPIを使用したRESTful API
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from contextlib import asynccontextmanager
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, ForeignKey, Index
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from sqlalchemy.sql import func
import urllib.parse
import os
from datetime import datetime


# ===== ライフサイクルイベント =====

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    # 起動時の処理
    print("=" * 60)
    print("POSアプリケーションAPI 起動中...")
    print("=" * 60)
    print(f"データベース接続先: {os.getenv('DB_HOST', 'localhost')}")
    print(f"データベース名: {os.getenv('DB_DATABASE', 'kondo2-pos')}")
    print("=" * 60)
    
    yield
    
    # 終了時の処理
    print("POSアプリケーションAPI 終了")


# FastAPIアプリケーション
app = FastAPI(
    title="POSアプリケーションAPI",
    description="商品マスタ検索と購入処理を行うAPI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS設定（フロントエンドからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では具体的なドメインを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データベース設定
Base = declarative_base()


# ===== データベースモデル =====

class ProductMaster(Base):
    """商品マスタテーブル"""
    __tablename__ = 'product_master'
    
    PRD_ID = Column(Integer, primary_key=True, autoincrement=True, comment='商品一意キー')
    CODE = Column(String(13), nullable=False, unique=True, comment='商品コード')
    NAME = Column(String(50), nullable=True, comment='商品名称')
    PRICE = Column(Integer, nullable=True, comment='商品単価')
    
    transaction_details = relationship('TransactionDetail', back_populates='product')
    
    __table_args__ = (
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    )


class Transaction(Base):
    """取引テーブル"""
    __tablename__ = 'transaction'
    
    TRD_ID = Column(Integer, primary_key=True, autoincrement=True, comment='取引一意キー')
    DATETIME = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), comment='取引日時')
    EMP_CD = Column(String(10), nullable=False, default='9999999999', comment='レシ担当者コード')
    STORE_CD = Column(String(5), nullable=False, comment='店舗コード')
    POS_NO = Column(String(3), nullable=False, default='90', comment='POS機ID')
    TOTAL_AMT = Column(Integer, nullable=False, default=0, comment='合計金額')
    
    details = relationship('TransactionDetail', back_populates='transaction', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('idx_datetime', 'DATETIME'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    )


class TransactionDetail(Base):
    """取引明細テーブル"""
    __tablename__ = 'transaction_detail'
    
    TRD_ID = Column(Integer, ForeignKey('transaction.TRD_ID', ondelete='CASCADE'), primary_key=True, comment='取引一意キー')
    DTL_ID = Column(Integer, primary_key=True, comment='取引明細一意キー')
    PRD_ID = Column(Integer, ForeignKey('product_master.PRD_ID'), nullable=False, comment='商品一意キー')
    PRD_CODE = Column(String(13), nullable=False, comment='商品コード')
    PRD_NAME = Column(String(50), nullable=False, comment='商品名称')
    PRD_PRICE = Column(Integer, nullable=False, comment='商品単価')
    
    transaction = relationship('Transaction', back_populates='details')
    product = relationship('ProductMaster', back_populates='transaction_details')
    
    __table_args__ = (
        Index('idx_prd_id', 'PRD_ID'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    )


# ===== Pydanticモデル（API入出力） =====

class ProductResponse(BaseModel):
    """商品情報レスポンス"""
    PRD_ID: Optional[int] = Field(None, description="商品一意キー")
    CODE: Optional[str] = Field(None, description="商品コード")
    NAME: Optional[str] = Field(None, description="商品名称")
    PRICE: Optional[int] = Field(None, description="商品単価")
    
    class Config:
        from_attributes = True


class PurchaseItem(BaseModel):
    """購入商品アイテム"""
    PRD_ID: int = Field(..., description="商品一意キー")
    PRD_CODE: str = Field(..., description="商品コード")
    PRD_NAME: str = Field(..., description="商品名称")
    PRD_PRICE: int = Field(..., description="商品単価")


class PurchaseRequest(BaseModel):
    """購入リクエスト"""
    EMP_CD: Optional[str] = Field("9999999999", description="レシ担当者コード")
    STORE_CD: str = Field("30", description="店舗コード")
    POS_NO: str = Field("90", description="POS機ID")
    items: List[PurchaseItem] = Field(..., description="購入商品リスト")


class PurchaseResponse(BaseModel):
    """購入レスポンス"""
    success: bool = Field(..., description="成否")
    total_amount: int = Field(..., description="合計金額")
    transaction_id: int = Field(..., description="取引ID")
    message: str = Field(..., description="メッセージ")


# ===== データベース接続 =====

def get_database_url():
    """環境変数からデータベースURLを生成"""
    host = os.getenv('DB_HOST', 'localhost')
    database = os.getenv('DB_DATABASE', 'kondo2-pos')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')
    port = os.getenv('DB_PORT', '3306')
    
    encoded_password = urllib.parse.quote_plus(password)
    
    return (
        f"mysql+pymysql://{user}:{encoded_password}@{host}:{port}/{database}"
        f"?charset=utf8mb4&ssl_ca=&ssl_verify_cert=true"
    )


# エンジン作成
engine = create_engine(
    get_database_url(),
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# セッション作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """データベースセッションの依存性注入"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===== APIエンドポイント =====

@app.get("/")
def read_root():
    """ルートエンドポイント"""
    return {
        "message": "POSアプリケーションAPI",
        "version": "1.0.0",
        "endpoints": {
            "商品マスタ検索": "/api/products/{code}",
            "購入": "/api/purchase"
        }
    }


@app.get("/api/health")
def health_check():
    """ヘルスチェック"""
    try:
        # データベース接続確認
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.get("/api/products/{code}", response_model=ProductResponse)
def search_product(code: str, db: Session = Depends(get_db)):
    """
    商品マスタ検索
    
    Args:
        code: 商品コード（13桁）
        
    Returns:
        商品情報（見つからない場合はNULL情報）
    """
    try:
        # 商品コードで検索
        product = db.query(ProductMaster).filter(ProductMaster.CODE == code).first()
        
        if product:
            return ProductResponse(
                PRD_ID=product.PRD_ID,
                CODE=product.CODE,
                NAME=product.NAME,
                PRICE=product.PRICE
            )
        else:
            # 見つからない場合はNULL情報を返却
            return ProductResponse(
                PRD_ID=None,
                CODE=None,
                NAME=None,
                PRICE=None
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"商品検索エラー: {str(e)}")


@app.post("/api/purchase", response_model=PurchaseResponse)
def purchase(request: PurchaseRequest, db: Session = Depends(get_db)):
    """
    購入処理
    
    Args:
        request: 購入リクエスト（担当者コード、店舗コード、POS機ID、商品リスト）
        
    Returns:
        購入レスポンス（成否、合計金額）
    """
    try:
        # 1-1: 取引テーブルへ登録
        transaction = Transaction(
            EMP_CD=request.EMP_CD or "9999999999",
            STORE_CD=request.STORE_CD,
            POS_NO=request.POS_NO,
            TOTAL_AMT=0
        )
        db.add(transaction)
        db.flush()  # TRD_IDを取得するためflush
        
        # 1-2: 取引明細へ登録
        total_amount = 0
        for idx, item in enumerate(request.items, start=1):
            detail = TransactionDetail(
                TRD_ID=transaction.TRD_ID,
                DTL_ID=idx,  # 取引ごとに1から採番
                PRD_ID=item.PRD_ID,
                PRD_CODE=item.PRD_CODE,
                PRD_NAME=item.PRD_NAME,
                PRD_PRICE=item.PRD_PRICE
            )
            db.add(detail)
            
            # 1-3: 合計を計算
            total_amount += item.PRD_PRICE
        
        # 1-4: 取引テーブルを更新（合計金額を設定）
        transaction.TOTAL_AMT = total_amount
        
        # コミット
        db.commit()
        
        # 1-5: 合計金額をフロントへ返却
        return PurchaseResponse(
            success=True,
            total_amount=total_amount,
            transaction_id=transaction.TRD_ID,
            message="購入処理が正常に完了しました"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"購入処理エラー: {str(e)}")


@app.get("/api/products")
def list_products(db: Session = Depends(get_db)):
    """商品マスタ一覧取得（開発・テスト用）"""
    try:
        products = db.query(ProductMaster).all()
        return {
            "count": len(products),
            "products": [
                {
                    "PRD_ID": p.PRD_ID,
                    "CODE": p.CODE,
                    "NAME": p.NAME,
                    "PRICE": p.PRICE
                }
                for p in products
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"商品一覧取得エラー: {str(e)}")




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

