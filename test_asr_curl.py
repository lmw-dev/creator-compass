#!/usr/bin/env python3
"""
生成腾讯云ASR的curl测试命令
"""

import os
import json
import base64
import hashlib
import hmac
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def generate_curl_command():
    """
    生成腾讯云ASR的curl命令
    参考: https://cloud.tencent.com/document/api/1093/35799
    """
    
    # 配置信息
    secret_id = os.getenv("TENCENT_SECRET_ID")
    secret_key = os.getenv("TENCENT_SECRET_KEY")
    region = os.getenv("TENCENT_REGION", "ap-guangzhou")
    
    print(f"Secret ID: {secret_id}")
    print(f"Region: {region}")
    
    # 读取音频文件
    audio_file = "temp/test_audio.wav"
    if not Path(audio_file).exists():
        print(f"❌ 音频文件不存在: {audio_file}")
        return
    
    with open(audio_file, 'rb') as f:
        audio_data = f.read()
    
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    print(f"音频文件大小: {len(audio_data)} bytes")
    print(f"Base64编码长度: {len(audio_base64)}")
    
    # API参数
    service = "asr"
    host = "asr.tencentcloudapi.com"
    action = "CreateRecTask"
    version = "2019-06-14"
    algorithm = "TC3-HMAC-SHA256"
    timestamp = int(time.time())
    date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
    
    # 请求体
    payload = {
        "EngineModelType": "16k_zh",
        "ChannelNum": 1,
        "ResTextFormat": 0,
        "SourceType": 1,
        "Data": audio_base64,
        "DataLen": len(audio_data)
    }
    
    payload_json = json.dumps(payload, separators=(',', ':'))
    
    # 生成签名
    def sign(key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
    
    def getSignatureKey(key, dateStamp, regionName, serviceName):
        kDate = sign(('TC3' + key).encode('utf-8'), dateStamp)
        kRegion = sign(kDate, regionName)
        kService = sign(kRegion, serviceName)
        kSigning = sign(kService, 'tc3_request')
        return kSigning
    
    # 创建规范请求
    canonical_uri = '/'
    canonical_querystring = ''
    canonical_headers = f'content-type:application/json\nhost:{host}\n'
    signed_headers = 'content-type;host'
    payload_hash = hashlib.sha256(payload_json.encode('utf-8')).hexdigest()
    canonical_request = f'POST\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}'
    
    # 创建待签名字符串
    credential_scope = f'{date}/{region}/{service}/tc3_request'
    string_to_sign = f'{algorithm}\n{timestamp}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()}'
    
    # 计算签名
    signing_key = getSignatureKey(secret_key, date, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    
    # 创建授权头
    authorization = f'{algorithm} Credential={secret_id}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}'
    
    # 生成curl命令
    curl_command = f'''curl -X POST https://{host}/ \\
  -H "Authorization: {authorization}" \\
  -H "Content-Type: application/json" \\
  -H "Host: {host}" \\
  -H "X-TC-Action: {action}" \\
  -H "X-TC-Timestamp: {timestamp}" \\
  -H "X-TC-Version: {version}" \\
  -H "X-TC-Region: {region}" \\
  -d '{payload_json}' \\
  | jq .'''
    
    print("\n=== 生成的curl命令 ===")
    print(curl_command)
    
    # 保存到文件
    with open("curl_test.sh", "w") as f:
        f.write("#!/bin/bash\n")
        f.write(curl_command)
    
    print("\n✅ curl命令已保存到 curl_test.sh")
    print("运行: chmod +x curl_test.sh && ./curl_test.sh")

def generate_simple_curl():
    """
    生成简化的curl命令用于测试
    """
    print("\n=== 简化测试方案 ===")
    
    # 读取音频文件
    audio_file = "temp/test_audio.wav"
    if not Path(audio_file).exists():
        print(f"❌ 音频文件不存在: {audio_file}")
        return
    
    with open(audio_file, 'rb') as f:
        audio_data = f.read()
    
    # 将音频文件保存为base64格式
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    with open("audio_base64.txt", "w") as f:
        f.write(audio_base64)
    
    print(f"音频文件大小: {len(audio_data)} bytes")
    print(f"Base64编码已保存到: audio_base64.txt")
    
    # 创建简单的Python脚本用于直接API调用
    simple_test = '''#!/usr/bin/env python3
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# 读取base64编码的音频
with open("audio_base64.txt", "r") as f:
    audio_base64 = f.read().strip()

print(f"Base64长度: {len(audio_base64)}")

# 使用腾讯云SDK
from tencentcloud.common import credential
from tencentcloud.asr.v20190614 import asr_client, models

try:
    cred = credential.Credential(
        os.getenv("TENCENT_SECRET_ID"), 
        os.getenv("TENCENT_SECRET_KEY")
    )
    
    client = asr_client.AsrClient(cred, "ap-guangzhou")
    
    # 创建请求
    req = models.CreateRecTaskRequest()
    req.EngineModelType = "16k_zh"
    req.ChannelNum = 1
    req.ResTextFormat = 0
    req.SourceType = 1
    req.Data = audio_base64
    req.DataLen = len(audio_base64.encode()) // 4 * 3  # base64解码后的长度
    
    print("发送请求...")
    resp = client.CreateRecTask(req)
    
    print("原始响应:")
    print(resp.to_json_string(indent=2))
    
    task_id = resp.Data.TaskId
    print(f"任务ID: {task_id}")
    
    # 查询结果
    import time
    time.sleep(5)
    
    desc_req = models.DescribeTaskStatusRequest()
    desc_req.TaskId = task_id
    
    desc_resp = client.DescribeTaskStatus(desc_req)
    print("\\n查询结果:")
    print(desc_resp.to_json_string(indent=2))
    
except Exception as e:
    print(f"错误: {e}")
'''
    
    with open("simple_asr_test.py", "w") as f:
        f.write(simple_test)
    
    print("✅ 简化测试脚本已保存到: simple_asr_test.py")
    print("运行: python simple_asr_test.py")

if __name__ == "__main__":
    print("🧪 腾讯云ASR curl测试生成器")
    print("=" * 50)
    
    generate_simple_curl()
    # generate_curl_command()  # 复杂的签名版本，先用简化版本