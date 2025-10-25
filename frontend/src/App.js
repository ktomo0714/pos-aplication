import React, { useState } from 'react';
import './App.css';
import axios from 'axios';

// APIのベースURL（環境変数から取得、なければデフォルト）
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  // 状態管理
  const [productCode, setProductCode] = useState('');
  const [currentProduct, setCurrentProduct] = useState(null);
  const [cartItems, setCartItems] = useState([]);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // 商品コード読み込み
  const handleSearchProduct = async () => {
    if (!productCode || productCode.length !== 13) {
      setMessage('商品コードは13桁で入力してください');
      return;
    }

    setIsLoading(true);
    setMessage('');

    try {
      const response = await axios.get(`${API_BASE_URL}/api/products/${productCode}`);
      const product = response.data;

      // 商品が見つからない場合（NULL情報）
      if (!product.PRD_ID || !product.NAME || !product.PRICE) {
        setMessage('該当する商品が見つかりませんでした');
        setCurrentProduct(null);
      } else {
        setCurrentProduct(product);
        setMessage(`商品が見つかりました: ${product.NAME}`);
      }
    } catch (error) {
      console.error('商品検索エラー:', error);
      setMessage('商品検索に失敗しました');
      setCurrentProduct(null);
    } finally {
      setIsLoading(false);
    }
  };

  // カートに追加
  const handleAddToCart = () => {
    if (!currentProduct) {
      setMessage('商品を読み込んでください');
      return;
    }

    const cartItem = {
      PRD_ID: currentProduct.PRD_ID,
      PRD_CODE: currentProduct.CODE,
      PRD_NAME: currentProduct.NAME,
      PRD_PRICE: currentProduct.PRICE,
    };

    setCartItems([...cartItems, cartItem]);
    setMessage(`${currentProduct.NAME} をカートに追加しました`);
    
    // 入力フィールドとカレント商品をクリア
    setProductCode('');
    setCurrentProduct(null);
  };

  // 購入処理
  const handlePurchase = async () => {
    if (cartItems.length === 0) {
      setMessage('カートに商品がありません');
      return;
    }

    setIsLoading(true);
    setMessage('');

    try {
      const purchaseData = {
        EMP_CD: '9999999999',
        STORE_CD: '30',
        POS_NO: '90',
        items: cartItems,
      };

      const response = await axios.post(`${API_BASE_URL}/api/purchase`, purchaseData);
      
      if (response.data.success) {
        const totalAmount = response.data.total_amount;
        setMessage(`購入が完了しました！合計金額: ${totalAmount.toLocaleString()}円`);
        
        // カートをクリア
        setCartItems([]);
        
        // ポップアップ表示
        alert(`購入完了！\n合計金額: ${totalAmount.toLocaleString()}円\n取引ID: ${response.data.transaction_id}`);
      } else {
        setMessage('購入処理に失敗しました');
      }
    } catch (error) {
      console.error('購入エラー:', error);
      setMessage('購入処理に失敗しました');
    } finally {
      setIsLoading(false);
    }
  };

  // カートの合計金額を計算
  const getTotalAmount = () => {
    return cartItems.reduce((sum, item) => sum + item.PRD_PRICE, 0);
  };

  // Enterキーで検索
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearchProduct();
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>POSアプリケーション</h1>
      </header>

      <main className="App-main">
        {/* 左側：商品入力エリア */}
        <div className="input-section">
          {/* コード入力エリア */}
          <div className="code-input-area">
            <input
              type="text"
              className="code-input"
              placeholder="商品コード（13桁）"
              value={productCode}
              onChange={(e) => setProductCode(e.target.value)}
              onKeyPress={handleKeyPress}
              maxLength={13}
              disabled={isLoading}
            />
            <button
              className="search-button"
              onClick={handleSearchProduct}
              disabled={isLoading}
            >
              商品コード読み込み
            </button>
          </div>

          {/* 商品情報表示エリア */}
          <div className="product-info">
            <div className="info-row">
              <label>商品名称:</label>
              <div className="info-value">
                {currentProduct?.NAME || '-'}
              </div>
            </div>
            <div className="info-row">
              <label>商品単価:</label>
              <div className="info-value">
                {currentProduct?.PRICE ? `${currentProduct.PRICE.toLocaleString()}円` : '-'}
              </div>
            </div>
          </div>

          {/* 追加ボタン */}
          <button
            className="add-button"
            onClick={handleAddToCart}
            disabled={!currentProduct || isLoading}
          >
            追加
          </button>

          {/* メッセージ表示 */}
          {message && (
            <div className={`message ${message.includes('失敗') ? 'error' : 'success'}`}>
              {message}
            </div>
          )}
        </div>

        {/* 右側：購入リスト */}
        <div className="cart-section">
          <h2>購入リスト</h2>
          <div className="cart-items">
            {cartItems.length === 0 ? (
              <p className="empty-cart">カートは空です</p>
            ) : (
              cartItems.map((item, index) => (
                <div key={index} className="cart-item">
                  <span className="item-name">{item.PRD_NAME}</span>
                  <span className="item-details">
                    x1 {item.PRD_PRICE.toLocaleString()}円
                  </span>
                  <span className="item-subtotal">
                    {item.PRD_PRICE.toLocaleString()}円
                  </span>
                </div>
              ))
            )}
          </div>

          {/* 合計金額 */}
          {cartItems.length > 0 && (
            <div className="cart-total">
              <span>合計:</span>
              <span className="total-amount">{getTotalAmount().toLocaleString()}円</span>
            </div>
          )}

          {/* 購入ボタン */}
          <button
            className="purchase-button"
            onClick={handlePurchase}
            disabled={cartItems.length === 0 || isLoading}
          >
            {isLoading ? '処理中...' : '購入'}
          </button>
        </div>
      </main>
    </div>
  );
}

export default App;

