from ultralytics import YOLO
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from datetime import timedelta
import os
import cv2
import numpy as np
import time

MODEL = YOLO('./weights/best_china.pt')


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

    def add_best_sequence(self, seq_dict):
        self.best_seqs.append(seq_dict)
    
    def add_ok_sequence(self, seq_dict):
        self.ok_seqs.append(seq_dict)

        


# function to map [videopaths] -> [best[sequence[timestamp, imgpath]], ok[sequence[timestamp, imgpath]]
# files: list of videopaths; savepath: path to resulting dirs; thrall: detection confidence threshold;
# thrbest: best results confidence threshold; timethr: time threshold in seconds to consider a sequence

def detect_video_files(files, upperpath, thrall, thrbest, timethr):

    dirname = str(time.time())
    dirpath = os.path.join(upperpath, dirname)


    os.mkdir(dirpath)


    file_results = []

    for file in files:


        secfname = secure_filename(file.filename)
        res_obj = FileResult(secfname)

        videodirpath = os.path.join(dirpath, secfname)
        os.mkdir(videodirpath)

        tmppath = os.path.join(videodirpath, "tmp")
        outpath = os.path.join(videodirpath, "output")
        os.mkdir(tmppath)
        os.mkdir(outpath)

        

        filepath = os.path.join(tmppath, secfname)
        
        file.save(filepath)


        videocap = cv2.VideoCapture(filepath)
        fps = videocap.get(cv2.CAP_PROP_FPS)

        results = MODEL.track(filepath, stream = True)

        # get objects
            # with open(f'./resultsManual/labels/5.mp4_{i}.txt', '+w') as file:
            #     for pred in res.boxes.xywhn:
            #         file.write(f"0 {pred[0].item()} {pred[1].item()} {pred[2].item()} {pred[3].item()}\n")

        allobjects = np.array([])
        for i, res in enumerate(results):
            if res.boxes.cls.shape[0] == 1:
                if res.boxes.conf > thrall:
                    timestamp = i // fps
                    allobjects = np.append(
                        allobjects,
                        FrameDetectionResult(
                            file, timestamp, i, res.boxes.conf.cpu().numpy(), res.plot()
                        ),
                    )

        # obtain sequences using time threshold

        diffs = np.diff([x.timestamp for x in allobjects])
        seqs = []

        shift = 0
        for v in np.split(diffs, np.where(diffs[:-1] > timethr)[0] + 1):
            tmpseq = []
            for k in range(np.size(v)):
                tmpseq.append(allobjects[shift + k])
            seqs.append(tmpseq)
            #del tmpseq
            shift += np.size(v)
        #del shift

        # split sequences by best confidence inside a sequence
        best_seqs = []
        ok_seqs = []

        #seqs.insert(0, []) # best sequences
        #seqs.insert(1, []) # ok sequences

        for seq in seqs:
            conf = np.max([x.conf for x in seq])
            if conf > thrbest:
                best_seqs.append(seq)
                #seqs[0].insert(ind + 2, seqs.pop(ind + 2))
                #seqs.pop(ind)
            else:
                #seqs[1].insert(ind + 2, seqs.pop(ind + 2))
                #seqs[1].insert(ind, seq)
                #seqs.pop(ind)
                ok_seqs.append(seq)

        # transform sequences into lists of timestamp and filepaths

        bestpath = os.path.join(outpath, "best")
        okpath = os.path.join(outpath, "ok")

        os.mkdir(os.path.join(outpath, "best"))
        os.mkdir(os.path.join(outpath, "ok"))
        

        for i, seq in enumerate(best_seqs):
            os.mkdir(os.path.join(bestpath, f"{i}"))
            path = os.path.join(bestpath, f"{i}")
            res_obj.add_best_sequence(dict([x.save_image_timestamp(path) for x in seq]))
        for i, seq in enumerate(ok_seqs):
            os.mkdir(os.path.join(okpath, f"{i}"))
            path = os.path.join(okpath, f"{i}")
            res_obj.add_ok_sequence(dict([x.save_image_timestamp(path) for x in seq]))


        print(res_obj.ok_seqs)
        
        file_results.append(res_obj.__dict__)

        

    return file_results


#def processFeedback(feedback_string):