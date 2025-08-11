"""
AI分析模块测试
"""

import pytest
from unittest.mock import patch, MagicMock
from src.ai_outreach.analyzer import ContentAnalyzer, AnalysisResult
from src.ai_outreach.utils.exceptions import AnalysisError, ConfigurationError

class TestAnalysisResult:
    """分析结果测试类"""
    
    def test_analysis_result_initialization(self):
        """测试分析结果初始化"""
        test_data = {
            'content_style': 'test_style',
            'main_topics': ['topic1', 'topic2'],
            'pain_points': ['pain1'],
            'value_propositions': ['value1'],
            'tone': 'test_tone',
            'target_audience': 'test_audience',
            'blogger_characteristics': {'expertise': 'test'}
        }
        
        result = AnalysisResult(test_data)
        
        assert result.content_style == 'test_style'
        assert result.main_topics == ['topic1', 'topic2']
        assert result.pain_points == ['pain1']
        assert result.tone == 'test_tone'

class TestContentAnalyzer:
    """内容分析器测试类"""
    
    @patch('src.ai_outreach.analyzer.config')
    def test_analyzer_initialization_deepseek(self, mock_config):
        """测试DeepSeek分析器初始化"""
        mock_config.DEFAULT_AI_PROVIDER = 'deepseek'
        mock_config.DEEPSEEK_API_KEY = 'test_key'
        mock_config.DEEPSEEK_BASE_URL = 'https://api.deepseek.com'
        mock_config.ensure_directories = MagicMock()
        
        analyzer = ContentAnalyzer()
        
        assert analyzer.ai_client is not None
    
    @patch('src.ai_outreach.analyzer.config')
    def test_analyzer_initialization_missing_key(self, mock_config):
        """测试缺少API密钥的初始化"""
        mock_config.DEFAULT_AI_PROVIDER = 'deepseek'
        mock_config.DEEPSEEK_API_KEY = None
        mock_config.ensure_directories = MagicMock()
        
        with pytest.raises(ConfigurationError):
            ContentAnalyzer()
    
    @patch('src.ai_outreach.analyzer.config')
    @patch('pathlib.Path.exists')
    @patch('builtins.open')
    def test_load_prompt_template_success(self, mock_open, mock_exists, mock_config):
        """测试成功加载Prompt模板"""
        mock_config.PROMPTS_DIR = MagicMock()
        mock_config.PROMPTS_DIR.__truediv__ = MagicMock(return_value=MagicMock())
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = 'test template content'
        mock_config.DEFAULT_AI_PROVIDER = 'deepseek'
        mock_config.DEEPSEEK_API_KEY = 'test_key'
        mock_config.ensure_directories = MagicMock()
        
        analyzer = ContentAnalyzer()
        result = analyzer.load_prompt_template('test_template')
        
        assert result == 'test template content'
    
    def test_analyze_content_empty_transcript(self):
        """测试空转录文本分析"""
        with patch('src.ai_outreach.analyzer.config') as mock_config:
            mock_config.DEFAULT_AI_PROVIDER = 'deepseek'
            mock_config.DEEPSEEK_API_KEY = 'test_key'
            mock_config.ensure_directories = MagicMock()
            
            analyzer = ContentAnalyzer()
            
            with pytest.raises(AnalysisError, match="转录文本为空"):
                analyzer.analyze_content("")
    
    @patch('src.ai_outreach.analyzer.config')
    def test_analyze_content_with_valid_response(self, mock_config):
        """测试有效响应的内容分析"""
        # Mock配置
        mock_config.DEFAULT_AI_PROVIDER = 'deepseek'
        mock_config.DEEPSEEK_API_KEY = 'test_key'
        mock_config.DEFAULT_MODEL = 'deepseek-chat'
        mock_config.ensure_directories = MagicMock()
        
        # Mock AI客户端响应
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''```json
        {
            "content_style": "测试风格",
            "main_topics": ["测试话题"],
            "pain_points": ["测试痛点"],
            "value_propositions": ["测试价值"],
            "tone": "测试语调",
            "target_audience": "测试受众",
            "blogger_characteristics": {"expertise": "测试"}
        }
        ```'''
        
        with patch('src.ai_outreach.analyzer.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            with patch.object(ContentAnalyzer, 'load_prompt_template', return_value='test template {transcript}'):
                analyzer = ContentAnalyzer()
                result = analyzer.analyze_content("test transcript", "test title", "test author")
                
                assert isinstance(result, AnalysisResult)
                assert result.content_style == "测试风格"
                assert result.main_topics == ["测试话题"]