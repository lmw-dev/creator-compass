---
tags: [design, user-flow, ai-outreach]
---


# 设计 - AI外联军师用户流程图 (V2.0 - 混合输入模式)

> [!tip] 核心流程
> 本工具支持“URL”和“本地文件”两种输入模式，将不稳定的“在线抓取”与可靠的“本地分析”相结合，最终统一进入核心AI分析管道，生成策略简报。


```mermaid
graph TD
    subgraph "输入层 (两种模式)"
        A1["用户输入: --url <视频链接>"]
        A2["用户输入: --file <本地文件路径>"]
    end

    A1 --> B{Python脚本启动}
    A2 --> B

    subgraph "数据获取层"
        C1["Fetcher模块 (yt-dlp)<br><i>处理URL，提取音频</i>"]
        C2["File Handler模块<br><i>处理本地文件，提取音频</i>"]
    end
    
    subgraph "核心分析管道"
        D["Transcriber模块<br><i>(腾讯云ASR，音频转文本)</i>"]
        E["Analyzer模块<br><i>(LLM API，文本提炼洞察)</i>"]
        F["Generator模块<br><i>(Jinja2，填充沟通模板)</i>"]
    end

    subgraph "输出层"
        G["组装Markdown报告"]
        H["输出: [博主]-[标题].md 文件"]
    end

    B -- IF url --> C1
    B -- IF file --> C2

    C1 -- 音频数据 --> D
    C2 -- 音频数据 --> D
    
    D -- 纯文本 --> E
    E -- 结构化洞察 --> F
    F -- 格式化文案 --> G
    G --> H

    style A1 fill:#D6EAF8
    style A2 fill:#D6EAF8
    style H fill:#D5F5E3
  ```  
---