# 🎯 HỆ THỐNG GIÁM SÁT VÀ NHẬN DIỆN VẬT THỂ TỰ ĐỘNG

## 📱 DetectB501 - Ứng dụng Quản lý Vật thể & Nhận diện YOLO

Hệ thống giám sát thông minh sử dụng công nghệ YOLO để nhận diện và đếm vật thể tự động, tích hợp thông báo qua Telegram Bot.

---

## ✨ TÍNH NĂNG CHÍNH

### 🎨 Giao diện Người dùng Thân thiện
- **Tab Quản lý Vật thể**: Thêm, sửa, xóa danh sách vật thể cần theo dõi
- **Tab Nhận diện Video**: Xem video real-time với kết quả nhận diện trực tiếp
- Hiển thị kết quả đếm với biểu tượng trực quan (✅ đủ, ❌ thiếu)

### 🤖 Nhận diện Thông minh
- Nhận diện vật thể real-time từ **camera** hoặc **file video**
- Sử dụng mô hình YOLO đã được train sẵn
- Tự động resize frame về 1080x720 để tối ưu hiệu suất
- Hiển thị bounding boxes và FPS trên video

### 📱 Thông báo Telegram Tự động
- **Gửi cảnh báo ngay** khi phát hiện thiếu vật thể
- **Báo cáo định kỳ** để theo dõi trạng thái liên tục
- **Cooldown thông minh** để tránh spam tin nhắn
- Gửi kèm file JSON chi tiết kết quả

### 💾 Quản lý Dữ liệu
- Lưu trữ danh sách vật thể trong file JSON
- Tự động tạo file kết quả nhận diện
- Dễ dàng backup và restore dữ liệu

---

## 🚀 CÀI ĐẶT NHANH

### Yêu cầu Hệ thống
- **Python**: 3.8 - 3.10
- **Hệ điều hành**: Windows / Linux / macOS
- **RAM**: Tối thiểu 4GB (khuyến nghị 8GB)
- **GPU**: Tùy chọn (hỗ trợ CUDA để tăng tốc)

### Bước 1: Clone hoặc Tải Project
```bash
# Nếu có Git
git clone <repository-url>
cd DetectB501

# Hoặc tải và giải nén file ZIP
```

### Bước 2: Tạo Virtual Environment (Khuyến nghị)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài đặt Dependencies
```bash
pip install -r requirements.txt
```

### Bước 4: Chuẩn bị Model YOLO
- Đặt file model vào thư mục `model/`
- File model mặc định: `model/best5n.pt`
- Đảm bảo model đã được train với các vật thể cần nhận diện

### Bước 5: Khởi động Ứng dụng
```bash
# Windows
python simple_app.py
# hoặc
start_simple.bat

# Linux/Mac
python3 simple_app.py
# hoặc
chmod +x start_simple.sh
./start_simple.sh
```

---

## 📖 HƯỚNG DẪN SỬ DỤNG

### 🎯 Bước 1: Quản lý Danh sách Vật thể

1. **Mở Tab "📋 Quản lý vật thể"**

2. **Thêm vật thể mới:**
   - Nhập **Tên vật thể** (phải khớp với tên class trong model YOLO)
   - Nhập **Số lượng mong đợi**
   - Nhập **Mô tả** (tùy chọn)
   - Nhấn **"➕ Thêm vật thể"**

3. **Sửa vật thể:**
   - Chọn vật thể trong danh sách
   - Nhấn **"✏️ Sửa"**
   - Chỉnh sửa thông tin
   - Nhấn **"💾 Lưu"**

4. **Xóa vật thể:**
   - Chọn vật thể trong danh sách
   - Nhấn **"🗑️ Xóa"**
   - Xác nhận xóa

> **Lưu ý:** Tên vật thể phải khớp chính xác với tên class trong model YOLO (không phân biệt hoa thường)

### 🎥 Bước 2: Cấu hình Telegram (Tùy chọn)

1. **Tạo Telegram Bot:**
   - Mở Telegram, tìm `@BotFather`
   - Gửi lệnh `/newbot` và làm theo hướng dẫn
   - Lưu lại **Bot Token**

2. **Lấy Chat ID:**
   - Gửi tin nhắn cho bot vừa tạo
   - Truy cập: `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Tìm `"chat":{"id":123456789}` - đó là Chat ID
   - Đối với group: Chat ID là số âm

3. **Cấu hình trong App:**
   - Vào Tab **"🎥 Nhận diện video"**
   - Nhấn **"⚙️ Cấu hình"**
   - Nhập **Bot Token** và **Chat ID**
   - Thiết lập:
     - **Cooldown**: Thời gian chờ giữa các tin nhắn khi có vấn đề (phút)
     - **Gửi định kỳ**: Khoảng thời gian gửi báo cáo (phút)
     - **Gửi ngay khi phát hiện vấn đề**: Bật/tắt
     - **Gửi tin nhắn định kỳ**: Bật/tắt
   - Nhấn **"💾 Lưu"**

### 🎬 Bước 3: Bắt đầu Nhận diện

1. **Chọn nguồn video:**
   - **Camera**: Sử dụng webcam (mặc định camera 0)
   - **File video**: Nhấn **"📁 Chọn file"** để chọn video từ máy tính

2. **Bật Telegram (nếu cần):**
   - Tick vào **"📱 Bật gửi tin nhắn Telegram"**

3. **Bắt đầu:**
   - Nhấn **"▶ Bắt đầu nhận diện"**
   - Đợi model load (lần đầu có thể mất vài giây)

4. **Xem kết quả:**
   - Video hiển thị real-time với bounding boxes
   - Kết quả đếm hiển thị ở bên phải:
     - ✅ **Đủ**: Số lượng đúng như mong đợi
     - ❌ **Thiếu**: Thiếu vật thể (hiển thị số lượng thiếu)
   - FPS và số frame hiển thị ở trên

5. **Dừng nhận diện:**
   - Nhấn **"⏹ Dừng nhận diện"**

### 📱 Nhận Thông báo Telegram

Hệ thống tự động gửi tin nhắn khi:

- **Phát hiện vấn đề:**
  - Khi phát hiện thiếu hoặc thừa vật thể
  - Chỉ gửi khi có thay đổi so với lần trước
  - Có cooldown để tránh spam
  - Tin nhắn có cảnh báo **🚨 CẢNH BÁO: Phát hiện vấn đề!**

- **Báo cáo định kỳ:**
  - Gửi theo khoảng thời gian đã cấu hình
  - Báo cáo trạng thái hiện tại dù có vấn đề hay không

**Nội dung tin nhắn bao gồm:**
- Thời gian gửi
- Số frame hiện tại
- Danh sách vật thể với trạng thái chi tiết
- File JSON đính kèm với kết quả đầy đủ

---

## 📁 CẤU TRÚC PROJECT

```
DetectB501/
├── simple_app.py              # Ứng dụng chính (GUI)
├── detect_video.py            # Script nhận diện độc lập
├── send_tele.py               # Script gửi Telegram độc lập
├── model/                     # Thư mục chứa model YOLO
│   └── best5n.pt             # Model chính
├── objects_data.json          # Danh sách vật thể
├── result_count.json          # Kết quả nhận diện (tự động)
├── requirements.txt           # Dependencies
└── README.md                 # File này
```

---

## ⚙️ CẤU HÌNH NÂNG CAO

### Thay đổi Model
Sửa trong `simple_app.py` (dòng 427):
```python
model_path = "model/ten_model_cua_ban.pt"
```

### Thay đổi Kích thước Frame
Sửa trong `simple_app.py` (dòng 513-514):
```python
TARGET_WIDTH = 1080   # Độ rộng
TARGET_HEIGHT = 720   # Độ cao
```

### Thay đổi Ngưỡng Confidence
Sửa trong `simple_app.py` (dòng 545):
```python
results = self.model(resized_frame, conf=0.5, verbose=False)
# Tăng lên 0.6 hoặc 0.7 để chính xác hơn (ít false positive)
# Giảm xuống 0.3 hoặc 0.4 để nhạy hơn (nhiều detection hơn)
```

---

## 🔧 XỬ LÝ SỰ CỐ

### ❌ "Không tìm thấy model"
- Kiểm tra file `model/best5n.pt` có tồn tại không
- Kiểm tra đường dẫn trong code

### ❌ "Không thể mở video source"
- Kiểm tra camera đã kết nối chưa
- Kiểm tra đường dẫn file video
- Thử file video khác

### ❌ "Không thể gửi Telegram"
- Kiểm tra Bot Token và Chat ID
- Kiểm tra kết nối internet
- Đảm bảo bot đã được thêm vào group (nếu dùng group)

### ❌ "Vật thể không được nhận diện"
- Kiểm tra tên vật thể khớp với tên class trong model
- Kiểm tra model đã được train với vật thể đó chưa
- Giảm ngưỡng confidence nếu cần

### ⚡ Ứng dụng chạy chậm
- Sử dụng model nhẹ hơn
- Giảm resolution (TARGET_WIDTH, TARGET_HEIGHT)
- Sử dụng GPU nếu có

---

## 📊 VÍ DỤ SỬ DỤNG

### Kịch bản 1: Giám sát Kho hàng
1. Thêm các vật thể: "Hop", "Vali", "Robot"
2. Đặt số lượng mong đợi cho từng vật thể
3. Bật camera hướng vào khu vực kho
4. Bật Telegram để nhận cảnh báo
5. Hệ thống tự động phát hiện và báo cáo khi thiếu/thừa

### Kịch bản 2: Kiểm tra Sản phẩm
1. Thêm các vật thể cần kiểm tra
2. Chọn file video từ camera an ninh
3. Chạy nhận diện và xem kết quả
4. Nhận báo cáo qua Telegram

---

## 📝 LƯU Ý QUAN TRỌNG

1. **Tên vật thể** phải khớp chính xác với tên class trong model YOLO
2. **Model** phải được train với dataset phù hợp
3. **Bot Token** không nên chia sẻ công khai
4. Hệ thống tự động lưu `result_count.json` mỗi khi gửi Telegram
5. Cooldown giúp tránh spam khi có nhiều thay đổi liên tục

---

## 📚 TÀI LIỆU THAM KHẢO

- **Hướng dẫn chi tiết**: Xem file `HUONG_DAN.md`
- **YOLO Documentation**: https://docs.ultralytics.com/
- **Telegram Bot API**: https://core.telegram.org/bots/api

---

## 🆘 HỖ TRỢ

Nếu gặp vấn đề:
1. Kiểm tra logs trong console
2. Xem file `result_count.json` để kiểm tra kết quả
3. Kiểm tra Telegram bot có hoạt động không
4. Xem file `HUONG_DAN.md` để biết thêm chi tiết

---

## 📄 LICENSE

Project này được phát triển cho mục đích học tập và nghiên cứu.

---

**Phiên bản:** 1.0  
**Cập nhật:** 2025  
**Tác giả:** 5N Team

---

## 🎉 CẢM ƠN ĐÃ SỬ DỤNG!

Nếu thấy hữu ích, hãy ⭐ star project này!
