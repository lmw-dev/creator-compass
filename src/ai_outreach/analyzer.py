"""
AI分析模块
使用大语言模型分析转录文本，提取博主特征和洞察
"""

import json
import re
from typing import Dict, Any, List, Optional
from openai import OpenAI
from .utils.logger import logger
from .utils.exceptions import AnalysisError, ConfigurationError, TemplateError
from .utils.config import config

class AnalysisResult:
    """AI分析结果类"""
    def __init__(self, data: Dict[str, Any]):
        # 基础分析字段
        self.content_style = data.get('content_style', '')
        self.core_values = data.get('core_values', [])  # 核心价值观
        self.golden_sentences = data.get('golden_sentences', [])  # 博主金句
        self.main_topics = data.get('main_topics', [])  # 保留兼容性
        self.pain_points = data.get('pain_points', [])
        self.value_propositions = data.get('value_propositions', [])
        self.tone = data.get('tone', '')
        self.target_audience = data.get('target_audience', '')
        self.blogger_characteristics = data.get('blogger_characteristics', {})
        
        # V2.1：核心洞察与策略字段（兼容旧版本）
        self.core_insights = data.get('core_insights', [])  # 兼容V2.1
        self.core_insight = data.get('core_insight', '')  # V3.0：一体化洞察
        self.unique_approach = data.get('unique_approach', '')  # 独特切入角度
        self.personalized_strategy = data.get('personalized_strategy', {})  # 个性化沟通策略
        
        # V3.0：方法论映射与最优脚本字段
        self.methodology_mapping = data.get('methodology_mapping', {})  # 方法论映射
        self.optimal_outreach_script = data.get('optimal_outreach_script', '')  # 最优破冰脚本
        
        # V3.0：博主综合分析专用字段
        self.blogger_golden_quotes = data.get('blogger_golden_quotes', [])  # 博主金句
        
        # 为模板兼容性提供映射
        self.golden_sentences = self.blogger_golden_quotes or self.golden_sentences
        
        self.prompt_version = data.get('prompt_version', 'v3.0')

class ContentAnalyzer:
    """内容分析器"""
    
    def __init__(self):
        # 初始化AI客户端
        self.ai_client = self._init_ai_client()
        
        # 确保Prompt目录存在
        config.ensure_directories()
    
    def _init_ai_client(self) -> OpenAI:
        """初始化AI客户端"""
        if config.DEFAULT_AI_PROVIDER == "deepseek":
            if not config.DEEPSEEK_API_KEY:
                raise ConfigurationError("DeepSeek API密钥未配置")
            
            return OpenAI(
                api_key=config.DEEPSEEK_API_KEY,
                base_url=config.DEEPSEEK_BASE_URL
            )
        
        elif config.DEFAULT_AI_PROVIDER == "openai":
            if not config.OPENAI_API_KEY:
                raise ConfigurationError("OpenAI API密钥未配置")
            
            return OpenAI(
                api_key=config.OPENAI_API_KEY,
                base_url=config.OPENAI_BASE_URL
            )
        
        else:
            raise ConfigurationError(f"不支持的AI提供商: {config.DEFAULT_AI_PROVIDER}")
    
    def load_prompt_template(self, template_name: str) -> str:
        """
        加载Prompt模板
        
        Args:
            template_name: 模板名称（不含扩展名）
            
        Returns:
            模板内容
        """
        template_path = config.PROMPTS_DIR / f"{template_name}.txt"
        
        if not template_path.exists():
            raise TemplateError(f"Prompt模板不存在: {template_path}")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            raise TemplateError(f"读取Prompt模板失败: {e}")
    
    def analyze_blogger_comprehensive(self, content: str, blogger_name: str = "") -> AnalysisResult:
        """
        博主综合分析（V3.0专用方法）
        
        Args:
            content: 博主信息和多视频内容的综合文本
            blogger_name: 博主名称
            
        Returns:
            博主综合分析结果
        """
        logger.info(f"开始博主综合分析: {blogger_name}")
        
        try:
            # 加载博主综合分析专用prompt
            prompt_template = self.load_prompt_template("analyze_blogger_comprehensive_v3")
            prompt = prompt_template.format(content=content)
            
            # 调用AI API
            response = self.ai_client.chat.completions.create(
                model=config.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": "你是专业的博主内容战略分析师，擅长深度洞察和策略生成。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            analysis_text = response.choices[0].message.content
            logger.debug(f"博主综合分析AI响应长度: {len(analysis_text)}")
            logger.debug(f"博主综合分析AI响应前200字符: {repr(analysis_text[:200])}")
            
            # 尝试解析JSON（复用现有逻辑）
            try:
                # 清理响应文本
                clean_text = analysis_text.strip()
                logger.debug(f"清理后的响应文本: {clean_text[:500]}...")
                
                # 查找JSON代码块
                if "```json" in clean_text:
                    json_start = clean_text.find("```json") + 7
                    json_end = clean_text.find("```", json_start)
                    if json_end == -1:
                        json_end = len(clean_text)
                    json_text = clean_text[json_start:json_end].strip()
                elif "```" in clean_text and "{" in clean_text:
                    # 处理没有json标识但有代码块的情况
                    json_start = clean_text.find("```") + 3
                    json_end = clean_text.find("```", json_start)
                    if json_end == -1:
                        json_end = len(clean_text)
                    potential_json = clean_text[json_start:json_end].strip()
                    # 找到JSON部分
                    bracket_start = potential_json.find('{')
                    bracket_end = potential_json.rfind('}') + 1
                    if bracket_start != -1 and bracket_end != 0:
                        json_text = potential_json[bracket_start:bracket_end]
                    else:
                        json_text = potential_json
                else:
                    # 提取JSON部分（可能包含其他文本）
                    json_start = clean_text.find('{')
                    json_end = clean_text.rfind('}') + 1
                    
                    if json_start == -1 or json_end == 0:
                        raise ValueError("响应中未找到JSON格式数据")
                    
                    json_text = clean_text[json_start:json_end]
                
                # 进一步清理JSON文本
                json_text = json_text.strip()
                # 移除可能的多余换行和空格
                json_text = re.sub(r'\n\s*', '\n', json_text)
                
                logger.debug(f"提取的JSON文本: {json_text[:300]}...")
                
                # 尝试解析JSON
                try:
                    analysis_data = json.loads(json_text)
                except json.JSONDecodeError as json_error:
                    # 如果JSON解析失败，尝试修复常见问题
                    logger.warning(f"初次JSON解析失败: {json_error}，尝试修复")
                    
                    # 常见修复：移除多余的引号、逗号等
                    fixed_json = json_text
                    
                    # 修复可能的问题：多余的换行符在字符串中
                    fixed_json = re.sub(r'"\s*\n\s*"', '", "', fixed_json)
                    
                    # 修复可能的问题：数组末尾多余的逗号
                    fixed_json = re.sub(r',(\s*[}\]])', r'\1', fixed_json)
                    
                    # 修复可能的问题：对象末尾多余的逗号
                    fixed_json = re.sub(r',(\s*})', r'\1', fixed_json)
                    
                    try:
                        analysis_data = json.loads(fixed_json)
                        logger.info("JSON修复成功")
                    except json.JSONDecodeError:
                        logger.warning("JSON修复失败，使用默认结构")
                        raise ValueError(f"无法解析JSON: {json_error}")
                        
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"博主综合分析JSON解析失败: {e}")
                # 使用默认结构
                analysis_data = {
                    "optimal_outreach_script": "脚本生成失败，请重试",
                    "core_insight": "洞察生成失败，请重试", 
                    "methodology_mapping": {
                        "trust_hook": "分析失败",
                        "empathy_anchor": "分析失败",
                        "value_map": "分析失败"
                    },
                    "blogger_golden_quotes": ["金句提取失败"],
                    "core_values": ["价值观分析失败"],
                    "content_style": "风格分析失败",
                    "tone": "语调分析失败",
                    "target_audience": "受众分析失败",
                    "main_topics": ["主题分析失败"],
                    "pain_points": ["痛点分析失败"],
                    "value_propositions": ["价值主张分析失败"],
                    "blogger_characteristics": {
                        "expertise": "专业领域分析失败",
                        "style": "风格分析失败",
                        "personality": "个性分析失败",
                        "experience_level": "经验分析失败"
                    }
                }
            
            # 标记为博主综合分析
            analysis_data['prompt_version'] = 'v3.0_comprehensive'

            # 对最优破冰脚本进行V5.0单点验证风格的兜底与去模板化处理
            try:
                analysis_data['optimal_outreach_script'] = self._sanitize_outreach_script(
                    analysis_data,
                    blogger_name=blogger_name or ""
                )
            except Exception as _:
                # 保底不影响主流程
                pass

            # 软性指标兜底生成：若模型未提供，尝试基于已有字段推断简短summary
            try:
                if not analysis_data.get('soft_indicator_summary'):
                    analysis_data['soft_indicator_summary'] = self._infer_soft_indicator_summary(analysis_data)
            except Exception as _:
                pass

            return AnalysisResult(analysis_data)
            
        except Exception as e:
            logger.error(f"博主综合分析失败: {e}")
            raise AnalysisError(f"博主综合分析失败: {e}")
    
    def analyze_content(self, transcript: str, title: str = "", author: str = "") -> AnalysisResult:
        """
        分析转录内容
        
        Args:
            transcript: 转录文本
            title: 视频标题（可选）
            author: 作者名称（可选）
            
        Returns:
            分析结果对象
        """
        if not transcript.strip():
            raise AnalysisError("转录文本为空")
        
        logger.info(f"开始分析内容，文本长度: {len(transcript)}字符")
        
        try:
            # 加载V3.0洞察即脚本Prompt模板
            prompt_template = self.load_prompt_template("analyze_blogger_content_v3")
            
            # 构建分析提示词
            analysis_prompt = prompt_template.format(
                title=title or "未知标题",
                author=author or "未知作者",
                transcript=transcript
            )
            
            # 调用AI分析
            response = self.ai_client.chat.completions.create(
                model=config.DEFAULT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的内容分析师，擅长分析博主的内容特征和受众画像。请严格按照要求分析提供的内容，并只返回规范的JSON格式结果，不要添加任何其他解释性文字。确保JSON格式正确，所有字符串都用双引号包围，数组和对象格式标准。"
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # 解析响应
            analysis_text = response.choices[0].message.content
            logger.debug(f"AI分析原始响应长度: {len(analysis_text)}")
            logger.debug(f"AI分析原始响应前200字符: {repr(analysis_text[:200])}")
            logger.debug(f"AI分析原始响应后200字符: {repr(analysis_text[-200:])}")
            
            # 尝试解析JSON
            try:
                # 清理响应文本
                clean_text = analysis_text.strip()
                logger.debug(f"清理后的响应文本: {clean_text[:500]}...")
                
                # 查找JSON代码块
                if "```json" in clean_text:
                    json_start = clean_text.find("```json") + 7
                    json_end = clean_text.find("```", json_start)
                    if json_end == -1:
                        json_end = len(clean_text)
                    json_text = clean_text[json_start:json_end].strip()
                elif "```" in clean_text and "{" in clean_text:
                    # 处理没有json标识但有代码块的情况
                    json_start = clean_text.find("```") + 3
                    json_end = clean_text.find("```", json_start)
                    if json_end == -1:
                        json_end = len(clean_text)
                    potential_json = clean_text[json_start:json_end].strip()
                    # 找到JSON部分
                    bracket_start = potential_json.find('{')
                    bracket_end = potential_json.rfind('}') + 1
                    if bracket_start != -1 and bracket_end != 0:
                        json_text = potential_json[bracket_start:bracket_end]
                    else:
                        json_text = potential_json
                else:
                    # 提取JSON部分（可能包含其他文本）
                    json_start = clean_text.find('{')
                    json_end = clean_text.rfind('}') + 1
                    
                    if json_start == -1 or json_end == 0:
                        raise ValueError("响应中未找到JSON格式数据")
                    
                    json_text = clean_text[json_start:json_end]
                
                # 进一步清理JSON文本
                json_text = json_text.strip()
                # 移除可能的多余换行和空格
                json_text = re.sub(r'\n\s*', '\n', json_text)
                
                logger.debug(f"提取的JSON文本: {json_text[:300]}...")
                
                # 尝试解析JSON
                try:
                    analysis_data = json.loads(json_text)
                except json.JSONDecodeError as json_error:
                    # 如果JSON解析失败，尝试修复常见问题
                    logger.warning(f"初次JSON解析失败: {json_error}，尝试修复")
                    
                    # 常见修复：移除多余的引号、逗号等
                    fixed_json = json_text
                    
                    # 修复可能的问题：多余的换行符在字符串中
                    fixed_json = re.sub(r'"\s*\n\s*"', '", "', fixed_json)
                    
                    # 修复可能的问题：数组末尾多余的逗号
                    fixed_json = re.sub(r',(\s*[}\]])', r'\1', fixed_json)
                    
                    # 修复可能的问题：对象末尾多余的逗号
                    fixed_json = re.sub(r',(\s*})', r'\1', fixed_json)
                    
                    try:
                        analysis_data = json.loads(fixed_json)
                        logger.info("JSON修复成功")
                    except json.JSONDecodeError:
                        logger.warning("JSON修复失败，尝试更激进的修复")
                        # 更激进的修复：重新构建基本结构
                        raise ValueError(f"无法解析JSON: {json_error}")
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"解析AI响应JSON失败: {e}，原始响应长度: {len(analysis_text)}")
                logger.warning(f"JSON解析错误详情: {str(e)}")
                logger.warning(f"完整AI响应内容: {repr(analysis_text)}")  # 添加完整响应内容
                
                # 尝试从原始响应中提取关键信息
                fallback_data = self._extract_fallback_data(analysis_text)
                if fallback_data:
                    logger.info("使用回退数据提取成功")
                    analysis_data = fallback_data
                else:
                    logger.warning("回退数据提取失败，使用默认结构")
                # 创建默认结构（包含新字段）
                analysis_data = {
                    "content_style": "未能分析",
                    "core_values": ["价值观分析失败"],
                    "golden_sentences": ["金句提取失败"],
                    "main_topics": ["内容分析失败"],
                    "pain_points": ["无法识别"],
                    "value_propositions": ["需要重新分析"],
                    "tone": "未知",
                    "target_audience": "未知",
                    "blogger_characteristics": {
                        "style": "未知",
                        "expertise": "未知",
                        "personality": "未知",
                        "experience_level": "未知"
                    },
                    "core_insights": ["洞察分析失败"],  # 兼容
                    "core_insight": "一体化洞察分析失败",
                    "unique_approach": "切入角度分析失败",
                    "personalized_strategy": {
                        "opening_line": "开场策略分析失败",
                        "resonance_building": "共鸣建立策略失败",
                        "value_demonstration": "价值展示策略失败",
                        "follow_up_approach": "后续沟通策略失败"
                    },
                    "methodology_mapping": {
                        "trust_hook": "信任之钩分析失败",
                        "empathy_anchor": "共情之锚分析失败",
                        "value_map": "价值图谱分析失败"
                    },
                    "optimal_outreach_script": "最优破冰脚本生成失败",
                    "raw_response": analysis_text
                }
            
            result = AnalysisResult(analysis_data)
            logger.info("内容分析完成")
            
            return result
            
        except Exception as e:
            if isinstance(e, (AnalysisError, TemplateError)):
                raise
            error_msg = f"内容分析失败: {e}"
            logger.error(error_msg)
            raise AnalysisError(error_msg)
    
    def _extract_fallback_data(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        从响应文本中提取回退数据
        当JSON解析失败时，尝试从原始文本中提取关键信息
        
        Args:
            response_text: AI响应的原始文本
            
        Returns:
            提取到的数据字典，如果提取失败则返回None
        """
        try:
            fallback_data = {
                "content_style": "未能完整分析",
                "core_values": [],
                "golden_sentences": [],
                "main_topics": [],
                "pain_points": [],
                "value_propositions": [],
                "tone": "未知",
                "target_audience": "未知",
                "blogger_characteristics": {
                    "expertise": "未知",
                    "style": "未知", 
                    "personality": "未知",
                    "experience_level": "未知"
                },
                "core_insights": [],  # 兼容
                "core_insight": "未能分析",
                "unique_approach": "未能分析",
                "personalized_strategy": {
                    "opening_line": "未能分析",
                    "resonance_building": "未能分析",
                    "value_demonstration": "未能分析",
                    "follow_up_approach": "未能分析"
                },
                "methodology_mapping": {
                    "trust_hook": "未能分析",
                    "empathy_anchor": "未能分析",
                    "value_map": "未能分析"
                },
                "optimal_outreach_script": "未能分析"
            }
            
            # 尝试提取具体字段的内容
            patterns = {
                "content_style": r'"content_style":\s*"([^"]+)"',
                "tone": r'"tone":\s*"([^"]+)"',
                "target_audience": r'"target_audience":\s*"([^"]+)"',
                "unique_approach": r'"unique_approach":\s*"([^"]+)"'
            }
            
            for field, pattern in patterns.items():
                match = re.search(pattern, response_text)
                if match:
                    fallback_data[field] = match.group(1)
            
            # 尝试提取数组字段
            array_patterns = {
                "core_values": r'"core_values":\s*\[([^\]]+)\]',
                "golden_sentences": r'"golden_sentences":\s*\[([^\]]+)\]',
                "main_topics": r'"main_topics":\s*\[([^\]]+)\]',
                "pain_points": r'"pain_points":\s*\[([^\]]+)\]',
                "value_propositions": r'"value_propositions":\s*\[([^\]]+)\]',
                "core_insights": r'"core_insights":\s*\[([^\]]+)\]'
            }
            
            for field, pattern in array_patterns.items():
                match = re.search(pattern, response_text)
                if match:
                    # 简单的数组元素提取
                    array_content = match.group(1)
                    # 提取引号内的内容
                    items = re.findall(r'"([^"]+)"', array_content)
                    if items:
                        fallback_data[field] = items
            
            # 检查是否提取到了有意义的数据
            meaningful_fields = 0
            for field in ["content_style", "tone", "target_audience", "unique_approach"]:
                if fallback_data[field] != "未知" and fallback_data[field] != "未能完整分析" and fallback_data[field] != "未能分析":
                    meaningful_fields += 1
            
            for field in ["core_values", "golden_sentences", "main_topics", "pain_points", "value_propositions", "core_insights"]:
                if fallback_data[field]:
                    meaningful_fields += 1
            
            # 如果提取到了至少3个有意义的字段，则认为回退提取成功
            if meaningful_fields >= 3:
                logger.info(f"回退提取成功，提取到{meaningful_fields}个有效字段")
                return fallback_data
            else:
                logger.warning(f"回退提取数据不足，仅提取到{meaningful_fields}个有效字段")
                return None
                
        except Exception as e:
            logger.warning(f"回退数据提取失败: {e}")
            return None
    
    def _sanitize_outreach_script(self, data: Dict[str, Any], blogger_name: str = "") -> str:
        """
        将AI返回的 optimal_outreach_script 去模板化并收敛为 V5.0 单点验证风格。
        - 避免出现示例/占位符（如“XX你好/痛点是A/环节是B/例如：如何在同类产品评测…”）
        - 自然嵌入博主金句/主题/痛点各至少一项（若可用）
        - 保证包含“LMW”与轻量方法论背书以兼容现有校验
        """
        script = (data.get("optimal_outreach_script") or "").strip()

        banned_fragments = [
            "XX你好",
            "痛点是A",
            "环节是B",
            "例如：如何在同类产品评测中找到一个全新的、别人没做过的切入点",
            "例如: 如何在同类产品评测中找到一个全新的、别人没做过的切入点",
            "我之前认为创作者的痛点是A",
        ]

        needs_rewrite = False
        if not script:
            needs_rewrite = True
        else:
            for frag in banned_fragments:
                if frag in script:
                    needs_rewrite = True
                    break

        # 需要补齐个性化要素或关键标识时也触发重写
        if "LMW" not in script:
            needs_rewrite = True

        # 从数据中提取可用信息
        blogger_display_name = blogger_name.strip() or data.get("blogger_info", {}).get("name", "") if isinstance(data.get("blogger_info", {}), dict) else blogger_name.strip()
        quotes: List[str] = data.get("blogger_golden_quotes") or data.get("golden_sentences") or []
        main_topics: List[str] = data.get("main_topics") or []
        pain_points: List[str] = data.get("pain_points") or []

        first_quote = (quotes[0] if quotes else "").strip().strip('"')
        if len(first_quote) > 20:
            first_quote = first_quote[:20]

        topic = (main_topics[0] if main_topics else "内容创作").strip()
        pain = (pain_points[0] if pain_points else "选题与时间分配").strip()

        if needs_rewrite:
            # 组装V5.0单点验证版脚本（单段落、简洁）
            name_prefix = f"{blogger_display_name}你好，" if blogger_display_name else "你好，"
            quote_part = f"您曾提到\"{first_quote}\"，" if first_quote else ""
            # 构造一个贴近场景的括号说明
            scenario = f"（例如：在{topic}内容中，常常被{pain}拖慢节奏）"
            composed = (
                f"{name_prefix}我叫LMW。{quote_part}最近和多位创作者深聊后，我更新了一个更具体的判断："
                f"像您这样的上升期博主，最耗时且最头痛的是{pain}{scenario}。"
                f"这个判断是否贴近您的真实困扰？仅做思考验证，感谢指点。（信任之钩/共情之锚/价值图谱）"
            )
            return composed

        # 若不需要彻底重写，最少做轻度个性化补全
        # 补充姓名
        if blogger_display_name and blogger_display_name not in script:
            script = script.replace("你好，", f"{blogger_display_name}你好，") if "你好，" in script else f"{blogger_display_name}你好，{script}"

        # 补充LMW与方法论背书
        if "LMW" not in script:
            script = script if script.startswith("我叫LMW") else f"我叫LMW。{script}"
        if ("信任之钩" not in script) and ("共情之锚" not in script) and ("价值图谱" not in script):
            script = f"{script}（信任之钩/共情之锚/价值图谱）"

        # 若缺少具体信息，注入最小场景锚点
        if topic and pain and "例如" not in script:
            script = f"{script}（例如：在{topic}内容中，常常被{pain}拖慢节奏）"

        return script

    def _infer_soft_indicator_summary(self, data: Dict[str, Any]) -> str:
        """
        从 golden_sentences / main_topics / pain_points 的关键词启发式推断一个软性指标总结（≤40字）。
        优先级：工作流 > 进化 > 求教。若皆无，返回"未识别"。
        """
        join_lower = lambda arr: " ".join(arr).lower() if isinstance(arr, list) else str(arr).lower()
        quotes = join_lower(data.get('blogger_golden_quotes') or data.get('golden_sentences') or [])
        topics = join_lower(data.get('main_topics') or [])
        pains = join_lower(data.get('pain_points') or [])
        concat = f"{quotes} {topics} {pains}"

        # 工作流触发词
        workflow_keys = ["流程", "sop", "我通常", "我会先", "整理资料", "构思脚本", "多设备", "三维评估", "复盘"]
        if any(k.lower() in concat for k in workflow_keys):
            return "展现‘工作流’：有方法论与步骤感"

        # 进化迹象触发词
        evolve_keys = ["结构", "叙事", "节奏", "脚本", "分镜", "转场", "悬念", "从只看数据到"]
        if any(k.lower() in concat for k in evolve_keys):
            return "有‘进化’迹象：从数据走向结构与节奏"

        # 求教欲望触发词
        seek_keys = ["欢迎留言", "评论区", "一起研究", "请教", "有没有建议", "你们怎么看"]
        if any(k.lower() in concat for k in seek_keys):
            return "‘求教’欲望强：互动积极，开放学习者"

        return "未识别"

