import os

from dotenv import load_dotenv, find_dotenv
from langchain_c.chat_models import ChatZhiPu
from langchain.prompts import ChatPromptTemplate

# read local .env file
_ = load_dotenv(find_dotenv())
gpt_api_key = os.environ['ZHIPUAI_API_KEY']

chat = ChatZhiPu(
    temperature=0.0,
    model_name="chatglm_130b",
    max_tokens=1000,
    zhipuai_api_key=gpt_api_key
)

# Prompt 编写
review_template = """\
从以下的文本提取信息:

gift: is this a gift for someone？if yes set True，or False
delivery_days: 花了几天收到了礼物？输出一个数字，如果没有这个信息，输出-1
price_value: 获取这个物品的价格或者价值，如果有多个，用逗号分隔组成一个python数组
cpu: discribe the cpu model
type: discribe the type of product

用以下的键值来格式化信息并输出一个JSON:
gift
delivery_days
price_value
cpu
type

文本: {text}
"""

# 创建 ChatPromptTemplate
prompt_template = ChatPromptTemplate.from_template(review_template)

# 用户的商品评价
customer_review = """
苹果垃圾桶工作站
"""

messages = prompt_template.format_messages(text=customer_review)

# 请求
response = chat(messages)
print(response.content)

