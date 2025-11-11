# ComfyUI-Prepack

**版本: 1.7.0**

专为 ComfyUI 设计的综合工作流优化工具包，提供模型管理、采样控制和工作流增强的核心节点，具备专业级可靠性。

## 🚀 功能特色

### 模型管理
- **💀Prepack Model DualCLIP** - 加载具备双 CLIP 编码器的模型
- **💀Prepack Model SingleCLIP** - 加载具备单 CLIP 编码器的模型
- **💀Prepack Loras** - 应用最多 3 个 LoRA 适配器，集成文本文档功能
- **💀Prepack Loras and MSSD3** - LoRA 管理，支持 MSSD3

### 采样控制
- **💀Prepack Ksampler** - 增强型 KSampler，具备优化参数
- **💀Prepack Ksampler Advanced** - 高级采样控制，提供额外选项
- **💀Prepack Seed** - 智能种子管理，具备随机生成和历史跟踪功能

### 工作流管理
- **💀Prepack SetPipe** - 设置和存储工作流管道状态（现在包括 LoRA 路径支持）
- **💀Prepack GetPipe** - 获取和使用已存储的管道状态（现在包括 LoRA 路径输出）

### 逻辑运算
- **💀Prepack Logic Int** - 整数逻辑运算和比较
- **💀Prepack Logic String** - 字符串逻辑运算和操作

### 整数操作
- **💀Prepack Int Combine** - 将最多 4 个整数合并为字符串，可选分隔符
- **💀Prepack Int Split** - 使用可选分隔符将字符串拆分为最多 4 个整数

### 数学运算
- **💀Prepack Calculator** - 使用变量 a、b、c、d 评估数学表达式。支持自定义公式如 `(a*c)+d/2`。同时输出整数和浮点数结果

### 类型转换
- **💀Prepack Number Type Converter** - 在字符串、整数和浮点数类型之间进行转换。接受任一类型并同时输出全部三种类型

### 文件管理
- **💀Save By File Name** - 智能文件保存，具备格式保持和自定义命名功能。支持图片（WebP、JPEG、PNG、GIF）、视频（MP4、AVI）和文本文件，具备自动格式检测功能

### 工作流工具
- **💀Export Workflow as PNG** - 将完整工作流导出为 PNG 图片，可选择嵌入工作流数据或仅图片。可通过右键点击画布菜单使用

## 📦 安装方法

### 方法一：ComfyUI Manager（推荐）
1. 打开 ComfyUI Manager
2. 搜索 "Prepack"
3. 点击安装
4. 重新启动 ComfyUI

### 方法二：手动安装
1. 导航至 ComfyUI 自定义节点目录：
   ```
   cd ComfyUI/custom_nodes/
   ```
2. 克隆此仓库：
   ```
   git clone https://github.com/S4MUEL-404/ComfyUI-Prepack.git
   ```
3. 安装依赖包（最小需求）：
   ```
   pip install -r ComfyUI-Prepack/requirements.txt
   ```
4. 重新启动 ComfyUI

## 🔧 依赖包

此包具备最小依赖性，使用 ComfyUI 内建功能：
- **PyTorch** - 核心张量运算（通常已可用）
- **NumPy** - 数值计算（通常已可用）

所有依赖包在标准 ComfyUI 安装中通常都已可用。

## 📖 使用方法

1. **查找节点**：所有 Prepack 节点在 ComfyUI 节点浏览器中都以 💀 为前缀
2. **分类**：在 "💀Prepack" 分类下查找
3. **专业品质**：所有节点都包含完整的错误处理
4. **智能功能**：高级 UI 控制，搭配 JavaScript 扩展

### 快速入门示例
1. 将任何 Prepack 节点添加到你的工作流
2. 设置节点参数
3. 连接到你的现有工作流
4. 以增强的控制执行工作流

## 🎯 主要特点

- ✅ **工作流优化** - 简化的模型和采样管理
- ✅ **智能 UI 控制** - 增强型界面，搭配 JavaScript 扩展
- ✅ **LoRA 集成** - 高级 LoRA 管理，支持文本文档
- ✅ **管道管理** - 高效存储和获取工作流状态
- ✅ **种子管理** - 智能种子控制，具备历史跟踪
- ✅ **逻辑运算** - 综合逻辑和比较工具
- ✅ **文件管理** - 智能文件保存，具备格式保持和自定义命名功能
- ✅ **工作流导出** - 将工作流导出为 PNG，支持嵌入数据

## 🤝 贡献

欢迎贡献！请随时提交 Pull Request 或报告问题。

## 📜 许可

本项目为开源项目。请遵守相关许可条款。

---

**作者:** S4MUEL  
**网站:** [s4muel.com](https://s4muel.com)  
**GitHub:** [https://github.com/S4MUEL-404/ComfyUI-Prepack](https://github.com/S4MUEL-404/ComfyUI-Prepack)  
**版本:** 1.7.0
