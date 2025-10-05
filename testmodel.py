from ultralytics import YOLO
import torch

# Thêm DetectionModel vào safe globals để load model
torch.serialization.add_safe_globals(['ultralytics.nn.tasks.DetectionModel'])

model = YOLO("D:/WorkSpace/Homework/NAM4/MNM/DetectB501/model/best (1).pt")

print(model.task, model.model.yaml)
