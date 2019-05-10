from flask import Flask, jsonify,request,render_template
from flaskext.mysql import MySQL
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
import time
import json
import time
import datetime

# 他のpcのブラウザでwebsocetを支えるためには必要らしがどこに書くかよくわからない
#class WebSocketHandler(tornado.websocket.WebSocketHandler):  
#  def check_origin(self, origin):  
#    return True 

app = Flask(__name__)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'pi'
app.config['MYSQL_DATABASE_PASSWORD'] = 'pi'
app.config['MYSQL_DATABASE_DB'] = 'sensor'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3306

mysql.init_app(app)

def ExecuteQuery(sql):
  cur = mysql.connect().cursor()
  cur.execute(sql)
  values = cur.fetchall()
  svalue = values[0]
  return svalue
      
@app.route('/')
def index():
  return render_template('index.html')

@app.route('/pipe')
def pipe():
  f = open("setting.json", 'r')
  setting_json = json.load(f)
  if request.environ.get('wsgi.websocket'):
    ws = request.environ['wsgi.websocket']
    while True:
      t = int(time.mktime(datetime.datetime.now().timetuple()))
      svalue = ExecuteQuery('select * from accelerations order by id desc limit 1') 
      acc_values = [{"time" : t, 'y' : str(svalue[0])},{"time" : t, 'y' : str(svalue[1])},{"time" : t, 'y' : str(svalue[2])}]
      svalue = ExecuteQuery('select * from geomagnetics order by id desc limit 1') 
      geo_values = [{"time" : t, 'y' : str(svalue[0])},{"time" : t, 'y' : str(svalue[1])},{"time" : t, 'y' : str(svalue[2])}]
      svalue = ExecuteQuery('select * from airs order by id desc limit 1') 
      air_values = [{"time" : t,"y" : str(svalue[0])}, {"time" : t,"y" : str(svalue[1])}, {"time" : t, "y" : str(svalue[2])}, {"time" : t,"y" : str(svalue[3])}, {"time" : t,"y" : str(svalue[4])}]
      values = json.dumps({'acc' : acc_values,'geo' : geo_values,'air' : air_values})
      ws.send(values)
      time.sleep(setting_json["time-interval"])

if __name__ == '__main__':
  app.debug= True
  server = pywsgi.WSGIServer(("0.0.0.0", 5000), app, handler_class=WebSocketHandler)
  server.serve_forever()
