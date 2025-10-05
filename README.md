# 🎯 Quản lý vật thể + Nhận diện YOLO

Ứng dụng desktop quản lý danh sách vật thể và chạy nhận diện video bằng YOLO. Dữ liệu vật thể lưu trong JSON, nhận diện xong tự động gửi kết quả qua Telegram.

## ✨ Tính năng

- **Quản lý vật thể**: Thêm, sửa, xóa các vật thể cần theo dõi (`simple_app.py`).
- **Lưu trữ đơn giản**: Dữ liệu trong `objects_data.json`.
- **Nhận diện video YOLO**: `detect_video.py` đọc `input.mp4`, resize mọi khung hình về 1080x720, phát hiện và ghi `output.mp4`.
- **Gửi Telegram**: Sau khi xử lý xong, tự động gọi `send_tele.py` để gửi tóm tắt và file `result_count.json`.

## 🏗️ Cấu trúc project (rút gọn)

```
DetectB501/
├── simple_app.py          # Ứng dụng desktop (tkinter)
├── detect_video.py        # Nhận diện YOLO trên video
├── send_tele.py           # Gửi kết quả lên Telegram
├── model/                 # Thư mục chứa file .pt (YOLO)
├── input.mp4              # Video đầu vào
├── output.mp4             # Video đầu ra (được ghi)
├── objects_data.json      # Danh sách vật thể mong đợi (GUI quản lý)
├── result_count.json      # Kết quả đếm cuối cùng
├── requirements.txt       # Dependencies Python
├── start_simple.bat/.sh   # Script chạy GUI
└── README.md
```

## 🚀 Cài đặt

```bash
pip install -r requirements.txt
```

Ghi chú:
- Cần Python 3.8–3.10 tương thích với PyTorch/Torchvision đã pin trong `requirements.txt`.
- `tkinter` thường đi kèm Python (Windows/macOS). Linux có thể cần cài thêm gói `python3-tk`.
- Đặt file model vào `model/` và cập nhật `MODEL_PATH` trong `detect_video.py` nếu cần.

## 🖥️ Sử dụng GUI (khuyến nghị)

1) Chạy GUI:

```bash
python simple_app.py
```

2) Tạo/cập nhật danh sách vật thể mong đợi trong bảng (được lưu vào `objects_data.json`).

3) Nhấn nút "▶ Bắt đầu giám sát":
- Ứng dụng sẽ khởi chạy `detect_video.py` bằng Python hiện tại rồi đóng GUI.
- `detect_video.py` sẽ:
  - Đọc `input.mp4` và resize mọi frame về 1080x720 trước khi detect.
  - Chạy YOLO trên frame đã resize, vẽ kết quả và ghi `output.mp4` (1080x720).
  - Tạo `result_count.json` (so sánh với `objects_data.json`).
  - Tự động gọi `send_tele.py` để gửi tin nhắn + file JSON qua Telegram.

## ▶ Chạy nhận diện trực tiếp (không qua GUI)

```bash
python detect_video.py
```

Mặc định sử dụng:
- `MODEL_PATH = model/best5n.pt`
- `VIDEO_PATH = input.mp4`
- `OUTPUT_PATH = output.mp4`
- Resize khung hình: 1080x720

Có thể chỉnh các hằng số này trong `detect_video.py`.

## 📬 Cấu hình Telegram

Trong `send_tele.py`:
- `TELEGRAM_BOT_TOKEN`: Token bot Telegram của bạn.
- `TELEGRAM_CHAT_ID`: Chat ID cần gửi.

Script sẽ đọc `result_count.json`, tạo thông điệp tóm tắt và gửi kèm file JSON.
