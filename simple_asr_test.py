#!/usr/bin/env python3
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
    print("\n查询结果:")
    print(desc_resp.to_json_string(indent=2))
    
except Exception as e:
    print(f"错误: {e}")
