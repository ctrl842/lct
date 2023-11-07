from flask import Flask, request, Response, render_template, make_response, redirect, url_for
from werkzeug.utils import secure_filename
import json
import os
import cv2

app = Flask(__name__, template_folder='pages')

camera = cv2.VideoCapture('rtsp://rtsp:Rtsp1234@188.170.176.190:8027/Streaming/Channels/101?transportmode=unicast')

def gen_frames():
    while True:
 #   frame frame loop read the data of the camera
        try:
            success, frame = camera.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except:
            print("help me pls")
 
 
@app.route('/video_start')
def video_start():
 # By returning an image of a frame of frame, it reaches the purpose of watching the video. Multipart / X-Mixed-Replace is a single HTTP request - response mode, if the network is interrupted, it will cause the video stream to terminate, you must reconnect to recover
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/uploadajax', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist("file") #  получаем файлы
        link = (request.form.get('link')) # получаем ссылку rtsp
        print(files)
        print(link)
        if(files != []): # Если получили файлы
            return [["15:12:11", "/static/imgs/pic.jpeg"], ["16:19:15", "/static/imgs/avar_42.jpg"]] # возвращаем массив с картинками распознанных случаев и таймингами
        elif(link != ""): # Если получили ссылку
            return link
        else: # Если ничего не получили TODO: (не работает)
            return "Пустой запрос!"
        
@app.route('/user_feedback', methods=['GET', 'POST']) # принимаем фидбек от пользователя, когда он тыкает на "Верно" или "Ошибка"
def user_feedback():
    if request.method == 'POST':
        feedback = request.data
        print(feedback[2]) # 1 - подтверждено пользователем, 0 - отклонено
    return ""
       

if __name__ == "__main__":
    app.run(debug=False)