from audioop import avg
from glob import glob
import cv2
import numpy as np
import os
def match_images(img1_path, img2_path):
        print(img1_path)
        print(img2_path)
         # Load YOLOv3 pre-trained model
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        weights_path = os.path.join(BASE_DIR, "yolov3.weights")
        config_path = os.path.join(BASE_DIR, "yolov3.cfg")
        coco_path = os.path.join(BASE_DIR, "coco.names")

        net = cv2.dnn.readNet(weights_path, config_path)

        # Load classes
        classes = []
        with open(coco_path, "r") as f:
            classes = [line.strip() for line in f.readlines()]

        # Define colors for each class
        colors = np.random.uniform(0, 255, size=(len(classes), 3))

        # Load first image
        img1 = cv2.imread(img1_path)
        img1 = cv2.resize(img1,(512,512))
        height1, width1, _ = img1.shape

        # Load second image
        img2 = cv2.imread(img2_path)
        img2 = cv2.resize(img2,(512,512))

        height2, width2, _ = img2.shape

        # Create input blob for first image
        blob1 = cv2.dnn.blobFromImage(img1, 1/255.0, (416, 416), swapRB=True, crop=False)

        # Set input blob for first image
        net.setInput(blob1)

        # Get output layers of YOLOv3
        
        layer_names = net.getLayerNames()
        temp = []
        for i in net.getUnconnectedOutLayers():
            temp.append([i])
        output_layers = [layer_names[i[0] - 1] for i in temp]


        # Forward pass for first image
        outs1 = net.forward(output_layers)

        # Extract bounding boxes, confidences and class IDs for first image
        boxes1 = []
        confidences1 = []
        class_ids1 = []
        for out in outs1:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * width1)
                    center_y = int(detection[1] * height1)
                    w = int(detection[2] * width1)
                    h = int(detection[3] * height1)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes1.append([x, y, w, h])
                    confidences1.append(float(confidence))
                    class_ids1.append(class_id)

        # Create input blob for second image
        blob2 = cv2.dnn.blobFromImage(img2, 1/255.0, (416, 416), swapRB=True, crop=False)

        # Set input blob for second image
        net.setInput(blob2)

        # Forward pass for second image
        outs2 = net.forward(output_layers)

        # Extract bounding boxes, confidences and class IDs for second image
        boxes2 = []
        confidences2 = []
        class_ids2 = []
        for out in outs2:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * width2)
                    center_y = int(detection[1] * height2)
                    w = int(detection[2] * width2)
                    h = int(detection[3] * height2)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes2.append([x, y, w, h])
                    confidences2.append(float(confidence))
                    class_ids2.append(class_id)

        # Non-maximum suppression to remove overlapping boxes
        indices1 = cv2.dnn.NMSBoxes(boxes1, confidences1, score_threshold=0.5, nms_threshold=0.4)
        indices2 = cv2.dnn.NMSBoxes(boxes2, confidences2, score_threshold=0.5, nms_threshold=0.4)

        # Extract objects from first image and resize to the size of second image
        objects1 = []
        for i in indices1:
            
            box = boxes1[i]
            x, y, w, h = box
            object1 = img1[y:y+h, x:x+w]
            object1_resized = cv2.resize(object1, (width2, height2), interpolation=cv2.INTER_AREA)
            objects1.append(object1_resized)

        # Extract objects from second image and resize to the size of first image
        objects2 = []
        for i in indices2:
            
            box = boxes2[i]
            x, y, w, h = box
            object2 = img2[y:y+h, x:x+w]
            if not object2.size:
                print("Object2 image is empty.")
            else:
                    # resize object2 to match object1 size
                object2_resized = cv2.resize(object2, (width1, height1), interpolation=cv2.INTER_AREA)
                objects2.append(object2_resized)
           
        # Compare each pair of objects and calculate the average difference score
        total_score = 0
        num_comparisons = 0
        for obj1 in objects1:
            for obj2 in objects2:
                # Compare the two images
                difference = cv2.subtract(obj1, obj2)
                score = np.sum(difference) / (obj1.shape[0] * obj1.shape[1] * obj1.shape[2])
                total_score += score
                num_comparisons += 1
        if num_comparisons != 0:
            avg_score = total_score / num_comparisons
        else:
            avg_score = 0

        # If the average difference score is below a certain threshold, consider the images a match
        if avg_score == 0:
            return True
        else:
            return False

  

    
