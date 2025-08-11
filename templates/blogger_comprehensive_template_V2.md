# 军师作战简报：{{ blogger_info.name }}

## 👤 博主档案 (Blogger Dossier)
| 基本信息 | 详情 |
|---|---|
| **博主姓名** | {{ blogger_info.name }} |
| **平台** | {{ blogger_info.platform }} |
| **粉丝数量** | {{ blogger_info.follower_count }} |
| **内容领域** | {{ blogger_info.niche }} |
| **一句话速写** | {{ comprehensive_analysis.blogger_characteristics.style }}的{{ comprehensive_analysis.blogger_characteristics.expertise }}，个性{{ comprehensive_analysis.blogger_characteristics.personality }} |
| **合作状态** | {{ blogger_info.status }} |
| **初步洞察（软性指标）** | {{ comprehensive_analysis.soft_indicator_summary or "未识别" }} |

---

## 🎯 核心洞察与战略建议 (Core Insight & Strategic Recommendation)

**核心洞察:** {{ comprehensive_analysis.core_insight or "洞察生成中..." }}

**方法论映射 (爆款公式视角):**
- **信任之钩:** {{ comprehensive_analysis.methodology_mapping.trust_hook or "未分析" }}
- **共情之锚:** {{ comprehensive_analysis.methodology_mapping.empathy_anchor or "未分析" }}
- **价值图谱:** {{ comprehensive_analysis.methodology_mapping.value_map or "未分析" }}

---

## 🚀 V5.0 单点验证最优破冰脚本 (Optimal Icebreaker Script)
目标：快速验证我们对您核心痛点的新假设

> {{ comprehensive_analysis.optimal_outreach_script or "脚本生成中..." }}

---

<details>
<summary><strong>📊 附件：原始数据与分析详情 (点击展开)</strong></summary>

### 核心主题
{% for topic in comprehensive_analysis.main_topics %}
- {{ topic }}
{% endfor %}

### 受众痛点
{% for pain_point in comprehensive_analysis.pain_points %}
- {{ pain_point }}
{% endfor %}

### 博主金句
{% for sentence in comprehensive_analysis.golden_sentences %}
- "{{ sentence }}"
{% endfor %}

### 视频作品清单
{% for video in video_summaries %}
**{{ loop.index }}. {{ video.title }}**
- ⏱️ 时长: {{ "%.1f"|format(video.duration) }}秒
- 🗣️ 语调特点: {{ video.tone[:50] }}...
{% endfor %}

</details>

---
*📊 报告生成时间: {{ current_time }}* *🔗 数据来源: 博主档案 + {{ total_videos }}个视频综合分析* *🤖 分析引擎: AI外联军师 v3.1*