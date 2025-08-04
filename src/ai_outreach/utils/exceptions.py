"""
自定义异常类
定义应用程序中使用的所有自定义异常
"""

class AIOutreachException(Exception):
    """基础异常类"""
    pass

class ConfigurationError(AIOutreachException):
    """配置错误"""
    pass

class NetworkError(AIOutreachException):
    """网络相关错误"""
    pass

class AudioProcessingError(AIOutreachException):
    """音频处理错误"""
    pass

class FileProcessingError(AIOutreachException):
    """文件处理错误"""
    pass

class TranscriptionError(AIOutreachException):
    """转录错误"""
    pass

class AnalysisError(AIOutreachException):
    """分析错误"""
    pass

class TemplateError(AIOutreachException):
    """模板错误"""
    pass