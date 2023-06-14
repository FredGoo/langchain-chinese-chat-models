import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
import os
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from urllib.parse import urlparse
from wsgiref.handlers import format_date_time

import websocket
from dotenv import load_dotenv, find_dotenv


class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, gpt_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(gpt_url).netloc
        self.path = urlparse(gpt_url).path
        self.gpt_url = gpt_url

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.gpt_url + '?' + urlencode(v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url


# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws):
    print("### closed ###")


# 收到websocket连接建立的处理
def on_open(ws):
    thread.start_new_thread(run, (ws,))


def run(ws, *args):
    data = json.dumps(gen_params(appid=ws.appid, question=ws.question))
    ws.send(data)


# 收到websocket消息的处理
def on_message(ws, message):
    data = json.loads(message)
    code = data['header']['code']
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    else:
        choices = data["payload"]["choices"]
        status = choices["status"]
        content = choices["text"][0]["content"]
        print(content, end='')
        if status == 2:
            ws.close()


def gen_params(appid, question):
    """
    通过appid和用户的提问来生成请参数
    """
    data = {
        "header": {
            "app_id": appid,
            "uid": "1234"
        },
        "parameter": {
            "chat": {
                "domain": "general",
                "random_threshold": 0.5,
                "max_tokens": 2048,
                "auditing": "default"
            }
        },
        "payload": {
            "message": {
                "text": [
                    {"role": "user", "content": question}
                ]
            }
        }
    }
    return data


def main(appid, api_key, api_secret, gpt_url, question):
    wsParam = Ws_Param(appid, api_key, api_secret, gpt_url)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.appid = appid
    ws.question = question
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


if __name__ == "__main__":
    # read local .env file
    _ = load_dotenv(find_dotenv())

    # 测试时候在此处正确填写相关信息即可运行
    main(appid=os.environ['XFYUN_APP_ID'],
         api_key=os.environ['XFYUN_API_KEY'],
         api_secret=os.environ['XFYUN_API_SECRET'],
         gpt_url="wss://spark-api.xf-yun.com/v1.1/chat",
         question=
         """
            2022年11月4日，计算机系通过线上线下相结合的方式在东主楼10-103会议室召开博士研究生导师交流会。\
            计算机学科学位分委员会主席吴空，计算机系副主任张建、党委副书记李伟出席会议，博士生研究生导师和教学办工作人员等30余人参加会议，会议由张建主持。\n
            请你提取包含“人”(name, position)，“时间”，“事件“，“地点”（location）类型的所有信息，并输出JSON格式
         """
         )
