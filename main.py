from flask import Flask, request, Response, render_template, make_response, redirect, url_for
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, emit
from time import sleep
import json
import os
import cv2
import detection

app = Flask(__name__, template_folder='pages')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


# def gen_frames(rtsp_url):
#     while True:
#         # I think there needs to be a button to stop this
#         try:
#             success, frame = cv2.VideoCapture(rtsp_url).read()
#         except Exception:
#                 continue
#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()
#         return (b'--frame\r\n'
#                 b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @app.route('/video_start')
# def video_start():
    # By returning an image of a frame of frame, it reaches the purpose of watching the video. Multipart / X-Mixed-Replace is a single HTTP request - response mode, if the network is interrupted, it will cause the video stream to terminate, you must reconnect to recover
#    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    return render_template('main.html')

@app.route('/upload_video', methods=['POST'])
def upload_file():
    files = request.files.getlist("file") #  получаем файлы
    print(files)
    if(request.files): # Если получили файлы
        return json.dumps(detection.detect_video_files(files, "./static/results/", 0.3, 0.7, 3))
    else: # Если ничего не получили TODO: (не работает)
        return "Пустой запрос!"
        
@socketio.on("link_socket") # получение ссылки и отправка фото в прямом эфире
def link_socket(link):
    print(link)
    for i in range(3):
        sleep(3)
        emit("receiving_photo", json.dumps(link))
        
@app.route('/user_feedback', methods=['POST']) # принимаем фидбек от пользователя, когда он тыкает на "Верно" или "Ошибка"
def user_feedback():
    feedback = json.loads(request.data)
    print(feedback) # 1 - подтверждено пользователем, 0 - отклонено
    return ""

@app.route('/send_archive', methods=['POST']) # Принимаем код пользователя
def get_archive():
    id = json.loads(request.data)
    print(id, "here")
    return detection.send_archive(id)



if __name__ == "__main__":
    socketio.run(app)