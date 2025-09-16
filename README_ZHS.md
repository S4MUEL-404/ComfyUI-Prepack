# ComfyUI-Prepack

**版本: 1.2.0**

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
- **💀Prepack SetPipe** - 设置和存储工作流管道状态
- **💀Prepack GetPipe** - 获取和使用已存储的管道状态

### 逻辑运算
- **💀Prepack Logic Int** - 整数逻辑运算和比较
- **💀Prepack Logic String** - 字符串逻辑运算和操作

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
   git clone https://github.com/S4MUEL/ComfyUI-Prepack.git
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

## 📁 项目结构

```
ComfyUI-Prepack/
├── py/                 # 核心节点实现
│   ├── getpipe.py      # 管道获取
│   ├── setpipe.py      # 管道存储
│   ├── seed.py         # 种子管理
│   ├── loras.py        # LoRA 管理
│   ├── ksampler.py     # 基本采样
│   ├── ksamplerAdvanced.py # 高级采样
│   ├── modelDualCLIP.py    # 双 CLIP 模型
│   ├── modelSingleCLIP.py  # 单 CLIP 模型
│   ├── logicInt.py     # 整数逻辑
│   └── logicString.py  # 字符串逻辑
├── js/                 # JavaScript UI 扩展
│   ├── seed.js         # 种子管理 UI
│   ├── loraText.js     # LoRA 文本集成
│   └── setgetnodes.js  # 管道节点 UI
├── summary_md/         # 文档和总结
├── __init__.py        # 插件初始化
└── requirements.txt   # 最小依赖包
```

## 🤝 贡献

欢迎贡献！请随时提交 Pull Request 或报告问题。

## 📜 许可

本项目为开源项目。请遵守相关许可条款。

---

**作者:** S4MUEL  
**网站:** [s4muel.com](https://s4muel.com)  
**版本:** 1.0.0