#!/usr/bin/env python3
"""
腾讯云ASR测试Demo
参考官方文档: https://cloud.tencent.com/document/product/1093/84291
"""

import os
import json
import base64
import time
from pathlib import Path

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.asr.v20190614 import asr_client, models
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

# 从环境变量读取配置
from dotenv import load_dotenv
load_dotenv()

def test_short_audio_recognition(audio_file_path: str):
    """
    测试一句话识别（≤60秒）
    """
    print(f"=== 测试一句话识别 ===")
    print(f"音频文件: {audio_file_path}")
    
    try:
        # 检查文件存在
        if not Path(audio_file_path).exists():
            print(f"❌ 音频文件不存在: {audio_file_path}")
            return
        
        # 读取音频文件
        with open(audio_file_path, 'rb') as f:
            audio_data = f.read()
        
        file_size = len(audio_data)
        print(f"文件大小: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
        
        if file_size > 5 * 1024 * 1024:
            print("❌ 文件超过5MB限制")
            return
        
        # 初始化认证
        cred = credential.Credential(
            os.getenv("TENCENT_SECRET_ID"), 
            os.getenv("TENCENT_SECRET_KEY")
        )
        
        # 实例化一个http选项
        httpProfile = HttpProfile()
        httpProfile.endpoint = "asr.tencentcloudapi.com"
        
        # 实例化一个client选项
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        
        # 实例化要请求产品的client对象
        client = asr_client.AsrClient(cred, os.getenv("TENCENT_REGION", "ap-guangzhou"), clientProfile)
        
        # 实例化一个请求对象
        req = models.SentenceRecognitionRequest()
        
        # 设置请求参数 - 参考官方文档
        req.ProjectId = 0
        req.SubServiceType = 2
        req.EngSerViceType = "16k_zh"
        req.SourceType = 1
        req.VoiceFormat = "wav"  # 明确指定音频格式
        req.UsrAudioKey = f"test_audio_{int(time.time())}"
        
        # Base64编码音频数据
        req.Data = base64.b64encode(audio_data).decode('utf-8')
        req.DataLen = len(audio_data)
        
        print("📤 发送识别请求...")
        
        # 返回的resp是一个SentenceRecognitionResponse的实例
        resp = client.SentenceRecognition(req)
        
        print("✅ 请求成功")
        print(f"识别结果: '{resp.Result}'")
        print(f"结果长度: {len(resp.Result) if resp.Result else 0} 字符")
        
        # 打印完整响应用于调试
        print("\n=== 完整响应信息 ===")
        print(resp.to_json_string(indent=2))
        
    except TencentCloudSDKException as err:
        print(f"❌ 腾讯云SDK异常: {err}")
    except Exception as e:
        print(f"❌ 其他异常: {e}")

def test_long_audio_recognition(audio_file_path: str):
    """
    测试长音频识别（录音文件识别）
    """
    print(f"\n=== 测试长音频识别 ===")
    print(f"音频文件: {audio_file_path}")
    
    try:
        # 检查文件存在
        if not Path(audio_file_path).exists():
            print(f"❌ 音频文件不存在: {audio_file_path}")
            return
        
        # 读取音频文件
        with open(audio_file_path, 'rb') as f:
            audio_data = f.read()
        
        file_size = len(audio_data)
        print(f"文件大小: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
        
        if file_size > 5 * 1024 * 1024:
            print("❌ 文件超过5MB限制")
            return
        
        # 初始化认证
        cred = credential.Credential(
            os.getenv("TENCENT_SECRET_ID"), 
            os.getenv("TENCENT_SECRET_KEY")
        )
        
        # 实例化一个http选项
        httpProfile = HttpProfile()
        httpProfile.endpoint = "asr.tencentcloudapi.com"
        
        # 实例化一个client选项
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        
        # 实例化要请求产品的client对象
        client = asr_client.AsrClient(cred, os.getenv("TENCENT_REGION", "ap-guangzhou"), clientProfile)
        
        # 创建录音文件识别任务
        req = models.CreateRecTaskRequest()
        req.EngineModelType = "16k_zh"
        req.ChannelNum = 1
        req.ResTextFormat = 0
        req.SourceType = 1
        
        # Base64编码音频数据
        req.Data = base64.b64encode(audio_data).decode('utf-8')
        req.DataLen = len(audio_data)
        
        print("📤 创建长音频识别任务...")
        
        # 创建任务
        resp = client.CreateRecTask(req)
        task_id = resp.Data.TaskId
        
        print(f"✅ 任务创建成功，任务ID: {task_id}")
        
        # 轮询任务状态
        max_attempts = 60
        attempt = 0
        
        while attempt < max_attempts:
            # 查询任务状态
            desc_req = models.DescribeTaskStatusRequest()
            desc_req.TaskId = task_id
            
            desc_resp = client.DescribeTaskStatus(desc_req)
            status = desc_resp.Data.StatusStr
            
            print(f"📊 任务状态 ({attempt + 1}/{max_attempts}): {status}")
            
            if status == "success":
                print("✅ 识别完成")
                
                # 获取结果
                result_detail = desc_resp.Data.ResultDetail
                print(f"ResultDetail类型: {type(result_detail)}")
                print(f"ResultDetail内容: {result_detail}")
                
                # 解析结果
                full_text = ""
                if result_detail:
                    print(f"ResultDetail长度: {len(result_detail)}")
                    for i, segment in enumerate(result_detail):
                        print(f"分段{i}: {type(segment)} - {segment}")
                        if hasattr(segment, "FinalSentence"):
                            print(f"  FinalSentence: '{segment.FinalSentence}'")
                            full_text += segment.FinalSentence
                        else:
                            print(f"  没有FinalSentence属性")
                
                print(f"\n🎯 最终识别结果: '{full_text}'")
                print(f"结果长度: {len(full_text)} 字符")
                break
                
            elif status == "failed":
                error_msg = getattr(desc_resp.Data, 'ErrorMsg', '未知错误')
                print(f"❌ 识别失败: {error_msg}")
                break
                
            elif status in ["waiting", "doing"]:
                print("⏳ 任务进行中，等待...")
                time.sleep(3)
                attempt += 1
            else:
                print(f"⚠️ 未知状态: {status}")
                time.sleep(3)
                attempt += 1
        
        if attempt >= max_attempts:
            print("❌ 任务超时")
            
    except TencentCloudSDKException as err:
        print(f"❌ 腾讯云SDK异常: {err}")
    except Exception as e:
        print(f"❌ 其他异常: {e}")

def main():
    print("🚀 腾讯云ASR测试Demo")
    print("=" * 50)
    
    # 测试文件路径
    audio_file = "temp/test_audio.wav"
    
    # 检查音频文件
    if not Path(audio_file).exists():
        print(f"❌ 音频文件不存在: {audio_file}")
        print("请先运行 ffmpeg 命令生成测试音频文件")
        return
    
    # 获取音频时长
    import subprocess
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_format', audio_file
        ], capture_output=True, text=True, check=True)
        
        info = json.loads(result.stdout)
        duration = float(info['format']['duration'])
        print(f"🎵 音频时长: {duration:.1f} 秒")
        
        # 根据时长选择识别方式
        if duration <= 60:
            print("📝 使用一句话识别（≤60秒）")
            test_short_audio_recognition(audio_file)
        else:
            print("📝 使用长音频识别（>60秒）")
            test_long_audio_recognition(audio_file)
            
    except Exception as e:
        print(f"⚠️ 无法获取音频时长: {e}")
        print("📝 尝试两种识别方式...")
        
        # 先尝试一句话识别
        test_short_audio_recognition(audio_file)
        
        # 再尝试长音频识别
        test_long_audio_recognition(audio_file)

if __name__ == "__main__":
    main()