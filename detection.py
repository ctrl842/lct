import cv2
from ultralytics import YOLO
import os
from datetime import timedelta


MODEL = YOLO('best.pt')


class VideoDetectionResult:
    def __init__(self, videopath, timestamp, frame, conf, img):
        self.videopath = videopath
        self.timestamp = timestamp
        self.frame = frame
        self.conf = conf
        self.img = img
        # self.feedback = False

    def save_image_timestamp(self, savepath):
        imgpath = os.path.join(savepath, f"{self.frame}.jpg")
        cv2.imwrite(imgpath, self.img)
        return [self.timestamp, imgpath]
    

def detect_video_files(files, savepath):

    for file in files:
        respath = os.mkdir(os.path.join(savepath, file))

        video = cv2.VideoCapture(file)
        fps = video.get(cv2.CAP_PROP_FPS)

        res = MODEL.track(file, stream=True)

        # get objects
        allObjs = []
        for i, res in enumerate(res):
            if res.boxes.cls.shape[0] == 1:
                timestamp = timedelta(seconds=fps * i)
                conf = res.boxes.conf
                allObjs.append(
                    VideoDetectionResult(file, timestamp, i, conf, res.plot())
                )

        # obtain sequences using time threshold
        timethr = 3
        seqs = [[]]
        for i, obj in enumerate(allObjs):
            seqs[-1].append(obj)
            if allObjs[i + 1].timestamp - obj.timestamp > timethr:
                seqs.append([])

        # split sequences by best conf inside a sequence
        best_seqs = [[]]
        ok_seqs = [[]]

        for seq in seqs:
            conf = max([x.conf for x in seq])
            if conf > 0.85:
                best_seqs.append(seq)
            else:
                ok_seqs.append(seq)

        # transform sequences into lists of timestamp and filepaths
        bestpath = os.mkdir(os.path.join(respath, "best"))
        okpath = os.mkdir(os.path.join(respath, "ok"))
        for i, seq in enumerate(best_seqs):
            path = os.mkdir(os.path.join(bestpath, "i"))
            lists = [x.save_image_timestamp(path) for x in seq]
        for i, seq in enumerate(ok_seqs):
            path = os.mkdir(os.path.join(okpath, "i"))
            lists = [x.save_image_timestamp(path) for x in seq]

    return [best_seqs, ok_seqs]