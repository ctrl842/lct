from ultralytics import YOLO
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from datetime import timedelta
import os
import cv2
import numpy as np
from unidecode import unidecode
import time
import shutil
import json
import sys

MODEL = YOLO("./weights/final.pt")


class FrameDetectionResult:
    def __init__(self, videopath, timestamp, frame, conf, img):
        self.videopath = videopath
        self.timestamp = timestamp
        self.frame = frame
        self.conf = conf
        self.img = img

    def save_image_timestamp(self, savepath):
        imgpath = os.path.join(savepath, f"{self.frame}.jpg")
        cv2.imwrite(imgpath, self.img)
        return (str(timedelta(seconds = self.timestamp)), "." + imgpath) 
    
class FileResult:

    def __init__(self, input_filename):
        
        self.input_filename = input_filename
        self.best_seqs = []
        self.ok_seqs = []

    def add_best_sequence(self, seq_tuples_list):
        self.best_seqs.append(seq_tuples_list)
    
    def add_ok_sequence(self, seq_tuples_list):
        self.ok_seqs.append(seq_tuples_list)

    def __repr__(self):
        return f"FileResult(input_filename={self.input_filename}, best_seqs={self.best_seqs}, ok_seqs={self.ok_seqs})"


        


# function to map [videopaths] -> [best[sequence[timestamp, imgpath]], ok[sequence[timestamp, imgpath]]
# files: list of videopaths; savepath: path to resulting dirs; thrall: detection confidence threshold;
# thrbest: best results confidence threshold; timethr: time threshold in seconds to consider a sequence

def detect_video_files(files, upperpath, thrall, thrbest, timethr):

    dirname = str(time.time())
    dirpath = os.path.join(upperpath, dirname)

    #to_train_path = os.path.join("to_train/", dirname)

    if not os.path.exists(dirpath):
        os.mkdir(dirpath)
        #os.mkdir(to_train_path)


    file_results = [dirname]

    for file in files:


        secfname = secure_filename(file.filename)
        

        #secfname_orig = secfname
        secfname = unidecode(secfname)
        secfname = secfname.replace(" ", "_")
        res_obj = FileResult(secfname)
        

        videodirpath = os.path.join(dirpath, secfname)
        os.mkdir(videodirpath)

        tmppath = os.path.join(videodirpath, "tmp")
        outpath = os.path.join(videodirpath, "frame_sequences")
        os.mkdir(tmppath)
        os.mkdir(outpath)

        

        filepath = os.path.join(tmppath, secfname)
        
        file.save(filepath)


        videocap = cv2.VideoCapture(filepath)
        fps = videocap.get(cv2.CAP_PROP_FPS)
        video_w = int(videocap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_h = int(videocap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        #encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

        print(video_w)
        print(video_h)

        results = MODEL.track(filepath, device = 0, stream = True)
        
        

        # get objects
            # save labels
            # with open(f'./resultsManual/labels/5.mp4_{i}.txt', '+w') as file:
            #     for pred in res.boxes.xywhn:
            #         file.write(f"0 {pred[0].item()} {pred[1].item()} {pred[2].item()} {pred[3].item()}\n")
        pred_video = cv2.VideoWriter(os.path.join(videodirpath, secfname), fourcc, fps, (video_w, video_h))
        allobjects = np.array([])
        for i, res in enumerate(results):
            
            if res.boxes.cls.shape[0] == 1:
                if res.boxes.conf > thrall:
                    #with open(os.path.join(to_train_path, f"{i}.txt"), '+w') as txt_file:
                        #for pred in res.boxes.xywhn:
                            #txt_file.write(f"0 {pred[0].item()} {pred[1].item()} {pred[2].item()} {pred[3].item()}\n")
                    timestamp = i // fps
                    allobjects = np.append(
                        allobjects,
                        FrameDetectionResult(
                            file, timestamp, i, res.boxes.conf.cpu().numpy(), res.plot(conf = False, labels = False) # conf = False, labels = False
                        ),
                    )
                    #cv2.imencode('.jpg', res.plot(conf = False, labels = False), encode_param)[1]
                    pred_video.write(res.plot(conf = False, labels = False)) # conf = False, labels = False
                else:
                    pred_video.write(res.orig_img)
            #cv2.imencode('.jpg', res.plot(conf = False, labels = False), encode_param)[1]
            else:
                pred_video.write(res.orig_img)

        pred_video.release()
        shutil.rmtree(tmppath)
        #shutil.move(f"./runs/detect/predict/{secfname}", os.path.join(videodirpath, secfname))
        # obtain sequences using time threshold

        diffs = np.diff([x.timestamp for x in allobjects])
        seqs = []

        shift = 0
        for v in np.split(diffs, np.where(diffs[:-1] > timethr)[0] + 1):
            tmpseq = []
            for k in range(np.size(v)):
                tmpseq.append(allobjects[shift + k])
            if len(tmpseq) > 2*fps:
                seqs.append(tmpseq)
            del tmpseq
            shift += np.size(v)
        del shift

        # split sequences by best confidence inside a sequence
        best_seqs = []
        ok_seqs = []


        for seq in seqs:
            conf = np.max([x.conf for x in seq])
            if conf > thrbest:
                best_seqs.append(seq)
            else:
                ok_seqs.append(seq)
        print(ok_seqs)


        # transform sequences into lists of timestamp and filepaths and save frames
        bestpath = os.path.join(outpath, "best")
        okpath = os.path.join(outpath, "ok")

        os.mkdir(os.path.join(outpath, "best"))
        os.mkdir(os.path.join(outpath, "ok"))
        

        for i, seq in enumerate(best_seqs):
            os.mkdir(os.path.join(bestpath, f"{i}"))
            path = os.path.join(bestpath, f"{i}")
            res_obj.add_best_sequence([x.save_image_timestamp(path) for x in seq])
        for i, seq in enumerate(ok_seqs):
            os.mkdir(os.path.join(okpath, f"{i}"))
            path = os.path.join(okpath, f"{i}")
            res_obj.add_ok_sequence([x.save_image_timestamp(path) for x in seq])

        
        file_results.append(res_obj.__dict__)

        

    return file_results


#def process_feedback(feedback_json):
#   feedback_string = json.loads(feedback_json)

#    filename = 

def send_archive(timestamp):
    path = os.path.join("./static/results", timestamp)
    print(path)
    shutil.make_archive(os.path.join("./static/results", timestamp), 'zip', path)
    #shutil.rmtree(path)
    return f"./static/results/{timestamp}.zip"

