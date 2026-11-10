import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# 从脚本所在目录读取配置，不受终端当前目录影响
load_dotenv(Path(__file__).parent / ".env", encoding="utf-8-sig")

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise RuntimeError("未读取到 DEEPSEEK_API_KEY，请检查 .env 文件")

with OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
    timeout=30.0,
    max_retries=0,
) as client:
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {"role": "user", "content": "请用一句中文说明你能帮助排查后端接口问题。"}
        ],
        max_tokens=256,
        extra_body={"thinking": {"type": "disabled"}},
    )

    print("模型回复：")
    print(response.choices[0].message.content)