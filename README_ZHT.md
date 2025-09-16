# ComfyUI-Prepack

**版本: 1.2.0**

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
- **💀Prepack SetPipe** - 設定和儲存工作流管道狀態
- **💀Prepack GetPipe** - 取得和使用已儲存的管道狀態

### 邏輯運算
- **💀Prepack Logic Int** - 整數邏輯運算和比較
- **💀Prepack Logic String** - 字串邏輯運算和操作

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
   git clone https://github.com/S4MUEL/ComfyUI-Prepack.git
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

## 📁 專案結構

```
ComfyUI-Prepack/
├── py/                 # 核心節點實作
│   ├── getpipe.py      # 管道取得
│   ├── setpipe.py      # 管道儲存
│   ├── seed.py         # 種子管理
│   ├── loras.py        # LoRA 管理
│   ├── ksampler.py     # 基本採樣
│   ├── ksamplerAdvanced.py # 進階採樣
│   ├── modelDualCLIP.py    # 雙 CLIP 模型
│   ├── modelSingleCLIP.py  # 單 CLIP 模型
│   ├── logicInt.py     # 整數邏輯
│   └── logicString.py  # 字串邏輯
├── js/                 # JavaScript UI 擴展
│   ├── seed.js         # 種子管理 UI
│   ├── loraText.js     # LoRA 文本整合
│   └── setgetnodes.js  # 管道節點 UI
├── summary_md/         # 文件和總結
├── __init__.py        # 外掛程式初始化
└── requirements.txt   # 最小相依套件
```

## 🤝 貢獻

歡迎貢獻！請隨時提交 Pull Request 或回報問題。

## 📜 授權

本專案為開源專案。請遵守相關授權條款。

---

**作者:** S4MUEL  
**網站:** [s4muel.com](https://s4muel.com)  
**版本:** 1.2.0