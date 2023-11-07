from ultralytics import YOLO
import os
from datetime import timedelta
import cv2
import numpy as np

MODEL = YOLO('./best.pt')


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
        return [str(timedelta(seconds = self.timestamp)), imgpath]


# function to map [videopaths] -> [best[sequence[timestamp, imgpath]], ok[sequence[timestamp, imgpath]]
# files: list of videopaths; savepath: path to resulting dirs; thrall: detection confidence threshold;
# thrbest: best results confidence threshold; timethr: time threshold in seconds to consider a sequence
def detect_video_files(files, savepath, thrall, thrbest, timethr):

    for file in files:

        os.mkdir(os.path.join(savepath, file))
        respath = os.path.join(savepath, file)

        video = cv2.VideoCapture(file)
        fps = video.get(cv2.CAP_PROP_FPS)

        results = MODEL.track(file, stream=True)

        # get objects
        stamps = np.array([])
        allobjects = np.array([])
        for i, res in enumerate(results):
            if res.boxes.cls.shape[0] == 1:
                if res.boxes.conf > thrall:
                    timestamp = i // fps
                    stamps = np.append(timestamp)
                    allobjects = np.append(
                        allobjects,
                        VideoDetectionResult(
                            file, timestamp, i, res.boxes.conf, res.plot()
                        ),
                    )

        # obtain sequences using time threshold
        diffs = np.diff(stamps)
        seqs = []
        len = 0
        for v in np.split(diffs, np.where(diffs[:-1] > timethr)[0] + 1):
            tmpseq = []
            for k in range(np.size(v)):
                tmpseq.append(allobjects[len + k])
            seqs.append(tmpseq)
            len += np.size(v)

        # split sequences by best confidence inside a sequence
        best_seqs = []
        ok_seqs = []

        for seq in seqs:
            conf = max([x.conf for x in seq])
            if conf > thrbest:
                best_seqs.append(seq)
            else:
                ok_seqs.append(seq)

        # transform sequences into lists of timestamp and filepaths
        os.mkdir(os.path.join(respath, "best"))
        bestpath = os.path.join(respath, "best")
        os.mkdir(os.path.join(respath, "ok"))
        okpath = os.path.join(respath, "ok")
        best_lists = []
        ok_lists = []
        for i, seq in enumerate(best_seqs):
            os.mkdir(os.path.join(bestpath, f"{i}"))
            path = os.path.join(bestpath, f"{i}")
            best_lists.append([x.save_image_timestamp(path) for x in seq])
        for i, seq in enumerate(ok_seqs):
            os.mkdir(os.path.join(okpath, f"{i}"))
            path = os.path.join(okpath, f"{i}")
            ok_lists.append([x.save_image_timestamp(path) for x in seq])

    return [best_lists, ok_lists]

"""
Speed: 3.1ms preprocess, 10.1ms inference, 1.0ms postprocess per image at shape (1, 3, 384, 640)

[[],
 [[['0:00:34', 'save/test.mp4/ok/0/866.jpg'],
   ['0:00:34', 'save/test.mp4/ok/0/867.jpg'],
   ['0:00:36', 'save/test.mp4/ok/0/917.jpg'],
   ['0:00:38', 'save/test.mp4/ok/0/954.jpg'],
   ['0:00:38', 'save/test.mp4/ok/0/955.jpg'],
   ['0:00:38', 'save/test.mp4/ok/0/967.jpg'],
   ['0:00:38', 'save/test.mp4/ok/0/969.jpg'],
   ['0:00:38', 'save/test.mp4/ok/0/971.jpg'],
   ['0:00:39', 'save/test.mp4/ok/0/989.jpg'],
   ['0:00:39', 'save/test.mp4/ok/0/990.jpg'],
   ['0:00:39', 'save/test.mp4/ok/0/991.jpg'],
   ['0:00:39', 'save/test.mp4/ok/0/992.jpg'],
   ['0:00:39', 'save/test.mp4/ok/0/993.jpg']]]]
"""