# WARP.md

這個文件為 WARP (warp.dev) 在這個倉庫中工作時提供指導。

## 專案概述

ComfyUI-Prepack 是一個為 ComfyUI 設計的綜合工作流優化工具包。它提供了一套帶有 💀 前綴的自定義節點，涵蓋模型管理、採樣控制、工作流管理和邏輯運算等核心功能。這個專案的特點是將複雜的 ComfyUI 操作簡化為單個節點，提升工作流效率。

## 核心架構

### 模組結構
- **py/** - Python 後端節點實現，每個檔案對應一個具體的節點功能
- **js/** - JavaScript 前端 UI 擴展，增強使用者界面體驗
- **__init__.py** - 主入口點，定義所有節點映射和分類

### 節點類別
1. **模型管理** - PrepackModelDualCLIP/SingleCLIP (支援多種 CLIP 類型：SDXL、SD3、FLUX、Hunyuan Video)
2. **LoRA 管理** - PrepackLoras/LorasAndMSSD3 (支援最多3個 LoRA 和文本文件整合)
3. **採樣控制** - PrepackKsampler/KsamplerAdvanced (具備完整錯誤處理和調試功能)
4. **工作流管理** - PrepackSetPipe/GetPipe (管道狀態的存儲和檢索)
5. **智能種子** - PrepackSeed (帶有歷史記錄和隨機生成按鈕)
6. **邏輯運算** - PrepackLogicInt/String 和 PrepackIntCombine/Split
7. **文件保存** - PrepackSaveByFileName (支持圖片、視頻、文本的自定義文件名保存)

### JavaScript UI 架構
- **seed.js** - 提供種子歷史追蹤和隨機生成按鈕（最多50條歷史記錄）
- **loraText.js** - LoRA 文本文件整合，支援動態載入 .txt 檔案內容
- **setgetnodes.js** - Set/Get 虛擬節點系統，具備類型適配和顏色管理

## 常用開發命令

### 測試與調試
```bash
# 啟用 Prepack 調試模式
set PREPACK_DEBUG=1

# 查看 ComfyUI 日誌
# ComfyUI 控制台會顯示節點執行和錯誤資訊

# 檢查 LoRA 文本文件 API
# 瀏覽器訪問: http://localhost:8188/prepack/lora-texts/{lora_name}
```

### 安裝與部署
```bash
# 透過 ComfyUI Manager 安裝（推薦）
# 在 ComfyUI Manager 中搜尋 "Prepack" 並安裝

# 手動安裝
cd ComfyUI/custom_nodes/
git clone https://github.com/S4MUEL-404/ComfyUI-Prepack.git
pip install -r ComfyUI-Prepack/requirements.txt
```

## 重要開發模式

### 節點開發模式
- 所有節點都繼承標準 ComfyUI 節點結構
- 使用 `INPUT_TYPES` 定義輸入，`RETURN_TYPES` 定義輸出
- 必須提供完整的 `tooltip` 和錯誤處理
- 節點分類統一使用 `"💀Prepack"`

### JavaScript 擴展模式
- 使用 `app.registerExtension` 註冊前端擴展
- 透過 `beforeRegisterNodeDef` 修改節點行為
- 使用 ComfyUI 標準 API (`api.fetchApi`) 進行後端通信
- 所有 UI 修改都應保持 ComfyUI 的原生風格

### 管道（Pipe）系統
PrepackSetPipe 和 PrepackGetPipe 實現了狀態傳遞機制：
- SetPipe 將多個組件打包為單一管道對象
- GetPipe 解包管道對象為個別組件
- 支援：model, clip, vae, lora_path, lora_text, positive, negative, latent_image, seed, steps, cfg, denoise

### LoRA 整合系統
- 支援最多3個 LoRA 同時載入
- 自動搜尋同名資料夾中的 .txt 檔案
- 提供 HTTP API 端點用於動態載入文本內容
- 安全檢查防止路徑遍歷攻擊

### 文件保存系統
- 多格式支持：圖片 (PNG/JPG/WebP)、視頻 (MP4/AVI/MOV)、文本 (TXT/JSON/CSV)
- 智能文件名處理：支持 {date}、{time}、{timestamp} 佔位符
- 批量處理和防重複機制
- 元數據嵌入和質量控制

## 關鍵技術實現

### 類型適配系統
Set/Get 節點實現動態類型適配：
- 根據連接自動推斷和適配類型
- 支援萬用字元 (*) 類型
- 顏色編碼區分不同資料類型

### 種子管理系統
- 支援64位無符號整數範圍
- JavaScript 擴展提供歷史追蹤（最多50條）
- 自動監控工作流執行中的種子變化

### 錯誤處理模式
所有節點都實現了完整的錯誤處理：
- 輸入驗證和類型檢查
- 資源載入失敗的優雅降級
- 詳細的錯誤訊息和日誌記錄

## 專案規則遵循

- 所有註釋必須使用英文
- 程式碼命名遵循既有規則
- requirements.txt 保持最簡依賴
- summary_md 目錄用於存放總結文件
- 主頁地址固定為 https://github.com/S4MUEL-404/
- 版本資訊和作者署名：S4MUEL (s4muel.com)