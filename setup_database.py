"""
POSアプリケーション データベース構築スクリプト
env.sampleから接続情報を読み込んでテーブルとサンプルデータを作成
"""

from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import urllib.parse
import os

# Base クラスの作成
Base = declarative_base()


class ProductMaster(Base):
    """商品マスタテーブル"""
    __tablename__ = 'product_master'
    
    PRD_ID = Column(Integer, primary_key=True, autoincrement=True, comment='商品一意キー')
    CODE = Column(String(13), nullable=False, unique=True, comment='商品コード')
    NAME = Column(String(50), nullable=True, comment='商品名称')
    PRICE = Column(Integer, nullable=True, comment='商品単価')
    
    # リレーション
    transaction_details = relationship('TransactionDetail', back_populates='product')
    
    __table_args__ = (
        {'comment': '商品マスタ', 'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
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
    
    # リレーション
    details = relationship('TransactionDetail', back_populates='transaction', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('idx_datetime', 'DATETIME'),
        {'comment': '取引', 'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
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
    
    # リレーション
    transaction = relationship('Transaction', back_populates='details')
    product = relationship('ProductMaster', back_populates='transaction_details')
    
    __table_args__ = (
        Index('idx_prd_id', 'PRD_ID'),
        {'comment': '取引明細', 'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    )


def load_env_from_file(filepath):
    """
    env.sampleファイルから環境変数を読み込む
    
    Args:
        filepath: env.sampleファイルのパス
    
    Returns:
        環境変数の辞書
    """
    env_vars = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # コメント行と空行をスキップ
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        return env_vars
    except FileNotFoundError:
        print(f"エラー: {filepath} が見つかりません。")
        return None


def get_engine_from_env_file():
    """
    env.sampleまたは.envファイルから接続情報を取得してエンジンを作成
    
    Returns:
        SQLAlchemyエンジン
    """
    # スクリプトのディレクトリを取得
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # .envファイルを優先的に読み込み、なければenv.sampleを使用
    env_file = os.path.join(script_dir, '.env')
    if not os.path.exists(env_file):
        env_file = os.path.join(script_dir, 'env.sample')
        print(f"env.sampleファイルから接続情報を読み込みます: {env_file}")
    else:
        print(f".envファイルから接続情報を読み込みます: {env_file}")
    
    env_vars = load_env_from_file(env_file)
    
    if not env_vars:
        raise ValueError("環境変数ファイルの読み込みに失敗しました。")
    
    host = env_vars.get('DB_HOST')
    database = env_vars.get('DB_DATABASE', 'posappdb')
    user = env_vars.get('DB_USER')
    password = env_vars.get('DB_PASSWORD')
    port = env_vars.get('DB_PORT', '3306')
    
    # 必須パラメータチェック
    if not all([host, user, password]):
        raise ValueError("DB_HOST, DB_USER, DB_PASSWORD が設定されていません。")
    
    print(f"\n接続情報:")
    print(f"  ホスト: {host}")
    print(f"  データベース: {database}")
    print(f"  ユーザー: {user}")
    print(f"  ポート: {port}")
    
    # パスワードをURLエンコード
    encoded_password = urllib.parse.quote_plus(password)
    
    # Azure Database for MySQL用の接続文字列
    connection_string = (
        f"mysql+pymysql://{user}:{encoded_password}@{host}:{port}/{database}"
        f"?charset=utf8mb4&ssl_ca=&ssl_verify_cert=true"
    )
    
    engine = create_engine(
        connection_string,
        echo=False,
        pool_pre_ping=True,
    )
    
    return engine


def create_tables(engine):
    """
    テーブルを作成
    
    Args:
        engine: SQLAlchemyエンジン
    """
    print("\nテーブル作成を開始します...")
    Base.metadata.create_all(engine)
    print("[OK] テーブル作成が完了しました。")


def insert_sample_data(engine):
    """
    サンプルデータを投入
    
    Args:
        engine: SQLAlchemyエンジン
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("\nサンプルデータ投入を開始します...")
        
        # 商品マスタのサンプルデータ（データ定義書より）
        sample_products = [
            ProductMaster(CODE='4901234567890', NAME='ソフコン', PRICE=300),
            ProductMaster(CODE='4901234567891', NAME='福島県ほうれん草', PRICE=188),
            ProductMaster(CODE='4901234567892', NAME='タイガー歯ブラシ青', PRICE=200),
            ProductMaster(CODE='4901234567893', NAME='四ツ谷サイダー', PRICE=160),
        ]
        
        # 既存データがあるかチェック
        existing_count = session.query(ProductMaster).count()
        
        if existing_count == 0:
            session.add_all(sample_products)
            session.commit()
            print(f"[OK] サンプルデータを{len(sample_products)}件投入しました。")
            
            # 投入したデータを表示
            print("\n投入された商品マスタデータ:")
            for product in sample_products:
                print(f"  - {product.CODE}: {product.NAME} ({product.PRICE}円)")
        else:
            print(f"既にデータが存在します（{existing_count}件）。サンプルデータの投入をスキップします。")
        
    except Exception as e:
        session.rollback()
        print(f"[ERROR] エラーが発生しました: {e}")
        raise
    finally:
        session.close()


def verify_tables(engine):
    """
    テーブルが正しく作成されたか確認
    
    Args:
        engine: SQLAlchemyエンジン
    """
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("\n作成されたテーブル一覧:")
    for table in tables:
        columns = inspector.get_columns(table)
        print(f"  [OK] {table} (カラム数: {len(columns)})")


def main():
    """
    メイン処理
    """
    print("=" * 60)
    print("POSアプリケーション データベース構築スクリプト")
    print("=" * 60)
    
    try:
        # エンジンの作成
        engine = get_engine_from_env_file()
        
        # 接続テスト
        print("\nデータベースに接続しています...")
        with engine.connect() as conn:
            print("[OK] 接続成功！")
        
        # テーブル作成
        create_tables(engine)
        
        # テーブル確認
        verify_tables(engine)
        
        # サンプルデータ投入
        insert_sample_data(engine)
        
        print("\n" + "=" * 60)
        print("[SUCCESS] データベース構築が完了しました！")
        print("=" * 60)
        
        print("\n次のステップ:")
        print("  1. Azure PortalでFirewall設定を確認してください")
        print("  2. MySQLクライアントツールで接続を確認してください")
        print("  3. POSアプリケーションから接続テストを行ってください")
        
    except ValueError as e:
        print(f"\n[ERROR] 設定エラー: {e}")
        print("\nenv.sample ファイルに以下の環境変数が設定されているか確認してください:")
        print("  DB_HOST=your-server-name.mysql.database.azure.com")
        print("  DB_DATABASE=kondo2-pos")
        print("  DB_USER=your-username")
        print("  DB_PASSWORD=your-password")
        print("  DB_PORT=3306")
        
    except Exception as e:
        print(f"\n[ERROR] エラーが発生しました: {e}")
        print("\n接続情報を確認してください:")
        print("  - ホスト名が正しいか")
        print("  - データベース名が存在するか")
        print("  - ユーザー名とパスワードが正しいか")
        print("  - ファイアウォール設定で接続元IPが許可されているか")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

