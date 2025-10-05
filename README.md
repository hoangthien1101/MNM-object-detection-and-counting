# 🎯 Quản lý vật thể - Simple Version

Giao diện desktop đơn giản để quản lý danh sách vật thể cần theo dõi. Không cần database, không cần dependencies phức tạp.

## ✨ Tính năng

- 📊 **Quản lý vật thể**: Thêm, sửa, xóa các vật thể cần theo dõi
- 💾 **Lưu trữ đơn giản**: Dữ liệu lưu trong file JSON
- 🖥️ **Giao diện desktop**: Windows Forms với tkinter, thân thiện và dễ sử dụng
- 🚀 **Không cần cài đặt**: Chỉ cần Python và tkinter (có sẵn)
- 📱 **Đa nền tảng**: Chạy được trên Windows, Linux, Mac

## 🏗️ Cấu trúc project

```
DetectB501/
├── simple_app.py         # Ứng dụng desktop chính
├── start_simple.bat      # Script khởi động (Windows)
├── start_simple.sh       # Script khởi động (Linux/Mac)
├── objects_data.json     # File lưu dữ liệu (tự tạo)
├── requirements.txt      # Dependencies (không cần)
└── README.md             # Documentation
```

## 🚀 Cài đặt và sử dụng

### Cách 1: Chạy trực tiếp

```bash
# Windows
python simple_app.py
# hoặc double-click start_simple.bat

# Linux/Mac
python3 simple_app.py
# hoặc
./start_simple.sh
```

### Cách 2: Copy và chạy

1. **Copy folder project** đến máy tính
2. **Mở terminal/command prompt** trong folder
3. **Chạy lệnh**:
   ```bash
   python simple_app.py
   ```

### Yêu cầu hệ thống

- ✅ **Python 3.6+** (có sẵn trên hầu hết hệ thống)
- ✅ **tkinter** (có sẵn với Python)
- ❌ **Không cần cài đặt gì thêm!**

## 🖥️ Sử dụng giao diện

### 1. Thêm vật thể mới
- Nhập tên vật thể (ví dụ: "Sách", "Hộp", "Bằng khen")
- Nhập số lượng mong đợi (ví dụ: 10)
- Thêm mô tả (tùy chọn)
- Nhấn nút "➕ Thêm vật thể"

### 2. Quản lý vật thể
- Xem danh sách tất cả vật thể trong bảng
- Chọn vật thể và nhấn "✏️ Sửa" để chỉnh sửa
- Chọn vật thể và nhấn "🗑️ Xóa" để xóa
- Nhấn "🔄 Làm mới" để cập nhật danh sách
- Tất cả thay đổi được lưu tự động vào file JSON

### 3. Lưu trữ dữ liệu
- Dữ liệu được lưu trong file `objects_data.json`
- Tự động lưu khi thêm/sửa/xóa
- Có thể copy file này để backup hoặc chia sẻ

## 📁 Cấu trúc dữ liệu

### File objects_data.json
```json
[
  {
    "id": 1,
    "name": "Sách",
    "expected_count": 10,
    "description": "Sách giáo khoa lớp 5",
    "created_at": "28/09/2025 12:30:45"
  },
  {
    "id": 2,
    "name": "Bằng khen",
    "expected_count": 5,
    "description": "Bằng khen học sinh giỏi",
    "created_at": "28/09/2025 12:31:20"
  }
]
```

### Các trường dữ liệu
- `id` - ID duy nhất của vật thể
- `name` - Tên vật thể
- `expected_count` - Số lượng mong đợi
- `description` - Mô tả chi tiết
- `created_at` - Thời gian tạo (tự động)

## 🐛 Troubleshooting

### Lỗi tkinter
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# CentOS/RHEL
sudo yum install tkinter

# Windows: tkinter có sẵn với Python
```

### Lỗi Python không tìm thấy
```bash
# Windows
python --version
# Nếu không có, cài đặt Python từ python.org

# Linux/Mac
python3 --version
# Nếu không có, cài đặt Python3
```

### Lỗi file JSON
- Xóa file `objects_data.json` nếu bị lỗi
- Ứng dụng sẽ tạo file mới khi khởi động

## 🔄 Workflow

1. **Chạy app**: `python simple_app.py`
2. **Thêm vật thể**: Nhập thông tin và nhấn "Thêm"
3. **Quản lý**: Sửa/xóa vật thể khi cần
4. **Lưu trữ**: Dữ liệu tự động lưu vào JSON
5. **Backup**: Copy file `objects_data.json` để backup

## 📈 Performance

### Hệ thống yêu cầu tối thiểu
- RAM: 100MB
- CPU: Bất kỳ
- Disk: 1MB (chỉ file Python)
- OS: Windows/Linux/Mac

### Ưu điểm
- ✅ **Siêu nhẹ**: Chỉ cần Python + tkinter
- ✅ **Nhanh**: Khởi động trong 1-2 giây
- ✅ **Đơn giản**: Không cần cài đặt gì
- ✅ **Ổn định**: Ít lỗi, dễ debug

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

