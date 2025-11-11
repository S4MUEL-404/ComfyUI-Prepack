# ComfyUI-Prepack

**版本: 1.7.0**

專為 ComfyUI 設計的綜合工作流優化工具包，提供模型管理、採樣控制和工作流強化的核心節點，具備專業級可靠性。

## 🚀 功能特色

### 模型管理
- **💀Prepack Model DualCLIP** - 載入具備雙 CLIP 編碼器的模型
- **💀Prepack Model SingleCLIP** - 載入具備單 CLIP 編碼器的模型
- **💀Prepack Loras** - 套用最多 3 個 LoRA 適配器，整合文本文件功能
- **💀Prepack Loras and MSSD3** - LoRA 管理，支援 MSSD3

### 採樣控制
- **💀Prepack Ksampler** - 增強型 KSampler，具備優化參數
- **💀Prepack Ksampler Advanced** - 進階採樣控制，提供額外選項
- **💀Prepack Seed** - 智慧種子管理，具備隨機生成和歷史追蹤功能

### 工作流管理
- **💀Prepack SetPipe** - 設定和儲存工作流管道狀態（現在包括 LoRA 路徑支援）
- **💀Prepack GetPipe** - 取得和使用已儲存的管道狀態（現在包括 LoRA 路徑輸出）

### 邏輯運算
- **💀Prepack Logic Int** - 整數邏輯運算和比較
- **💀Prepack Logic String** - 字串邏輯運算和操作

### 整數操作
- **💀Prepack Int Combine** - 將最多 4 個整數合併為字串，可選分隔符
- **💀Prepack Int Split** - 使用可選分隔符將字串拆分為最多 4 個整數

### 數學運算
- **💀Prepack Calculator** - 使用變數 a、b、c、d 評估數學表達式。支援自訂公式如 `(a*c)+d/2`。同時輸出整數和浮點數結果

### 類型轉換
- **💀Prepack Number Type Converter** - 在字串、整數和浮點數類型之間進行轉換。接受任一類型並同時輸出全部三種類型

### 文件管理
- **💀Save By File Name** - 智慧文件保存，具備格式保持和自訂命名功能。支援圖片（WebP、JPEG、PNG、GIF）、影片（MP4、AVI）和文本文件，具備自動格式檢測功能

### 工作流工具
- **💀Export Workflow as PNG** - 將完整工作流匯出為 PNG 圖片，可選擇嵌入工作流數據或僅圖片。可透過右鍵點擊畫布選單使用

## 📦 安裝方法

### 方法一：ComfyUI Manager（推薦）
1. 開啟 ComfyUI Manager
2. 搜尋 "Prepack"
3. 點擊安裝
4. 重新啟動 ComfyUI

### 方法二：手動安裝
1. 導航至 ComfyUI 自定義節點目錄：
   ```
   cd ComfyUI/custom_nodes/
   ```
2. 克隆此儲存庫：
   ```
   git clone https://github.com/S4MUEL-404/ComfyUI-Prepack.git
   ```
3. 安裝相依套件（最小需求）：
   ```
   pip install -r ComfyUI-Prepack/requirements.txt
   ```
4. 重新啟動 ComfyUI

## 🔧 相依套件

此套件具備最小相依性，使用 ComfyUI 內建功能：
- **PyTorch** - 核心張量運算（通常已可用）
- **NumPy** - 數值計算（通常已可用）

所有相依套件在標準 ComfyUI 安裝中通常都已可用。

## 📖 使用方法

1. **尋找節點**：所有 Prepack 節點在 ComfyUI 節點瀏覽器中都以 💀 為前綴
2. **分類**：在 "💀Prepack" 分類下查找
3. **專業品質**：所有節點都包含完整的錯誤處理
4. **智慧功能**：進階 UI 控制，搭配 JavaScript 擴展

### 快速入門範例
1. 將任何 Prepack 節點新增到你的工作流程
2. 設定節點參數
3. 連接到你的現有工作流程
4. 以增強的控制執行工作流程

## 🎯 主要特點

- ✅ **工作流優化** - 簡化的模型和採樣管理
- ✅ **智慧 UI 控制** - 增強型介面，搭配 JavaScript 擴展
- ✅ **LoRA 整合** - 進階 LoRA 管理，支援文本文件
- ✅ **管道管理** - 高效率儲存和取得工作流狀態
- ✅ **種子管理** - 智慧種子控制，具備歷史追蹤
- ✅ **邏輯運算** - 綜合邏輯和比較工具
- ✅ **文件管理** - 智慧文件保存，具備格式保持和自訂命名功能
- ✅ **工作流匯出** - 將工作流匯出為 PNG，支援嵌入數據

## 🤝 貢獻

歡迎貢獻！請隨時提交 Pull Request 或回報問題。

## 📜 授權

本專案為開源專案。請遵守相關授權條款。

---

**作者:** S4MUEL  
**網站:** [s4muel.com](https://s4muel.com)  
**GitHub:** [https://github.com/S4MUEL-404/ComfyUI-Prepack](https://github.com/S4MUEL-404/ComfyUI-Prepack)  
**版本:** 1.7.0
