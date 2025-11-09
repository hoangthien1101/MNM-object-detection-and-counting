# 📖 HƯỚNG DẪN CHI TIẾT PROJECT DETECTB501

## 📋 MỤC LỤC

1. [Tổng quan Project](#tổng-quan-project)
2. [Kiến trúc Hệ thống](#kiến-trúc-hệ-thống)
3. [Cấu trúc Thư mục và File](#cấu-trúc-thư-mục-và-file)
4. [Chi tiết từng Module](#chi-tiết-từng-module)
5. [Luồng Hoạt động](#luồng-hoạt-động)
6. [Cấu hình và Thiết lập](#cấu-hình-và-thiết-lập)
7. [Hướng dẫn Sử dụng](#hướng-dẫn-sử-dụng)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 TỔNG QUAN PROJECT

### Mục đích
**DetectB501** là hệ thống giám sát và nhận diện vật thể tự động sử dụng công nghệ YOLO (You Only Look Once). Hệ thống được thiết kế để:
- Quản lý danh sách vật thể cần theo dõi
- Nhận diện vật thể real-time từ camera hoặc video file
- So sánh số lượng vật thể phát hiện được với số lượng mong đợi
- Tự động gửi cảnh báo qua Telegram khi phát hiện vấn đề
- Gửi báo cáo định kỳ để theo dõi trạng thái liên tục

### Công nghệ sử dụng
- **YOLO (Ultralytics)**: Mô hình deep learning để nhận diện vật thể
- **OpenCV**: Xử lý video và hình ảnh
- **Tkinter**: Giao diện người dùng (GUI)
- **Telegram Bot API**: Gửi thông báo và cảnh báo
- **Python 3.8-3.10**: Ngôn ngữ lập trình chính

---

## 🏗️ KIẾN TRÚC HỆ THỐNG

### Sơ đồ tổng quan

```
┌─────────────────────────────────────────────────────────┐
│                    SIMPLE_APP.PY                        │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │  Tab 1: Quản lý  │      │  Tab 2: Nhận diện│        │
│  │     Vật thể      │      │      Video       │        │
│  │                  │      │                  │        │
│  │ - Thêm/Sửa/Xóa   │      │ - Chọn nguồn     │        │
│  │ - Lưu JSON       │      │ - Hiển thị video │        │
│  │                  │      │ - Kết quả realtime│        │
│  └──────────────────┘      └──────────────────┘        │
│           │                          │                    │
│           └──────────┬──────────────┘                    │
│                      │                                     │
│           ┌─────────▼─────────┐                           │
│           │  YOLO Model      │                           │
│           │  (best5n.pt)     │                           │
│           └─────────┬─────────┘                           │
│                      │                                     │
│           ┌─────────▼─────────┐                           │
│           │  Telegram Bot     │                           │
│           │  (Gửi cảnh báo)   │                           │
│           └───────────────────┘                           │
└─────────────────────────────────────────────────────────┘
```

### Các thành phần chính

1. **GUI Application (simple_app.py)**
   - Giao diện người dùng với 2 tab
   - Quản lý dữ liệu vật thể
   - Điều khiển nhận diện video
   - Cấu hình Telegram

2. **YOLO Detection Engine**
   - Load model từ file `.pt`
   - Xử lý frame video
   - Vẽ bounding boxes
   - Đếm số lượng vật thể

3. **Telegram Notification System**
   - Gửi cảnh báo khi phát hiện vấn đề
   - Gửi báo cáo định kỳ
   - Quản lý cooldown để tránh spam

---

## 📁 CẤU TRÚC THƯ MỤC VÀ FILE

```
DetectB501/
│
├── 📄 simple_app.py              # File chính - GUI ứng dụng
├── 📄 detect_video.py             # Script nhận diện video độc lập
├── 📄 detect_image.py             # Script nhận diện ảnh
├── 📄 send_tele.py                # Script gửi Telegram độc lập
├── 📄 testmodel.py                # Script test model
│
├── 📁 model/                      # Thư mục chứa model YOLO
│   ├── best5n.pt                  # Model chính (được sử dụng)
│   ├── best (1).pt                # Model backup
│   ├── last.pt                    # Model checkpoint cuối
│   └── last5n.pt                  # Model checkpoint cuối (5n)
│
├── 📄 objects_data.json           # Danh sách vật thể cần theo dõi
├── 📄 result_count.json           # Kết quả nhận diện (tự động tạo)
│
├── 📄 requirements.txt             # Dependencies Python
├── 📄 README.md                    # Hướng dẫn sử dụng
├── 📄 HUONG_DAN.md                 # Hướng dẫn chi tiết (file này)
│
├── 📄 start_simple.bat            # Script khởi chạy (Windows)
├── 📄 start_simple.sh             # Script khởi chạy (Linux/Mac)
├── 📄 activate_env.bat            # Kích hoạt virtual environment
│
├── 📁 venv/                       # Virtual environment (nếu có)
└── 📁 __pycache__/                # Python cache files
```

### Mô tả các file quan trọng

#### 1. `simple_app.py (850 dòng)`
**File chính của ứng dụng**

**Chức năng:**
- Tạo giao diện GUI với 2 tab
- Quản lý danh sách vật thể (CRUD)
- Điều khiển nhận diện video real-time
- Tích hợp Telegram bot
- Hiển thị kết quả nhận diện

**Các class và method chính:**
- `SimpleObjectManager`: Class chính quản lý toàn bộ ứng dụng
  - `create_widgets()`: Tạo giao diện
  - `create_tab1_widgets()`: Tạo tab quản lý vật thể
  - `create_tab2_widgets()`: Tạo tab nhận diện video
  - `add_object()`: Thêm vật thể mới
  - `edit_object()`: Sửa vật thể
  - `delete_object()`: Xóa vật thể
  - `start_detection()`: Bắt đầu nhận diện
  - `stop_detection()`: Dừng nhận diện
  - `detection_loop()`: Vòng lặp nhận diện (chạy trong thread)
  - `check_and_send_telegram()`: Logic gửi Telegram thông minh
  - `send_telegram_message()`: Gửi tin nhắn
  - `send_telegram_document()`: Gửi file JSON

**Các biến quan trọng:**
- `self.objects`: Danh sách vật thể trong memory
- `self.expected_objects`: Dictionary vật thể mong đợi
- `self.detected_counts`: Dictionary số lượng vật thể phát hiện được
- `self.model`: YOLO model object
- `self.telegram_enabled`: Trạng thái bật/tắt Telegram
- `self.telegram_cooldown`: Thời gian chờ giữa các tin nhắn (giây)
- `self.telegram_periodic_interval`: Khoảng thời gian gửi định kỳ (giây)

#### 2. `objects_data.json`
**File lưu trữ danh sách vật thể**

**Định dạng:**
```json
[
  {
    "id": 1,
    "name": "Hop",
    "expected_count": 20,
    "description": "Hộp carton",
    "created_at": "04/10/2025 17:17:27"
  },
  {
    "id": 2,
    "name": "Robot",
    "expected_count": 6,
    "description": "",
    "created_at": "04/10/2025 17:43:34"
  }
]
```

**Cấu trúc:**
- `id`: ID duy nhất của vật thể
- `name`: Tên vật thể (phải khớp với tên class trong model YOLO)
- `expected_count`: Số lượng mong đợi
- `description`: Mô tả (tùy chọn)
- `created_at`: Thời gian tạo

#### 3. `result_count.json`
**File kết quả nhận diện (tự động tạo)**

**Định dạng:**
```json
[
  {
    "object_name": "hop",
    "expected_count": 20,
    "detected_count": 16,
    "status": "thiếu",
    "difference": 4
  },
  {
    "object_name": "robot",
    "expected_count": 6,
    "detected_count": 4,
    "status": "thiếu",
    "difference": 2
  }
]
```

**Cấu trúc:**
- `object_name`: Tên vật thể (chữ thường)
- `expected_count`: Số lượng mong đợi
- `detected_count`: Số lượng phát hiện được
- `status`: Trạng thái ("đủ", "thiếu", "thừa")
- `difference`: Số lượng chênh lệch (giá trị tuyệt đối)

#### 4. `detect_video.py`
**Script nhận diện video độc lập (không dùng GUI)**

**Chức năng:**
- Đọc video từ file
- Resize frame về 1080x720
- Chạy YOLO detection
- Ghi kết quả vào `result_count.json`
- Tự động gọi `send_tele.py` để gửi Telegram

**Các hằng số:**
- `MODEL_PATH = "model/best5n.pt"`
- `VIDEO_PATH = "input.mp4"`
- `TARGET_WIDTH = 1080`
- `TARGET_HEIGHT = 720`

#### 5. `send_tele.py`
**Script gửi Telegram độc lập**

**Chức năng:**
- Đọc `result_count.json`
- Tạo message HTML
- Gửi message và file JSON qua Telegram Bot API

**Cấu hình:**
- `TELEGRAM_BOT_TOKEN`: Token của bot
- `TELEGRAM_CHAT_ID`: ID của chat/group nhận tin nhắn

---

## 🔄 LUỒNG HOẠT ĐỘNG

### Luồng chính khi sử dụng GUI

```
1. Khởi động ứng dụng
   └─> simple_app.py
       └─> Load objects_data.json
       └─> Khởi tạo GUI

2. Tab 1: Quản lý vật thể
   ├─> Thêm vật thể mới
   │   └─> Lưu vào objects_data.json
   ├─> Sửa vật thể
   │   └─> Cập nhật objects_data.json
   └─> Xóa vật thể
       └─> Cập nhật objects_data.json

3. Tab 2: Nhận diện video
   ├─> Chọn nguồn (Camera/File)
   ├─> Cấu hình Telegram (nếu cần)
   ├─> Bật Telegram (nếu cần)
   └─> Nhấn "Bắt đầu nhận diện"
       │
       ├─> Load YOLO model (best5n.pt)
       ├─> Mở video source
       └─> Bắt đầu detection thread
           │
           └─> Vòng lặp detection:
               ├─> Đọc frame
               ├─> Resize về 1080x720
               ├─> YOLO detection
               ├─> Đếm vật thể
               ├─> Vẽ bounding boxes
               ├─> Hiển thị trên GUI
               ├─> Kiểm tra và gửi Telegram (nếu cần)
               └─> Lặp lại
```

### Logic gửi Telegram

```
Mỗi 30 frame:
│
├─> Kiểm tra có vấn đề không?
│   ├─> Có thiếu/thừa vật thể?
│   └─> Có thay đổi so với lần trước?
│
├─> Logic gửi:
│   │
│   ├─> 1. Gửi khi phát hiện vấn đề
│   │   ├─> Có vấn đề?
│   │   ├─> Có thay đổi?
│   │   └─> Đã qua cooldown?
│   │       └─> GỬI TIN NHẮN + CẢNH BÁO
│   │
│   └─> 2. Gửi định kỳ
│       ├─> Đã đến thời gian?
│       └─> GỬI BÁO CÁO ĐỊNH KỲ
│
└─> Cập nhật last_detected_counts
```

---

## ⚙️ CẤU HÌNH VÀ THIẾT LẬP

### 1. Cài đặt Dependencies

```bash
# Tạo virtual environment (khuyến nghị)
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Cài đặt packages
pip install -r requirements.txt
```

### 2. Chuẩn bị Model YOLO

- Đặt file model vào thư mục `model/`
- File model mặc định: `model/best5n.pt`
- Model phải được train với các class vật thể cần nhận diện
- Tên class trong model phải khớp với tên trong `objects_data.json` (không phân biệt hoa thường)

### 3. Cấu hình Telegram Bot

#### Bước 1: Tạo Bot
1. Mở Telegram, tìm `@BotFather`
2. Gửi lệnh `/newbot`
3. Đặt tên và username cho bot
4. Lưu lại **Bot Token** (dạng: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### Bước 2: Lấy Chat ID
**Cách 1: Chat cá nhân**
1. Tìm bot vừa tạo
2. Gửi tin nhắn bất kỳ
3. Truy cập: `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Tìm `"chat":{"id":123456789}` - đó là Chat ID

**Cách 2: Group/Channel**
1. Thêm bot vào group/channel
2. Làm admin (nếu cần)
3. Lấy Chat ID tương tự (số âm cho group)

#### Bước 3: Cấu hình trong App
1. Mở ứng dụng
2. Vào Tab 2: Nhận diện video
3. Nhấn "⚙️ Cấu hình"
4. Nhập Bot Token và Chat ID
5. Thiết lập các tham số:
   - **Cooldown**: Thời gian chờ giữa các tin nhắn khi có vấn đề (phút)
   - **Gửi định kỳ**: Khoảng thời gian gửi báo cáo (phút)
   - **Gửi ngay khi phát hiện vấn đề**: Bật/tắt
   - **Gửi tin nhắn định kỳ**: Bật/tắt

### 4. Cấu hình Model và Video

**Trong `simple_app.py`:**
```python
# Dòng 427 (trong start_detection)
model_path = "model/best5n.pt"  # Đổi đường dẫn nếu cần
```

**Kích thước frame:**
```python
# Dòng 513-514 (trong detection_loop)
TARGET_WIDTH = 1080
TARGET_HEIGHT = 720
```

---

## 📖 HƯỚNG DẪN SỬ DỤNG

### Bước 1: Khởi động ứng dụng

**Windows:**
```bash
python simple_app.py
```
hoặc
```bash
start_simple.bat
```

**Linux/Mac:**
```bash
python3 simple_app.py
```
hoặc
```bash
chmod +x start_simple.sh
./start_simple.sh
```

### Bước 2: Quản lý vật thể (Tab 1)

#### Thêm vật thể mới:
1. Nhập **Tên vật thể** (phải khớp với tên class trong model)
2. Nhập **Số lượng mong đợi**
3. Nhập **Mô tả** (tùy chọn)
4. Nhấn "➕ Thêm vật thể"

#### Sửa vật thể:
1. Chọn vật thể trong danh sách
2. Nhấn "✏️ Sửa"
3. Chỉnh sửa thông tin
4. Nhấn "💾 Lưu"

#### Xóa vật thể:
1. Chọn vật thể trong danh sách
2. Nhấn "🗑️ Xóa"
3. Xác nhận xóa

### Bước 3: Nhận diện video (Tab 2)

#### Cấu hình Telegram (tùy chọn):
1. Nhấn "⚙️ Cấu hình"
2. Nhập Bot Token và Chat ID
3. Thiết lập các tham số
4. Nhấn "💾 Lưu"

#### Bắt đầu nhận diện:
1. Chọn nguồn video:
   - **Camera**: Sử dụng webcam (mặc định camera 0)
   - **File video**: Chọn file từ máy tính
2. Bật Telegram (nếu cần): Tick "📱 Bật gửi tin nhắn Telegram"
3. Nhấn "▶ Bắt đầu nhận diện"

#### Trong khi nhận diện:
- Video hiển thị real-time với bounding boxes
- Kết quả đếm hiển thị ở bên phải:
  - ✅ Đủ: Số lượng đúng
  - ❌ Thiếu: Thiếu vật thể
  - ⚠️ Thừa: Thừa vật thể
- FPS và số frame hiển thị ở trên
- Telegram tự động gửi khi:
  - Phát hiện vấn đề (nếu bật)
  - Đến thời gian định kỳ (nếu bật)

#### Dừng nhận diện:
- Nhấn "⏹ Dừng nhận diện"

---

## 🔧 TROUBLESHOOTING

### Lỗi thường gặp

#### 1. "Không tìm thấy model"
**Nguyên nhân:** File model không tồn tại hoặc đường dẫn sai

**Giải pháp:**
- Kiểm tra file `model/best5n.pt` có tồn tại không
- Kiểm tra đường dẫn trong code (dòng 427)

#### 2. "Không thể mở video source"
**Nguyên nhân:** 
- Camera không kết nối
- File video không tồn tại
- File video bị hỏng

**Giải pháp:**
- Kiểm tra camera đã kết nối chưa
- Kiểm tra đường dẫn file video
- Thử file video khác

#### 3. "Không thể gửi Telegram"
**Nguyên nhân:**
- Bot Token sai
- Chat ID sai
- Không có kết nối internet
- Bot chưa được thêm vào group (nếu dùng group)

**Giải pháp:**
- Kiểm tra lại Bot Token và Chat ID
- Kiểm tra kết nối internet
- Thử gửi tin nhắn cho bot trước
- Nếu dùng group, đảm bảo bot đã được thêm vào

#### 4. "Vật thể không được nhận diện"
**Nguyên nhân:**
- Tên vật thể không khớp với tên class trong model
- Model chưa được train với vật thể đó
- Độ tin cậy (confidence) quá thấp

**Giải pháp:**
- Kiểm tra tên vật thể trong `objects_data.json` phải khớp với tên class trong model
- Kiểm tra model đã được train với vật thể đó chưa
- Giảm ngưỡng confidence trong code (dòng 545: `conf=0.5`)

#### 5. "Ứng dụng chạy chậm"
**Nguyên nhân:**
- Model quá lớn
- Video resolution quá cao
- CPU/GPU yếu

**Giải pháp:**
- Sử dụng model nhẹ hơn
- Giảm resolution (TARGET_WIDTH, TARGET_HEIGHT)
- Sử dụng GPU nếu có (CUDA)

#### 6. "Lỗi import module"
**Nguyên nhân:** Thiếu dependencies

**Giải pháp:**
```bash
pip install -r requirements.txt
```

### Tối ưu hiệu suất

1. **Sử dụng GPU:**
   - Cài đặt CUDA và cuDNN
   - PyTorch sẽ tự động sử dụng GPU nếu có

2. **Giảm resolution:**
   - Giảm `TARGET_WIDTH` và `TARGET_HEIGHT`
   - Ví dụ: 640x480 thay vì 1080x720

3. **Tăng confidence threshold:**
   - Tăng `conf` trong `detection_loop()` (dòng 545)
   - Ví dụ: `conf=0.6` thay vì `conf=0.5`

4. **Giảm tần suất kiểm tra Telegram:**
   - Tăng interval kiểm tra (dòng 565: `if self.frame_count % 30`)
   - Ví dụ: `% 60` thay vì `% 30`

---

## 📊 CẤU TRÚC DỮ LIỆU

### objects_data.json
```json
[
  {
    "id": 1,
    "name": "Hop",
    "expected_count": 20,
    "description": "Hộp carton",
    "created_at": "04/10/2025 17:17:27"
  }
]
```

### result_count.json
```json
[
  {
    "object_name": "hop",
    "expected_count": 20,
    "detected_count": 16,
    "status": "thiếu",
    "difference": 4
  }
]
```

---

## 🔐 BẢO MẬT

### Lưu ý quan trọng:
1. **Bot Token**: Không chia sẻ Bot Token công khai
2. **Chat ID**: Bảo mật Chat ID
3. **Model**: Bảo vệ file model nếu là proprietary

### Khuyến nghị:
- Sử dụng file cấu hình riêng cho production
- Không commit Bot Token vào Git
- Sử dụng environment variables cho sensitive data

---

## 📝 GHI CHÚ

- Model YOLO phải được train với dataset phù hợp
- Tên vật thể phải khớp chính xác (không phân biệt hoa thường)
- Hệ thống tự động lưu `result_count.json` mỗi khi gửi Telegram
- Telegram cooldown giúp tránh spam khi có nhiều thay đổi liên tục

---

## 📞 HỖ TRỢ

Nếu gặp vấn đề, vui lòng kiểm tra:
1. Logs trong console
2. File `result_count.json` để xem kết quả
3. Telegram bot có hoạt động không

---

**Phiên bản:** 1.0  
**Cập nhật:** 2025

