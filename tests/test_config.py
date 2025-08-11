"""
配置管理模块测试
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.ai_outreach.utils.config import Config, config

class TestConfig:
    """配置管理测试类"""
    
    def test_config_initialization(self):
        """测试配置初始化"""
        test_config = Config()
        
        # 检查基本属性
        assert hasattr(test_config, 'ROOT_DIR')
        assert isinstance(test_config.ROOT_DIR, Path)
        assert hasattr(test_config, 'TENCENT_REGION')
        assert hasattr(test_config, 'DEFAULT_AI_PROVIDER')
        assert hasattr(test_config, 'DEFAULT_MODEL')
    
    @patch.dict('os.environ', {
        'TENCENT_SECRET_ID': 'test_id',
        'TENCENT_SECRET_KEY': 'test_key',
        'DEEPSEEK_API_KEY': 'test_deepseek_key'
    })
    def test_config_with_env_vars(self):
        """测试环境变量配置"""
        test_config = Config()
        
        assert test_config.TENCENT_SECRET_ID == 'test_id'
        assert test_config.TENCENT_SECRET_KEY == 'test_key'
        assert test_config.DEEPSEEK_API_KEY == 'test_deepseek_key'
    
    def test_validate_missing_keys(self):
        """测试缺少必需密钥的验证"""
        test_config = Config()
        test_config.TENCENT_SECRET_ID = None
        test_config.TENCENT_SECRET_KEY = None
        test_config.DEEPSEEK_API_KEY = None
        
        errors = test_config.validate()
        
        assert len(errors) >= 2  # 至少有腾讯云的两个密钥错误
        assert any('TENCENT_SECRET_ID' in error for error in errors)
        assert any('TENCENT_SECRET_KEY' in error for error in errors)
    
    @patch.dict('os.environ', {
        'TENCENT_SECRET_ID': 'test_id',
        'TENCENT_SECRET_KEY': 'test_key',
        'DEEPSEEK_API_KEY': 'test_deepseek_key'
    })
    def test_validate_with_keys(self):
        """测试有效配置的验证"""
        test_config = Config()
        
        errors = test_config.validate()
        
        assert len(errors) == 0
    
    def test_ensure_directories(self, tmp_path):
        """测试目录创建"""
        test_config = Config()
        test_config.OUTPUT_DIR = tmp_path / 'test_output'
        test_config.TEMP_DIR = tmp_path / 'test_temp'
        
        test_config.ensure_directories()
        
        assert test_config.OUTPUT_DIR.exists()
        assert test_config.TEMP_DIR.exists()
    
    def test_global_config_instance(self):
        """测试全局配置实例"""
        assert config is not None
        assert isinstance(config, Config)