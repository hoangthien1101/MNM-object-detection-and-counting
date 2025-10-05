#!/usr/bin/env python3
"""
detect_image_jetson.py
Tự động chạy inference với best.pt trên test.jpg và lưu kết quả out.jpg.
Dành cho Jetson Nano, không cần truyền tham số.
"""

import os
import sys
import cv2
import numpy as np

# Đường dẫn cố định
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "best.pt")
IMAGE_PATH = os.path.join(BASE_DIR, "test.jpg")
OUTPUT_PATH = os.path.join(BASE_DIR, "out.jpg")

# Kiểm tra file
if not os.path.isfile(MODEL_PATH):
    print("Model file not found:", MODEL_PATH)
    sys.exit(1)
if not os.path.isfile(IMAGE_PATH):
    print("Image file not found:", IMAGE_PATH)
    sys.exit(1)

# Thử import YOLO
USE_ULTRALYTICS = False
USE_TORCHHUB = False
try:
    from ultralytics import YOLO
    USE_ULTRALYTICS = True
except Exception:
    try:
        import torch
        USE_TORCHHUB = True
    except Exception:
        pass

if not (USE_ULTRALYTICS or USE_TORCHHUB):
    print("Error: Cần cài 'ultralytics' hoặc 'torch'")
    sys.exit(1)

def draw_boxes(image, boxes, scores, classes, names, conf_thresh=0.25):
    img = image.copy()
    for bbox, score, cls in zip(boxes, scores, classes):
        if score < conf_thresh:
            continue
        x1, y1, x2, y2 = [int(x) for x in bbox]
        label = f"{names[int(cls)]} {score:.2f}"
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(img, (x1, y1 - th - 6), (x1 + tw, y1), (0, 255, 0), -1)
        cv2.putText(img, label, (x1, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
    return img

def run_ultralytics(model_path, img_path, output_path):
    model = YOLO(model_path)
    device = '0' if model.device.type == 'cuda' else 'cpu'
    results = model.predict(source=img_path, conf=0.25, imgsz=640, device=device, save=False)
    r = results[0]
    boxes_xyxy = []
    scores = []
    classes = []
    for box in r.boxes:
        xyxy = box.xyxy.tolist()[0]
        conf_score = float(box.conf.tolist()[0])
        cls = int(box.cls.tolist()[0])
        boxes_xyxy.append(xyxy)
        scores.append(conf_score)
        classes.append(cls)
    names = model.names if hasattr(model, "names") else {i:str(i) for i in range(100)}
    img = cv2.imread(img_path)
    out = draw_boxes(img, boxes_xyxy, scores, classes, names)
    cv2.imwrite(output_path, out)
    print(f"Saved result to {output_path}")

def run_torchhub(model_path, img_path, output_path):
    import torch
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=False)
    if device=='cuda':
        model.to('cuda')
    results = model(img_path, size=640)
    df = results.pandas().xyxy[0]
    boxes, scores, classes = [], [], []
    names = results.names
    img = cv2.imread(img_path)
    for idx, row in df.iterrows():
        boxes.append([int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])])
        scores.append(float(row['confidence']))
        classes.append(int(row['class']))
    out = draw_boxes(img, boxes, scores, classes, names)
    cv2.imwrite(output_path, out)
    print(f"Saved result to {output_path}")

def main():
    try:
        if USE_ULTRALYTICS:
            run_ultralytics(MODEL_PATH, IMAGE_PATH, OUTPUT_PATH)
        else:
            run_torchhub(MODEL_PATH, IMAGE_PATH, OUTPUT_PATH)
    except Exception as e:
        print("Inference failed:", e)
        import traceback; traceback.print_exc()

if __name__ == '__main__':
    main()

