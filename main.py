from flask import Flask, request, render_template, make_response, redirect, url_for
from werkzeug.utils import secure_filename
import json
import os

app = Flask(__name__, template_folder='pages')

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