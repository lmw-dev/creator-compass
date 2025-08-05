# 🎯 AI外联军师 (Creator Compass)

> 一个AI辅助的博主分析工具，支持URL链接和本地文件两种输入模式，快速分析博主视频内容并生成个性化的破冰私信脚本

## 📋 项目概述

**AI外联军师**是一个专为独立开发者设计的内部命令行工具，旨在通过AI技术分析博主视频内容，自动生成个性化的沟通脚本，将手工外联工作升级为体系化、高效率的作战流程。

### 🚀 核心特色

- **🔄 混合输入模式**: 支持`--url`(在线抓取)和`--file`(本地文件)两种输入方式
- **📦 批量处理**: 支持批量处理文件夹中的多个MP4文件，智能去重和进度跟踪
- **🎯 博主综合分析**: 整合博主基础信息和多个视频内容，生成综合分析报告
- **🎵 音频转录**: 通过yt-dlp + 腾讯云ASR绕过硬字幕限制，直接从音频获取文本
- **🤖 AI洞察**: 基于DeepSeek/OpenAI + 可配置Prompt模板分析博主特征
- **📝 脚本生成**: 自动生成两套个性化沟通脚本模板
- **📊 策略简报**: 输出完整的Markdown格式外联策略简报

### 🏗️ 技术架构 (V5.0)

**核心设计**: "混合输入模式"+"可配置化Prompt"策略

```mermaid
graph TD
    A[--url 或 --file] --> B{输入类型判断}
    B --> C[fetcher.py / file_handler.py]
    C --> D[腾讯云ASR转录]
    D --> E[LLM分析 + Prompt模板]
    E --> F[Jinja2生成脚本]
    F --> G[Markdown报告]
```

### 📊 技术栈

| 组件 | 技术选型 | 核心理由 |
|------|----------|----------|
| **主语言** | Python 3.11+ | 强大的文本处理能力和丰富的AI生态 |
| **信息抓取** | yt-dlp | 支持几乎所有主流视频平台，能精准提取音频流 |
| **语音转文字** | 腾讯云ASR | 与现有云服务生态一致，集成顺畅，成本可控 |
| **AI模型** | DeepSeek/OpenAI | 以DeepSeek为首选，OpenAI为备选，兼顾性能与成本 |
| **模板引擎** | Jinja2 | 功能强大，语法简洁，用于动态生成报告和脚本 |
| **命令行解析** | Typer | 基于类型提示自动生成CLI，代码简洁现代，开发体验极佳 |
| **代码规范** | Ruff | 超高速的Linter和Formatter，一体化代码质量管理 |

## 🚀 快速开始

### 环境要求

- Python 3.11+
- 腾讯云ASR API密钥
- DeepSeek/OpenAI API密钥

### 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件，填入你的API密钥
nano .env
```

### 使用方法

#### 单文件分析
```bash
# 方式1: URL链接分析 (B站、YouTube等) - 优先提取字幕
python main.py analyze --url "https://www.bilibili.com/video/BV14e8JzdEgH/?spm_id_from=333.1007.tianma.2-2-5.click&vd_source=976833e5802fbddc07ce1803775b1e06"

# 方式2: 本地文件分析 (推荐用于抖音等复杂平台)
python main.py analyze --file "/path/to/downloaded/video.mp4"

# 详细输出（调试模式）
python main.py analyze --file "video.mp4" --verbose
```

#### 批量处理
```bash
# 批量处理文件夹中的所有MP4文件
python main.py batch /path/to/videos

# 批量处理，启用详细输出
python main.py batch docs/data --verbose

# 限制处理数量（适用于大批量文件）
python main.py batch docs/data --max 10 --verbose
```

#### 博主综合分析
```bash
# 分析博主文件夹（包含基础信息和多个视频）
python main.py blogger-analysis "/path/to/11-博主-穷听 - jjjin0"

# 博主综合分析，启用详细输出
python main.py blogger-analysis "/path/to/博主文件夹" --verbose
```

#### 其他命令
```bash
# 检查配置
python main.py config-check

# 查看帮助
python main.py --help
python main.py batch --help
python main.py blogger-analysis --help
```

#### 输出文件
```text
outputs/
├── [博主名]-[视频标题]-[时间戳].md           # 单视频分析报告
├── 博主综合分析-[博主名]-[时间戳].md          # 博主综合分析报告
└── transcripts/
    └── [博主名]-[视频标题]-[时间戳].txt      # 纯转录文本
```

## 📁 项目结构

```text
creator-compass/
├── main.py                    # 🎯 主流程入口 (Typer CLI)
├── src/                       # 📦 源代码目录
│   └── ai_outreach/           # 核心包
│       ├── __init__.py        # 包初始化文件
│       ├── fetcher.py         # 在线抓取模块 (yt-dlp封装)
│       ├── file_handler.py    # 本地文件处理模块
│       ├── transcriber.py     # ASR转录模块 (腾讯云ASR封装)
│       ├── analyzer.py        # AI分析模块 (LLM API封装)
│       ├── blogger_analyzer.py # 博主综合分析模块
│       ├── generator.py       # 脚本生成模块 (Jinja2封装)
│       └── utils/             # 工具函数目录
│           ├── __init__.py    # 工具包初始化
│           ├── config.py      # 配置管理
│           ├── logger.py      # 日志工具
│           ├── exceptions.py  # 自定义异常
│           └── audio_utils.py # 音频处理工具
├── prompts/                   # 🧠 AI分析Prompt模板目录
│   ├── analyze_blogger_content.txt
│   └── extract_pain_points.txt
├── templates/                 # 📝 沟通脚本模板目录
│   ├── new_blogger_template.md     # 新锐博主破冰脚本
│   ├── known_blogger_template.md   # 旧识博主激活脚本
│   └── blogger_comprehensive_template.md # 博主综合分析报告模板
├── tests/                     # 🧪 测试文件目录
│   ├── test_*.py             # 单元测试和集成测试
│   └── __init__.py
├── outputs/                   # 📊 输出报告目录
│   └── transcripts/           # 📝 转录文本专用目录
├── temp/                      # 🗂️ 临时文件目录
├── docs/                      # 📚 项目文档
│   ├── 项目 - AI外联军师.md
│   ├── 架构 - AI外联军师.md (V5.0)
│   ├── 决策 - AI外联军师技术选型.md
│   └── development/           # 开发文档
├── requirements.txt           # 📋 Python依赖清单
├── .env.example              # ⚙️ 环境变量模板
└── README.md                 # 📖 项目说明文档
```

## 🎯 用户故事

**作为** 独立开发者  
**我希望** 能利用AI工具，快速分析目标博主的视频内容，并自动生成个性化的沟通脚本初稿  
**以便于** 我能以数倍的效率，与潜在的天使用户建立真诚、有效的首次联系

## ✅ 验收标准

- [x] 支持`--url`和`--file`两种输入模式（URL优先字幕提取，本地文件音频处理）
- [x] 能通过URL或本地文件成功提取音频并转录（腾讯云ASR验证通过）
- [x] 能调用LLM基于Prompt模板分析博主风格、痛点、契合点（DeepSeek API验证）
- [x] 能生成两套不重复的个性化沟通脚本（3种风格脚本：专业认可型、价值共鸣型、资源互助型）
- [x] 整个流程能在30秒内完成（实测约18秒完成完整分析）
- [x] 输出完整的Markdown格式策略简报（格式清晰，内容完整）

## 🔧 开发指南

### 代码规范

```bash
# 代码格式化
ruff format .

# 代码检查
ruff check .

# 类型检查
mypy .
```

### 测试

```bash
# 运行测试
pytest tests/

# 测试覆盖率
pytest --cov=. tests/
```

## 📝 更新日志

### 2025-08-05 (v1.2.0)

- 🎯 **博主综合分析**: 全新分析模式，整合博主基础信息和多个视频内容
- 📋 **智能档案解析**: 支持"人物 - 博主名.md"基础信息文件自动解析
- 🤝 **合作评估报告**: 生成包含优势风险评估和个性化开场白的综合报告
- 🔤 **智能命名优化**: 从文件夹路径和文件名智能提取博主名称
- 📊 **多维度分析**: 视频作品清单、内容特征、受众画像全方位分析

### 2025-08-05 (v1.1.0)

- 📦 **批量处理**: 新增批量处理功能，支持一次性处理文件夹中的多个MP4文件
- 🧠 **智能去重**: 自动检测已处理文件，避免重复处理节省时间和API调用
- 📊 **进度追踪**: 实时显示处理进度和详细统计报告
- 📝 **转录保存**: 新增转录文本独立保存功能，输出到专用transcripts目录
- ⚡ **性能优化**: 批量处理支持错误恢复，单文件失败不影响整体任务

### 2025-08-04 (v1.0.0)

- ✅ **项目完成**: 所有核心功能实现并测试通过
- 🏗️ **架构优化**: 重构代码目录，采用`src/ai_outreach/`包结构
- 🎯 **混合输入**: 完美实现URL和本地文件双输入模式
- 📝 **字幕提取**: URL模式优先提取字幕，无字幕时自动回退音频处理
- 🤖 **AI集成**: DeepSeek/OpenAI + 腾讯云ASR完整工作流验证
- 📊 **性能优化**: 18秒完成完整分析流程，音频自动压缩处理
- 🧪 **完整测试**: 单元测试、集成测试、端到端验证全部通过

## 🤝 贡献指南

本项目目前处于内部MVP阶段，暂不接受外部贡献。

## 📄 许可证

本项目仅供内部使用，版权所有。

## 🔗 相关链接

- **代码仓库**: [GitHub](https://github.com/lmw-dev/creator-compass.git)
- **项目文档**: [docs/](./docs/)
- **Linear Issue**: TOM-246

---

**🚀 让外联工作从手工作业升级为体系化作战！**
