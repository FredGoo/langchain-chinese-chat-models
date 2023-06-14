# langchain-chinese-chat-models

为langchain添加chatGLM-130B，星火大模型的chat models

# 智谱的ChatGLM

```python
chat = ChatZhiPu(
    temperature=0.0,
    model_name="chatglm_130b",
    max_tokens=1000,
    zhipuai_api_key=gpt_api_key
)
```

可以参考test/zhipuai_test.py

# 科大讯飞的星火认知大模型

```python
chat = ChatXfyun(
    temperature=0.0,
    max_tokens=1000,
    xfyun_app_id=app_id,
    xfyun_api_key=api_key,
    xfyun_api_secret=api_secret
)
```

只支持流模式，可以参考test/xfyun_test.py
