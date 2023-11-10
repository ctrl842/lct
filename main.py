from flask import Flask, request, Response, render_template, make_response, redirect, url_for
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, emit
import json
import os
import cv2
import detection

app = Flask(__name__, template_folder='pages')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# '''
# def gen_frames():
#     while True:
#         # I think there needs to be a button to stop this
#         rtsp_url = ''
#         try:
#             success, frame = cv2.VideoCapture(rtsp_url).read()
#         except Exception:
#                 continue
#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()
#         yield (b'--frame\r\n'
#                 b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
# '''
 
#@app.route('/video_start')

#def video_start():
    # By returning an image of a frame of frame, it reaches the purpose of watching the video. Multipart / X-Mixed-Replace is a single HTTP request - response mode, if the network is interrupted, it will cause the video stream to terminate, you must reconnect to recover
#    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


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
        if(request.files): # Если получили файлы
            return json.dumps(detection.detect_video_files(files, "./static/results/", 0.3, 0.7, 3))
        elif(link != ""): # Если получили ссылку
            return link
        else: # Если ничего не получили TODO: (не работает)
            return "Пустой запрос!"
        
@app.route('/user_feedback', methods=['GET', 'POST']) # принимаем фидбек от пользователя, когда он тыкает на "Верно" или "Ошибка"
def user_feedback():
    if request.method == 'POST':
        feedback = json.loads(request.data)
        print(feedback) # 1 - подтверждено пользователем, 0 - отклонено
    return ""

       

if __name__ == "__main__":
    app.run(debug=False)