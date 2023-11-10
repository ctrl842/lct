import av
import io
import cv2 as cv

import time
import cv2
from playsound import playsound
import numpy as np

def rotate_image(image, angle):
    height, width = image.shape[:2]
    image_center = (width/2, height/2)
    matrix = cv.getRotationMatrix2D(image_center, angle, 1.)
    abs_cos = abs(matrix[0,0])
    abs_sin = abs(matrix[0,1])
    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)
    matrix[0, 2] += bound_w/2 - image_center[0]
    matrix[1, 2] += bound_h/2 - image_center[1]
    matrix = cv.warpAffine(image, matrix, (bound_w, bound_h))
    return matrix

class VideoReader:
    def __init__(self, source_path, step=1, start=0, stop=None):
        self._source_path = source_path
        self._step = step
        self._start = start
        self._stop = stop + 1 if stop is not None else stop


    def _has_frame(self, i):
        if i >= self._start:
            if (i - self._start) % self._step == 0:
                if self._stop is None or i < self._stop:
                    return True

        return False

    def __iter__(self):
        with self._get_av_container() as container:
            stream = container.streams.video[0]
            stream.thread_type = 'AUTO'
            frame_num = 0
            for packet in container.demux(stream):
                for image in packet.decode():
                    frame_num += 1
                    if self._has_frame(frame_num - 1):
                        if packet.stream.metadata.get('rotate'):
                            pts = image.pts
                            image = av.VideoFrame().from_ndarray(
                                rotate_image(
                                    image.to_ndarray(format='bgr24'),
                                    360 - int(stream.metadata.get('rotate'))
                                ),
                                format ='bgr24'
                            )
                            image.pts = pts
                        yield (image, self._source_path[0], image.pts)

    def get_progress(self, pos):
        duration = self._get_duration()
        return pos / duration if duration else None

    def _get_av_container(self):
        if isinstance(self._source_path[0], io.BytesIO):
            self._source_path[0].seek(0) # required for re-reading
        return av.open(self._source_path[0])

    def _get_duration(self):
        with self._get_av_container() as container:
            stream = container.streams.video[0]
            duration = None
            if stream.duration:
                duration = stream.duration
            else:
                # may have a DURATION in format like "01:16:45.935000000"
                duration_str = stream.metadata.get("DURATION", None)
                tb_denominator = stream.time_base.denominator
                if duration_str and tb_denominator:
                    _hour, _min, _sec = duration_str.split(':')
                    duration_sec = 60*60*float(_hour) + 60*float(_min) + float(_sec)
                    duration = duration_sec * tb_denominator
            return duration

    def get_preview(self, frame):
        with self._get_av_container() as container:
            stream = container.streams.video[0]
            tb_denominator = stream.time_base.denominator
            needed_time = int((frame / stream.guessed_rate) * tb_denominator)
            container.seek(offset=needed_time, stream=stream)
            for packet in container.demux(stream):
                for frame in packet.decode():
                    return self._get_preview(frame.to_image() if not stream.metadata.get('rotate') \
                        else av.VideoFrame().from_ndarray(
                            rotate_image(
                                frame.to_ndarray(format='bgr24'),
                                360 - int(container.streams.video[0].metadata.get('rotate'))
                            ),
                            format ='bgr24'
                        ).to_image()
                    )

    def get_image_size(self, i):
        image = (next(iter(self)))[0]
        return image.width, image.height
    
import numpy as np
import imutils
import cv2
from modules.detection import detect_people
import supervision as sv
from ultralytics import YOLO
labelsPath = "yolo-coco/coco.names"
LABELS = open(labelsPath).read().strip().split("\n")

model = YOLO("yolov8s.pt")
model.export(format='onnx', opset=12)
net = cv2.dnn.readNetFromONNX("yolov8s.onnx") 
if True:
	# set CUDA as the preferable backend and target
	print("")
	print("[INFO] Looking for GPU")
	net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
	net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
classes = []
with open(labelsPath, "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))

cap = cv2.VideoCapture(0)       #Start Video Streaming
while (cap.isOpened()):
    ret, image = cap.read()

    if ret == False:
        break

    img = imutils.resize(image, width=600)
    height, width, channels = img.shape
    blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

    net.setInput(blob)
    outs = net.forward(output_layers) 
    results = detect_people(image, net, output_layers,
                            personIdx=LABELS.index("person"))

    # Showing  @information on the screen
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            classIDs = np.argmax(scores)
            confidence = scores[classIDs]
            if confidence > 0.5:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(classIDs)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    font = cv2.FONT_HERSHEY_PLAIN
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            if(classes[class_ids[i]] == classes[class_ids[i]] ):
               
                color = colors[i]
                cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
                cv2.putText(image, label, (x, y + 30), font, 3, color, 3)
                print(label)
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.3)
    ind = []
    for i in range(0, len(class_ids)):
        if (class_ids[i] == 0):
            ind.append(i)
    a = []
    b = []
    #color = (0, 255, 0)
    if len(idxs) > 0:
        for i in idxs.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
            a.append(x)
            b.append(y)
    distance = []
    nsd = []
    for i in range(0, len(a) - 1):
        for k in range(1, len(a)):
            if (k == i):
                break
            else:
                x_dist = (a[k] - a[i])
                y_dist = (b[k] - b[i])
                d = math.sqrt(x_dist * x_dist + y_dist * y_dist)
                distance.append(d)
                if (d <= 100.0):
                    nsd.append(i)
                    nsd.append(k)
                nsd = list(dict.fromkeys(nsd))

    color = (0, 0, 255)
    for i in nsd:
        (x, y) = (boxes[i][0], boxes[i][1])
        (w, h) = (boxes[i][2], boxes[i][3])
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 1)
        text = "Alert"
        cv2.putText(image, text, (x, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    color = (138, 68, 38)
    if len(idxs) > 0:
        for i in idxs.flatten():
            if (i in nsd):
                break
            else:
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])
                cv2.rectangle(image, (x, y), (x + w, y + h), color, 1)
                text = "SAFE"
                cv2.putText(image, text, (x, y - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            # _____________________________________________________________________ #
            #  Counting Sources

            serious = set()
            abnormal = set()

            # ensure there are *at least* two people detections (required in
            # order to compute our pairwise distance maps)
            if len(results) >= 2:
                # extract all centroids from the results and compute the
                # Euclidean distances between all pairs of the centroids
                centroids = np.array([r[2] for r in results])
                D = dist.cdist(centroids, centroids, metric="euclidean")

                # loop over the upper triangular of the distance matrix
                for i in range(0, D.shape[0]):
                    for j in range(i + 1, D.shape[1]):
                        # check to see if the distance between any two
                        # centroid pairs is less than the configured number of pixels
                        if D[i, j] < 50:
                            # update our violation set with the indexes of the centroid pairs
                            serious.add(i)
                            serious.add(j)
                        # update our abnormal set if the centroid distance is below max distance limit
                        if (D[i, j] < 80) and not serious:
                            abnormal.add(i)
                            abnormal.add(j)

            # loop over the results
            for (i, (prob, bbox, centroid)) in enumerate(results):
                # extract the bounding box and centroid coordinates, then
                # initialize the color of the annotation
                (startX, startY, endX, endY) = bbox
                (cX, cY) = centroid
                color = (0, 255, 0)

                # if the index pair exists within the violation/abnormal sets, then update the color
                if i in serious:
                    color = (0, 0, 255)
                elif i in abnormal:
                    color = (0, 255, 255) #orange = (0, 165, 255)

           
                cv2.circle(image, (cX, cY), 2, color, 2)


    cv2.imshow("output frame",image)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

class VideoStreaming(object):
    def __init__(self):
        super(VideoStreaming, self).__init__()
        self.VIDEO = cv2.VideoCapture(0)

        self.MODEL = ObjectDetection()

        self._preview = True
        self._flipH = False
        self._detect = True
        self._exposure = self.VIDEO.get(cv2.CAP_PROP_EXPOSURE)
        self._contrast = self.VIDEO.get(cv2.CAP_PROP_CONTRAST)

    @property
    def preview(self):
        return self._preview

    @preview.setter
    def preview(self, value):
        self._preview = bool(value)

    @property
    def flipH(self):
        return self._flipH

    @flipH.setter
    def flipH(self, value):
        self._flipH = bool(value)

    @property
    def detect(self):
        return self._detect

    @detect.setter
    def detect(self, value):
        self._detect = bool(value)
    
    @property
    def exposure(self):
        return self._exposure

    @exposure.setter
    def exposure(self, value):
        self._exposure = value
        self.VIDEO.set(cv2.CAP_PROP_EXPOSURE, self._exposure)
    
    @property
    def contrast(self):
        return self._contrast

    @contrast.setter
    def contrast(self, value):
        self._contrast = value
        self.VIDEO.set(cv2.CAP_PROP_CONTRAST, self._contrast)

    def show(self):
        currentframe = 0
        while(self.VIDEO.isOpened()):
            ret, snap = self.VIDEO.read()
            if self.flipH:
                snap = cv2.flip(snap, 1)
            
            if ret == True:
                if self._preview:
                    # snap = cv2.resize(snap, (0, 0), fx=0.5, fy=0.5)
                    if self.detect:
                        snap = self.MODEL.detectObj(snap, currentframe)

                else:
                    snap = np.zeros((
                        int(self.VIDEO.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                        int(self.VIDEO.get(cv2.CAP_PROP_FRAME_WIDTH))
                    ), np.uint8)
                    label = 'camera disabled'
                    H, W = snap.shape
                    font = cv2.FONT_HERSHEY_PLAIN
                    color = (255,255,255)
                    cv2.putText(snap, label, (W//2 - 100, H//2), font, 2, color, 2)
		    
                
                frame = cv2.imencode('.jpg', snap)[1].tobytes()
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                time.sleep(0.01)

            else:
                break
        print('off')



class ObjectDetection:
    def __init__(self):
        self.MODEL = cv2.dnn.readNet(
            'weights/yolov3.onxx',
            oftp=12
        )

        self.CLASSES = []
        with open("weights/obj.names", "r") as f:
            self.CLASSES = [line.strip() for line in f.readlines()]

        self.OUTPUT_LAYERS = [self.MODEL.getLayerNames()[i[0] - 1] for i in self.MODEL.getUnconnectedOutLayers()]
        self.COLORS = np.random.uniform(0, 255, size=(len(self.CLASSES), 3))
        self.COLORS /= (np.sum(self.COLORS**2, axis=1)**0.5/255)[np.newaxis].T
    
    def detectObj(self, snap, currentframe):
        #codec = cv2.VideoWriter_fourcc(*'XVID') 
        #output1 = cv2.VideoWriter('webcam_output.avi', codec, 2.5 ,(640,480))
        height, width, channels = snap.shape
        blob = cv2.dnn.blobFromImage(snap, 1/255, (416, 416), swapRB=True, crop=False)

        self.MODEL.setInput(blob)
        outs = self.MODEL.forward(self.OUTPUT_LAYERS)

        # Showing informations on the screen
        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.3:
                    # Object detected
                    center_x = int(detection[0]*width)
                    center_y = int(detection[1]*height)
                    w = int(detection[2]*width)
                    h = int(detection[3]*height)

                    #print(w, h)		     

                    # Rectangle coordinates
                    x = int(center_x - w/2)
                    y = int(center_y - h/2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        font = cv2.FONT_HERSHEY_PLAIN
        
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(self.CLASSES[class_ids[i]])
                color = self.COLORS[i]
                
                cv2.rectangle(snap, (x, y), (x + w, y + h), color, 2)
                cv2.putText(snap, label, (x, y - 5), font, 2, color, 2)
                
                if label == "Gun" or label == "Knife":
                    playsound("siren.wav")
                    name = './output/frames/frame' + str(currentframe) + '.jpg'
                    print ('Creating...' + name)
                    cv2.imwrite(name, snap)
                    currentframe += 1
        
                
        #output1.release()    
        return snap
    

    def create_tmp_dir():
    return tempfile.mkdtemp(prefix='weapn-', suffix='.data')

def delete_tmp_dir(tmp_dir):
    if tmp_dir:
        shutil.rmtree(tmp_dir)
