import http.server
import socketserver
import threading
import webview
import os
import json

# HTTP 服务器配置
PORT = 6987
DIRECTORY = "trader-ui/dist"

class Api:
  def init(self):
    pass

  def sayHelloTo(self, name):
    response = {'message': 'Hello {0}!'.format(name)}
    return response

  # 获取旧命令回填
  def getLastCommond(self):
    path = './old_command.json'
    if os.path.exists(path):
      with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
      return data
    else:
      return {}

  # 获取配置文件
  def getConfig(self):
    path = './config.json'
    if os.path.exists(path):
      with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
      return data
    else:
      return {}

  # 写入JSON
  def sendCommand(self, data):
    if isinstance(data, dict):
      # 将 JSON 对象写入文件
      with open('./command.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        
      # 将 JSON 对象写入文件
      with open('./old_command.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

class Handler(http.server.SimpleHTTPRequestHandler):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_http_server():
  with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving Vue3 project at http://localhost:{PORT}")
    httpd.serve_forever()

# 启动 HTTP 服务器线程
http_server_thread = threading.Thread(target=start_http_server, daemon=True)
http_server_thread.start()

def on_closed():
  os._exit(0)

# f'http://localhost:6987',

# 创建一个小窗口并打开 Vue3 项目的网址
window = webview.create_window(
  '下单员',
  f'http://localhost:6987',
  width=620,
  height=540,
  resizable=False,
  js_api=Api()
)

window.events.closed += on_closed

webview.start()

# 保持主线程运行以保持服务器继续运行
http_server_thread.join()
