import cv2
import torch
import time
import json
import subprocess
import sys
from ultralytics import YOLO


# ==== CẤU HÌNH ====
MODEL_PATH = "model/best5n.pt"           # file model YOLO đã train
VIDEO_PATH = "input.mp4"          # video input
OUTPUT_PATH = "output.mp4"        # video output
JSON_PATH = "objects_data.json"   # file JSON chứa object & số lượng mong muốn
RESULT_JSON_PATH = "result_count.json"  # file JSON xuất kết quả

# ==== LOAD MODEL ====
model = YOLO(MODEL_PATH)

# ==== ĐỌC FILE JSON ====
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)
    expected_objects = {obj["name"].lower(): obj["expected_count"] for obj in data}

print("Expected objects:", expected_objects)

# ==== MỞ VIDEO ====
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print("Không thể mở video")
    exit()

# Thông tin video
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps_input = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"Video input: {width}x{height}, {fps_input} FPS, {total_frames} frames")

# Lưu video output
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(OUTPUT_PATH, fourcc, fps_input, (width, height))

# ==== Biến lưu kết quả cuối cùng ====
final_detected_counts = {}

# ==== LOOP DETECT ====
frame_idx = 0  # đếm số frame

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_idx += 1
    start_time = time.time()

    # Detect object (không resize để giữ nguyên tỉ lệ)
    results = model(frame, conf=0.5, verbose=False)

    # Đếm object detect được
    detected_counts = {}
    for box in results[0].boxes:
        cls_id = int(box.cls)
        cls_name = model.names[cls_id].lower()  # chuyển về chữ thường
        detected_counts[cls_name] = detected_counts.get(cls_name, 0) + 1

    # Cập nhật kết quả cuối cùng (frame cuối)
    final_detected_counts = detected_counts.copy()

    # ==== Chỉ in thông báo mỗi 10 frame ====
    if frame_idx % 10 == 0:
        print(f"\n--- Frame {frame_idx}/{total_frames} ---")
        for obj_name, expected_count in expected_objects.items():
            detected_count = detected_counts.get(obj_name, 0)
            if detected_count == expected_count:
                print(f"✓ Đã đủ {expected_count} {obj_name}")
            elif detected_count < expected_count:
                print(f"✗ Thiếu {expected_count - detected_count} {obj_name} (có {detected_count}/{expected_count})")
            else:
                print(f"⚠ Thừa {detected_count - expected_count} {obj_name} (có {detected_count}/{expected_count})")

    # Vẽ kết quả
    annotated_frame = results[0].plot()

    # Tính FPS
    end_time = time.time()
    fps = 1 / (end_time - start_time + 1e-6)

    # Hiển thị FPS trên khung hình
    cv2.putText(annotated_frame, f"FPS: {fps:.2f}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Xuất ra video
    out.write(annotated_frame)

    # Hiển thị
    cv2.imshow("YOLOv5 Detection", annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# ==== XUẤT KẾT QUẢ RA JSON ====
result_data = []

for obj_name, expected_count in expected_objects.items():
    detected_count = final_detected_counts.get(obj_name, 0)
    difference = detected_count - expected_count
    
    status = "đủ"
    if difference < 0:
        status = "thiếu"
    elif difference > 0:
        status = "thừa"
    
    result_data.append({
        "object_name": obj_name,
        "expected_count": expected_count,
        "detected_count": detected_count,
        "status": status,
        "difference": abs(difference)
    })

# Ghi ra file JSON
with open(RESULT_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(result_data, f, ensure_ascii=False, indent=4)

print(f"\n✓ Đã xuất kết quả ra file: {RESULT_JSON_PATH}")

# In kết quả tổng kết
print("\n==== KẾT QUẢ CUỐI CÙNG ====")
for item in result_data:
    if item["status"] == "đủ":
        print(f"✓ {item['object_name']}: Đủ {item['expected_count']}")
    elif item["status"] == "thiếu":
        print(f"✗ {item['object_name']}: Thiếu {item['difference']} (có {item['detected_count']}/{item['expected_count']})")
    else:
        print(f"⚠ {item['object_name']}: Thừa {item['difference']} (có {item['detected_count']}/{item['expected_count']})")

# ==== CLEANUP ====
cap.release()
out.release()
cv2.destroyAllWindows()

# ==== GỌI GỬI TELEGRAM SAU KHI XỬ LÝ XONG ====
try:
    print("\n🚀 Đang gọi send_tele.py để gửi kết quả...")
    subprocess.run([sys.executable, 'send_tele.py'], check=True)
    print("✅ Đã gửi kết quả qua Telegram.")
except Exception as e:
    print(f"✗ Không thể gửi Telegram: {e}")