import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import sys
import threading
import time
from datetime import datetime
import cv2
from PIL import Image, ImageTk
from ultralytics import YOLO
import requests


class SimpleObjectManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản lý vật thể & Nhận diện YOLO")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Danh sách vật thể trong memory
        self.objects = []
        self.load_data()
        
        # Biến cho video detection
        self.video_cap = None
        self.is_detecting = False
        self.detection_thread = None
        self.model = None
        self.current_frame = None
        self.fps = 0
        self.frame_count = 0
        self.detected_counts = {}
        self.expected_objects = {}
        self.update_expected_objects()
        
        # Biến cho mượn/trả vật thể
        self.borrow_records = []
        self.borrow_tree = None
        self.borrow_return_btn = None
        self.borrow_file = "borrow_records.json"
        self.load_borrow_data()
        
        # Chuẩn hoá ID sau khi đã load cả objects và borrow_records
        self.normalize_object_ids()
        
        # Biến cho Telegram
        self.telegram_enabled = False
        self.telegram_bot_token = "8483157815:AAFazLwGgzjUCR1l99SeNpFagXq0PrvySKM"
        self.telegram_chat_id = "-5064417328"
        self.last_telegram_send_time = 0
        self.last_detected_counts = {}
        self.telegram_cooldown = 300  # 5 phút cooldown mặc định
        self.telegram_periodic_interval = 1800  # 30 phút gửi định kỳ
        self.last_periodic_send_time = 0
        self.telegram_send_on_issue = True  # Gửi ngay khi có vấn đề
        self.telegram_send_periodic = True  # Gửi định kỳ
        # Vùng ROI (Region of Interest) để chỉ nhận diện trong vùng này
        # roi_canvas_coords: (x1, y1, x2, y2) in canvas coordinates (displayed image area)
        # roi_frame_coords: (x1, y1, x2, y2) in current frame coordinates (same space as model outputs)
        self.roi_canvas_coords = None
        self.roi_frame_coords = None
        self.roi_rect_id = None
        self.drawing_roi = False
        
        # Tạo giao diện
        self.create_widgets()
        
    def create_widgets(self):
        """Tạo giao diện chính với tabs"""
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text="🎯 QUẢN LÝ VẬT THỂ & NHẬN DIỆN YOLO", 
                 font=('Arial', 16, 'bold')).pack()
        
        # Tạo Notebook (Tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Tab 1: Quản lý vật thể
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="📋 Quản lý vật thể")
        self.create_tab1_widgets()
        
        # Tab 2: Nhận diện video
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="🎥 Nhận diện video")
        self.create_tab2_widgets()
        
        # Tab 3: Mượn/Trả vật thể
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="🔄 Mượn/Trả vật thể")
        self.create_tab3_widgets()
    
    def create_tab1_widgets(self):
        """Tạo giao diện Tab 1: Quản lý vật thể"""
        # Frame thêm vật thể
        add_frame = ttk.LabelFrame(self.tab1, text="Thêm vật thể mới")
        add_frame.pack(fill='x', padx=10, pady=5)
        
        # Tên vật thể
        ttk.Label(add_frame, text="Tên vật thể:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(add_frame, textvariable=self.name_var, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Số lượng mong đợi
        ttk.Label(add_frame, text="Số lượng mong đợi:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.count_var = tk.IntVar(value=1)
        self.count_spinbox = ttk.Spinbox(add_frame, from_=1, to=100, textvariable=self.count_var, width=10)
        self.count_spinbox.grid(row=0, column=3, padx=5, pady=5)
        
        # Mô tả
        ttk.Label(add_frame, text="Mô tả:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.desc_var = tk.StringVar()
        self.desc_entry = ttk.Entry(add_frame, textvariable=self.desc_var, width=50)
        self.desc_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5)
        
        # Nút thêm
        self.add_btn = ttk.Button(add_frame, text="➕ Thêm vật thể", command=self.add_object)
        self.add_btn.grid(row=1, column=3, padx=5, pady=5)
        
        # Frame danh sách vật thể
        list_frame = ttk.LabelFrame(self.tab1, text="Danh sách vật thể")
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview
        columns = ('ID', 'Tên', 'Số lượng', 'Mô tả', 'Ngày tạo')
        self.objects_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Cấu hình columns
        for col in columns:
            self.objects_tree.heading(col, text=col)
            self.objects_tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.objects_tree.yview)
        self.objects_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview và scrollbar
        self.objects_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Frame nút điều khiển
        control_frame = ttk.Frame(list_frame)
        control_frame.pack(side='bottom', fill='x', pady=5)
        
        self.edit_btn = ttk.Button(control_frame, text="✏️ Sửa", command=self.edit_object, state='disabled')
        self.edit_btn.pack(fill='x', padx=5, pady=2, anchor='w')
        
        self.delete_btn = ttk.Button(control_frame, text="🗑️ Xóa", command=self.delete_object, state='disabled')
        self.delete_btn.pack(fill='x', padx=5, pady=2, anchor='w')
        
        self.refresh_btn = ttk.Button(control_frame, text="🔄 Làm mới", command=self.refresh_list)
        self.refresh_btn.pack(fill='x', padx=5, pady=2, anchor='w')
        
        # Bind selection event
        self.objects_tree.bind('<<TreeviewSelect>>', self.on_object_select)
        
        # Load dữ liệu
        self.refresh_list()
    
    def create_tab2_widgets(self):
        """Tạo giao diện Tab 2: Nhận diện video"""
        # Frame điều khiển
        control_frame = ttk.LabelFrame(self.tab2, text="Điều khiển")
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # Chọn nguồn video
        source_frame = ttk.Frame(control_frame)
        source_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(source_frame, text="Nguồn video:").pack(side='left', padx=5)
        self.video_source_var = tk.StringVar(value="camera")
        ttk.Radiobutton(source_frame, text="Camera", variable=self.video_source_var, 
                       value="camera").pack(side='left', padx=5)
        ttk.Radiobutton(source_frame, text="File video", variable=self.video_source_var, 
                       value="file").pack(side='left', padx=5)
        
        self.video_file_var = tk.StringVar(value="input2.mp4")
        ttk.Entry(source_frame, textvariable=self.video_file_var, width=30).pack(side='left', padx=5)
        ttk.Button(source_frame, text="📁 Chọn file", 
                  command=self.browse_video_file).pack(side='left', padx=5)
        
        # Nút điều khiển
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        self.start_detect_btn = ttk.Button(button_frame, text="▶ Bắt đầu nhận diện", 
                                           command=self.start_detection, state='normal')
        self.start_detect_btn.pack(side='left', padx=5)
        
        self.stop_detect_btn = ttk.Button(button_frame, text="⏹ Dừng nhận diện", 
                                          command=self.stop_detection, state='disabled')
        self.stop_detect_btn.pack(side='left', padx=5)
        
        # Frame cấu hình Telegram
        telegram_config_frame = ttk.LabelFrame(self.tab2, text="Cấu hình Telegram")
        telegram_config_frame.pack(fill='x', padx=10, pady=5)
        
        # Bật/tắt Telegram
        telegram_enable_frame = ttk.Frame(telegram_config_frame)
        telegram_enable_frame.pack(fill='x', padx=5, pady=5)
        
        self.telegram_enable_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(telegram_enable_frame, text="📱 Bật gửi tin nhắn Telegram", 
                       variable=self.telegram_enable_var,
                       command=self.toggle_telegram).pack(side='left', padx=5)
        
        ttk.Button(telegram_enable_frame, text="⚙️ Cấu hình", 
                  command=self.config_telegram).pack(side='left', padx=5)
        
        # Thông tin Telegram
        self.telegram_status_label = ttk.Label(telegram_enable_frame, 
                                              text="Telegram: Tắt", 
                                              foreground='gray')
        self.telegram_status_label.pack(side='left', padx=10)
        
        # Tạo PanedWindow để chia không gian giữa video và kết quả
        main_paned = ttk.PanedWindow(self.tab2, orient='horizontal')
        main_paned.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Frame hiển thị video (bên trái)
        video_frame = ttk.LabelFrame(main_paned, text="Video nhận diện")
        main_paned.add(video_frame, weight=1)
        
        # Canvas để hiển thị video (kích thước nhỏ hơn)
        self.video_canvas = tk.Canvas(video_frame, bg='black', width=640, height=360)
        self.video_canvas.pack(fill='both', expand=True, padx=5, pady=5)
        # Bind canvas mouse events for ROI drawing
        self.video_canvas.bind('<ButtonPress-1>', self.on_canvas_button_press)
        self.video_canvas.bind('<B1-Motion>', self.on_canvas_motion)
        self.video_canvas.bind('<ButtonRelease-1>', self.on_canvas_button_release)
        
        # Frame thông tin (bên phải)
        info_frame = ttk.LabelFrame(main_paned, text="Kết quả nhận diện")
        main_paned.add(info_frame, weight=1)
        
        # Label hiển thị FPS và số lượng vật thể
        self.info_label = ttk.Label(info_frame, text="FPS: 0.00 | Chưa bắt đầu nhận diện", 
                                   font=('Arial', 10, 'bold'))
        self.info_label.pack(padx=5, pady=5)

        # ROI controls (draw / clear)
        roi_control_frame = ttk.Frame(info_frame)
        roi_control_frame.pack(fill='x', padx=5, pady=2)

        self.draw_roi_btn = ttk.Button(roi_control_frame, text="✏️ Vẽ vùng ROI", command=self.start_draw_roi)
        self.draw_roi_btn.pack(side='left', padx=5)

        self.clear_roi_btn = ttk.Button(roi_control_frame, text="❌ Xóa vùng ROI", command=self.clear_roi)
        self.clear_roi_btn.pack(side='left', padx=5)

        self.roi_status_label = ttk.Label(roi_control_frame, text="ROI: Không", foreground='gray')
        self.roi_status_label.pack(side='left', padx=8)
        
        # Text widget hiển thị kết quả đếm (lớn hơn)
        result_frame = ttk.Frame(info_frame)
        result_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.result_text = tk.Text(result_frame, height=20, wrap='word', state='disabled',
                                  font=('Arial', 11))
        result_scrollbar = ttk.Scrollbar(result_frame, orient='vertical', 
                                         command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        self.result_text.pack(side='left', fill='both', expand=True)
        result_scrollbar.pack(side='right', fill='y')
    
    def create_tab3_widgets(self):
        """Tạo giao diện Tab 3: Mượn/Trả vật thể"""
        main_frame = ttk.Frame(self.tab3)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Khối mượn vật thể
        borrow_frame = ttk.LabelFrame(main_frame, text="Mượn vật thể")
        borrow_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(borrow_frame, text="Vật thể:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.borrow_object_var = tk.StringVar()
        object_names = [obj['name'] for obj in self.objects]
        self.borrow_object_combo = ttk.Combobox(
            borrow_frame, textvariable=self.borrow_object_var, values=object_names, state='readonly', width=30
        )
        self.borrow_object_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(borrow_frame, text="Số lượng:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.borrow_quantity_var = tk.IntVar(value=1)
        ttk.Spinbox(borrow_frame, from_=1, to=100, textvariable=self.borrow_quantity_var, width=10).grid(
            row=0, column=3, padx=5, pady=5
        )

        ttk.Label(borrow_frame, text="Người mượn:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.borrower_name_var = tk.StringVar()
        ttk.Entry(borrow_frame, textvariable=self.borrower_name_var, width=30).grid(
            row=1, column=1, padx=5, pady=5
        )

        ttk.Label(borrow_frame, text="Ghi chú:").grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.borrow_note_var = tk.StringVar()
        ttk.Entry(borrow_frame, textvariable=self.borrow_note_var, width=30).grid(
            row=1, column=3, padx=5, pady=5
        )

        ttk.Button(borrow_frame, text="📦 Mượn", command=self.borrow_object).grid(
            row=2, column=0, columnspan=4, pady=10
        )

        # Danh sách mượn
        list_frame = ttk.LabelFrame(main_frame, text="Danh sách mượn/trả")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)

        columns = ("ID", "Vật thể", "Số lượng", "Người mượn", "Ngày mượn", "Ghi chú", "Trạng thái")
        self.borrow_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        for col in columns:
            self.borrow_tree.heading(col, text=col)
            if col == "Ghi chú":
                self.borrow_tree.column(col, width=180)
            elif col == "Trạng thái":
                self.borrow_tree.column(col, width=160)
            else:
                self.borrow_tree.column(col, width=110)
        self.borrow_tree.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.borrow_tree.yview)
        self.borrow_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # Điều khiển trả
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', padx=5, pady=5)

        self.borrow_return_btn = ttk.Button(
            control_frame, text="↩️ Đánh dấu đã trả", command=self.return_borrowed_object, state='disabled'
        )
        self.borrow_return_btn.pack(side='left', padx=5)

        ttk.Button(control_frame, text="🔄 Làm mới", command=self.refresh_borrow_list).pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="🧹 Xóa lịch sử", command=self.clear_borrow_history).pack(side='left', padx=5)

        self.borrow_tree.bind('<<TreeviewSelect>>', self.on_borrow_select)
        self.refresh_borrow_list()
    
    def add_object(self):
        """Thêm vật thể mới"""
        name = self.name_var.get().strip()
        count = self.count_var.get()
        description = self.desc_var.get().strip()
        
        if not name:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên vật thể!")
            return
        
        # Tạo object mới
        new_object = {
            'id': self.get_next_object_id(),
            'name': name,
            'expected_count': count,
            'description': description,
            'created_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        self.objects.append(new_object)
        self.save_data()
        self.refresh_list()
        self.update_expected_objects()  # Cập nhật cho tab 2
        
        # Clear form
        self.name_var.set('')
        self.count_var.set(1)
        self.desc_var.set('')
        
        messagebox.showinfo("Thành công", f"Đã thêm vật thể '{name}' thành công!")
    
    def edit_object(self):
        """Sửa vật thể"""
        selection = self.objects_tree.selection()
        if not selection:
            return
        
        item = self.objects_tree.item(selection[0])
        values = item['values']
        object_id = int(values[0])
        
        # Tìm object trong list
        obj = next((o for o in self.objects if o['id'] == object_id), None)
        if not obj:
            return
        
        # Tạo dialog sửa
        self.edit_dialog(obj)
    
    def edit_dialog(self, obj):
        """Dialog sửa vật thể"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Sửa vật thể")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Variables
        name_var = tk.StringVar(value=obj['name'])
        count_var = tk.IntVar(value=obj['expected_count'])
        desc_var = tk.StringVar(value=obj['description'])
        
        # Widgets
        ttk.Label(dialog, text="Tên vật thể:").grid(row=0, column=0, sticky='w', padx=10, pady=10)
        ttk.Entry(dialog, textvariable=name_var, width=30).grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Số lượng:").grid(row=1, column=0, sticky='w', padx=10, pady=10)
        ttk.Spinbox(dialog, from_=1, to=100, textvariable=count_var, width=10).grid(row=1, column=1, sticky='w', padx=10, pady=10)
        
        ttk.Label(dialog, text="Mô tả:").grid(row=2, column=0, sticky='w', padx=10, pady=10)
        ttk.Entry(dialog, textvariable=desc_var, width=30).grid(row=2, column=1, padx=10, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        def save_changes():
            obj['name'] = name_var.get()
            obj['expected_count'] = count_var.get()
            obj['description'] = desc_var.get()
            
            self.save_data()
            self.refresh_list()
            self.update_expected_objects()  # Cập nhật cho tab 2
            messagebox.showinfo("Thành công", "Đã cập nhật vật thể!")
            dialog.destroy()
        
        ttk.Button(button_frame, text="💾 Lưu", command=save_changes).pack(side='left', padx=10)
        ttk.Button(button_frame, text="❌ Hủy", command=dialog.destroy).pack(side='left', padx=10)
    
    def delete_object(self):
        """Xóa vật thể"""
        selection = self.objects_tree.selection()
        if not selection:
            return
        
        item = self.objects_tree.item(selection[0])
        values = item['values']
        object_id = int(values[0])
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa vật thể '{values[1]}'?"):
            # Xóa object khỏi list
            self.objects = [o for o in self.objects if o['id'] != object_id]
            # Chuẩn hoá lại ID sau khi xóa (1, 2, 3, ...)
            self.normalize_object_ids()
            self.save_data()
            self.save_borrow_data()  # Lưu lại borrow_records với object_id đã cập nhật
            self.refresh_list()
            self.refresh_borrow_list()
            self.update_expected_objects()  # Cập nhật cho tab 2
            messagebox.showinfo("Thành công", "Đã xóa vật thể!")
    
    def on_object_select(self, event):
        """Xử lý khi chọn vật thể"""
        selection = self.objects_tree.selection()
        if selection:
            self.edit_btn.config(state='normal')
            self.delete_btn.config(state='normal')
        else:
            self.edit_btn.config(state='disabled')
            self.delete_btn.config(state='disabled')
    
    def update_expected_objects(self):
        """Cập nhật danh sách vật thể mong đợi từ objects_data.json"""
        try:
            if os.path.exists('objects_data.json'):
                with open('objects_data.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.expected_objects = {obj["name"].lower(): obj["expected_count"] for obj in data}
                    if hasattr(self, 'borrow_object_combo') and self.borrow_object_combo:
                        self.borrow_object_combo['values'] = [obj["name"] for obj in data]
        except Exception as e:
            print(f"Lỗi đọc expected objects: {e}")
            self.expected_objects = {}
    
    def browse_video_file(self):
        """Chọn file video"""
        filename = filedialog.askopenfilename(
            title="Chọn file video",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
        )
        if filename:
            self.video_file_var.set(filename)
    
    def toggle_telegram(self):
        """Bật/tắt Telegram"""
        self.telegram_enabled = self.telegram_enable_var.get()
        if self.telegram_enabled:
            self.telegram_status_label.config(text="Telegram: Bật", foreground='green')
        else:
            self.telegram_status_label.config(text="Telegram: Tắt", foreground='gray')

    def on_borrow_select(self, event):
        """Kích hoạt nút trả khi chọn bản ghi"""
        selection = self.borrow_tree.selection()
        if not selection:
            self.borrow_return_btn.config(state='disabled')
            return

        item = self.borrow_tree.item(selection[0])
        borrow_id = item['values'][0]
        record = next((r for r in self.borrow_records if r['id'] == borrow_id), None)
        if record and not record.get('returned', False):
            self.borrow_return_btn.config(state='normal')
        else:
            self.borrow_return_btn.config(state='disabled')

    def refresh_borrow_list(self):
        """Làm mới danh sách mượn/trả"""
        if not self.borrow_tree:
            return

        for item in self.borrow_tree.get_children():
            self.borrow_tree.delete(item)

        for record in sorted(self.borrow_records, key=lambda r: r['id'], reverse=True):
            status = "Đang mượn"
            if record.get('returned', False):
                returned_at = record.get('returned_at') or ""
                status = f"Đã trả ({returned_at})" if returned_at else "Đã trả"

            self.borrow_tree.insert(
                '',
                'end',
                values=(
                    record['id'],
                    record['object_name'],
                    record['quantity'],
                    record.get('borrower', ''),
                    record.get('borrowed_at', ''),
                    record.get('notes', ''),
                    status
                )
            )

        self.borrow_return_btn.config(state='disabled')

    def borrow_object(self):
        """Xử lý mượn vật thể"""
        object_name = self.borrow_object_var.get().strip()
        borrower = self.borrower_name_var.get().strip()
        quantity = self.borrow_quantity_var.get()
        notes = self.borrow_note_var.get().strip()

        if not object_name:
            messagebox.showerror("Lỗi", "Vui lòng chọn vật thể muốn mượn!")
            return

        if quantity <= 0:
            messagebox.showerror("Lỗi", "Số lượng mượn phải lớn hơn 0!")
            return

        obj = next((o for o in self.objects if o['name'].lower() == object_name.lower()), None)
        if not obj:
            messagebox.showerror("Lỗi", "Không tìm thấy vật thể trong danh sách!")
            return

        available = obj.get('expected_count', 0)
        if quantity > available:
            messagebox.showerror(
                "Lỗi",
                f"Số lượng còn lại của '{obj['name']}' chỉ còn {available}. Không thể mượn {quantity}!"
            )
            return

        if not borrower:
            if not messagebox.askyesno("Xác nhận", "Bạn chưa nhập tên người mượn. Vẫn tiếp tục?"):
                return

        record = {
            "id": self.get_next_borrow_id(),
            "object_id": obj['id'],
            "object_name": obj['name'],
            "quantity": quantity,
            "borrower": borrower,
            "notes": notes,
            "borrowed_at": datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            "returned": False,
            "returned_at": None
        }

        self.borrow_records.append(record)
        obj['expected_count'] = available - quantity

        self.save_data()
        self.save_borrow_data()
        self.refresh_list()
        self.refresh_borrow_list()
        self.update_expected_objects()

        messagebox.showinfo("Thành công", f"Đã ghi nhận mượn {quantity} '{obj['name']}'!")

        self.borrow_quantity_var.set(1)
        self.borrow_note_var.set('')

    def return_borrowed_object(self):
        """Đánh dấu trả vật thể"""
        selection = self.borrow_tree.selection()
        if not selection:
            return

        item = self.borrow_tree.item(selection[0])
        borrow_id = item['values'][0]
        record = next((r for r in self.borrow_records if r['id'] == borrow_id), None)

        if not record:
            messagebox.showwarning("Thông báo", "Không tìm thấy bản ghi mượn.")
            return

        if record.get('returned', False):
            messagebox.showinfo("Thông báo", "Bản ghi này đã được trả trước đó.")
            return

        obj = next((o for o in self.objects if o['id'] == record['object_id']), None)

        if not messagebox.askyesno(
            "Xác nhận",
            f"Đánh dấu '{record['object_name']}' (x{record['quantity']}) đã được trả?"
        ):
            return

        record['returned'] = True
        record['returned_at'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        if obj:
            obj['expected_count'] = obj.get('expected_count', 0) + record['quantity']

        self.save_data()
        self.save_borrow_data()
        self.refresh_list()
        self.refresh_borrow_list()
        self.update_expected_objects()

        messagebox.showinfo("Thành công", "Đã đánh dấu trả vật thể!")
    
    def clear_borrow_history(self):
        """Xóa toàn bộ lịch sử mượn/trả"""
        if not self.borrow_records:
            messagebox.showinfo("Thông báo", "Không có lịch sử mượn/trả để xóa.")
            return
        
        # Đếm số bản ghi đang mượn (chưa trả)
        outstanding = [record for record in self.borrow_records if not record.get('returned', False)]
        outstanding_count = len(outstanding)
        
        if outstanding_count > 0:
            msg = f"Bạn có {outstanding_count} vật thể đang mượn chưa trả.\n"
            msg += "Nếu xóa lịch sử, số lượng các vật thể này sẽ được hoàn trả.\n\n"
            msg += "Bạn có chắc muốn xóa toàn bộ lịch sử mượn/trả?"
        else:
            msg = "Bạn có chắc muốn xóa toàn bộ lịch sử mượn/trả?"
        
        if not messagebox.askyesno("Xác nhận", msg):
            return
        
        # Hoàn trả số lượng cho các vật thể đang mượn
        for record in outstanding:
            obj = next((o for o in self.objects if o['id'] == record.get('object_id')), None)
            if obj:
                obj['expected_count'] = obj.get('expected_count', 0) + record['quantity']
        
        # Xóa toàn bộ lịch sử
        self.borrow_records = []
        
        # Lưu lại dữ liệu
        self.save_data()
        self.save_borrow_data()
        self.refresh_list()
        self.refresh_borrow_list()
        self.update_expected_objects()
        
        messagebox.showinfo("Thành công", "Đã xóa toàn bộ lịch sử mượn/trả!")
    
    def config_telegram(self):
        """Cấu hình Telegram bot token và chat ID"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Cấu hình Telegram")
        dialog.geometry("500x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Variables
        token_var = tk.StringVar(value=self.telegram_bot_token)
        chat_id_var = tk.StringVar(value=self.telegram_chat_id)
        cooldown_var = tk.IntVar(value=self.telegram_cooldown // 60)  # Đổi sang phút
        interval_var = tk.IntVar(value=self.telegram_periodic_interval // 60)  # Đổi sang phút
        send_on_issue_var = tk.BooleanVar(value=self.telegram_send_on_issue)
        send_periodic_var = tk.BooleanVar(value=self.telegram_send_periodic)
        
        # Widgets
        ttk.Label(dialog, text="Bot Token:").grid(row=0, column=0, sticky='w', padx=10, pady=10)
        ttk.Entry(dialog, textvariable=token_var, width=50).grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Chat ID:").grid(row=1, column=0, sticky='w', padx=10, pady=10)
        ttk.Entry(dialog, textvariable=chat_id_var, width=50).grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Cooldown (phút):").grid(row=2, column=0, sticky='w', padx=10, pady=10)
        ttk.Spinbox(dialog, from_=1, to=60, textvariable=cooldown_var, width=10).grid(row=2, column=1, sticky='w', padx=10, pady=10)
        ttk.Label(dialog, text="(Thời gian chờ giữa các tin nhắn khi có vấn đề)").grid(row=2, column=1, sticky='e', padx=10)
        
        ttk.Label(dialog, text="Gửi định kỳ (phút):").grid(row=3, column=0, sticky='w', padx=10, pady=10)
        ttk.Spinbox(dialog, from_=5, to=120, textvariable=interval_var, width=10).grid(row=3, column=1, sticky='w', padx=10, pady=10)
        ttk.Label(dialog, text="(Gửi tin nhắn định kỳ)").grid(row=3, column=1, sticky='e', padx=10)
        
        ttk.Checkbutton(dialog, text="Gửi ngay khi phát hiện vấn đề", 
                       variable=send_on_issue_var).grid(row=4, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        
        ttk.Checkbutton(dialog, text="Gửi tin nhắn định kỳ", 
                       variable=send_periodic_var).grid(row=5, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        def save_config():
            self.telegram_bot_token = token_var.get().strip()
            self.telegram_chat_id = chat_id_var.get().strip()
            self.telegram_cooldown = cooldown_var.get() * 60  # Đổi về giây
            self.telegram_periodic_interval = interval_var.get() * 60  # Đổi về giây
            self.telegram_send_on_issue = send_on_issue_var.get()
            self.telegram_send_periodic = send_periodic_var.get()
            
            messagebox.showinfo("Thành công", "Đã lưu cấu hình Telegram!")
            dialog.destroy()
        
        ttk.Button(button_frame, text="💾 Lưu", command=save_config).pack(side='left', padx=10)
        ttk.Button(button_frame, text="❌ Hủy", command=dialog.destroy).pack(side='left', padx=10)
    
    def start_detection(self):
        """Bắt đầu nhận diện video"""
        if self.is_detecting:
            return
        
        # Cập nhật danh sách vật thể mong đợi
        self.update_expected_objects()
        
        # Load model
        try:
            model_path = "model/best8n.pt"
            if not os.path.exists(model_path):
                messagebox.showerror("Lỗi", f"Không tìm thấy model tại: {model_path}")
                return
            self.model = YOLO(model_path)
            print("✓ Đã load model thành công")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể load model: {e}")
            return
        
        # Mở video source
        source = self.video_source_var.get()
        if source == "camera":
            self.video_cap = cv2.VideoCapture(0)
        else:
            video_path = self.video_file_var.get()
            if not os.path.exists(video_path):
                messagebox.showerror("Lỗi", f"Không tìm thấy file video: {video_path}")
                return
            self.video_cap = cv2.VideoCapture(video_path)
        
        if not self.video_cap.isOpened():
            messagebox.showerror("Lỗi", "Không thể mở video source")
            return
        
        # Reset biến Telegram
        self.last_telegram_send_time = 0
        self.last_periodic_send_time = time.time()
        self.last_detected_counts = {}
        
        # Bắt đầu detection thread
        self.is_detecting = True
        self.frame_count = 0
        self.detected_counts = {}
        self.start_detect_btn.config(state='disabled')
        self.stop_detect_btn.config(state='normal')
        
        self.detection_thread = threading.Thread(target=self.detection_loop, daemon=True)
        self.detection_thread.start()
    
    def stop_detection(self):
        """Dừng nhận diện video"""
        self.is_detecting = False
        self.start_detect_btn.config(state='normal')
        self.stop_detect_btn.config(state='disabled')
        
        # Đợi thread detection kết thúc
        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(timeout=1.0)
        
        if self.video_cap:
            self.video_cap.release()
        
        # Xóa video trên canvas
        self.video_canvas.delete("all")
        self.info_label.config(text="Đã dừng nhận diện")
        
        # Hiển thị thông báo kết quả
        result_text = "Đã dừng nhận diện\n\n"
        result_text += "ℹ️ Hệ thống đã dừng nhận diện"
        
        self.result_text.config(state='normal')
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert('1.0', result_text)
        self.result_text.config(state='disabled')
    
    def detection_loop(self):
        """Vòng lặp nhận diện trong thread riêng"""
        TARGET_WIDTH = 1080
        TARGET_HEIGHT = 720
        fps_time = time.time()
        fps_counter = 0
        
        while self.is_detecting:
            ret, frame = self.video_cap.read()
            if not ret:
                if self.video_source_var.get() == "file":
                    # Quay lại đầu video nếu là file
                    self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    break
            
            self.frame_count += 1
            start_time = time.time()
            
            # Resize frame
            resized_frame = cv2.resize(frame, (TARGET_WIDTH, TARGET_HEIGHT), 
                                      interpolation=cv2.INTER_LINEAR)
            
            # Detect objects
            results = self.model(resized_frame, conf=0.5, verbose=False)
            
            # Đếm objects (chỉ chấp nhận detection có độ tin cậy > 0.5)
            frame_detected_counts = {}
            for box in results[0].boxes:
                # Lấy giá trị confidence một cách an toàn (box.conf có thể là scalar hoặc mảng/tensor)
                conf = None
                try:
                    conf = float(box.conf)
                except Exception:
                    try:
                        conf = float(box.conf[0])
                    except Exception:
                        conf = None

                # Bỏ qua các detection không có confidence hợp lệ hoặc <= 0.5
                if conf is None or conf <= 0.5:
                    continue

                # Lấy tọa độ bbox (xyxy) một cách linh hoạt
                try:
                    xyxy = box.xyxy[0]
                    x1, y1, x2, y2 = [float(v) for v in xyxy]
                except Exception:
                    try:
                        # đôi khi .xyxy là list/array
                        x1, y1, x2, y2 = [float(v) for v in box.xyxy]
                    except Exception:
                        try:
                            # fallback dùng xywh
                            xywh = box.xywh[0]
                            cx_b, cy_b, w_b, h_b = [float(v) for v in xywh]
                            x1 = cx_b - w_b / 2.0
                            y1 = cy_b - h_b / 2.0
                            x2 = cx_b + w_b / 2.0
                            y2 = cy_b + h_b / 2.0
                        except Exception:
                            # nếu không lấy được tọa độ, bỏ qua
                            continue

                # Nếu có ROI, chỉ đếm khi tâm bbox nằm trong ROI (ROI tính theo frame coords)
                if self.roi_frame_coords:
                    rx1, ry1, rx2, ry2 = self.roi_frame_coords
                    cx_box = (x1 + x2) / 2.0
                    cy_box = (y1 + y2) / 2.0
                    if not (rx1 <= cx_box <= rx2 and ry1 <= cy_box <= ry2):
                        continue

                cls_id = int(box.cls)
                cls_name = self.model.names[cls_id].lower()
                frame_detected_counts[cls_name] = frame_detected_counts.get(cls_name, 0) + 1
            
            # Cập nhật kết quả cuối cùng
            self.detected_counts = frame_detected_counts.copy()
            
            # Vẽ kết quả
            annotated_frame = results[0].plot()
            
            # Tính FPS
            end_time = time.time()
            frame_time = end_time - start_time
            fps_counter += 1
            if time.time() - fps_time >= 1.0:
                self.fps = fps_counter
                fps_counter = 0
                fps_time = time.time()
            
            # Hiển thị FPS
            cv2.putText(annotated_frame, f"FPS: {self.fps:.1f}", (20, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Kiểm tra và gửi Telegram nếu cần (mỗi 30 frame để không quá tải)
            if self.frame_count % 30 == 0 and self.telegram_enabled:
                self.check_and_send_telegram()
            
            # Cập nhật GUI (phải dùng after để chạy trong main thread)
            self.current_frame = annotated_frame
            self.root.after(0, self.update_video_display)
            
            # Điều chỉnh tốc độ
            time.sleep(max(0, 0.033 - frame_time))  # ~30 FPS
    
    def update_video_display(self):
        """Cập nhật hiển thị video trong GUI"""
        if self.current_frame is None:
            return
        
        # Resize để fit canvas
        canvas_width = self.video_canvas.winfo_width()
        canvas_height = self.video_canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            
            # Resize để fit canvas nhưng giữ tỉ lệ
            frame_h, frame_w = frame_rgb.shape[:2]
            scale = min(canvas_width / frame_w, canvas_height / frame_h)
            new_w = int(frame_w * scale)
            new_h = int(frame_h * scale)
            
            frame_resized = cv2.resize(frame_rgb, (new_w, new_h))
            
            # Convert to PIL Image
            image = Image.fromarray(frame_resized)
            photo = ImageTk.PhotoImage(image=image)
            
            # Update canvas
            self.video_canvas.delete("all")
            self.video_canvas.create_image(canvas_width // 2, canvas_height // 2, 
                                      image=photo, anchor='center')
            self.video_canvas.image = photo  # Keep a reference
            # Nếu đã có ROI được lưu ở canvas coords, vẽ lại và tính ROI theo frame coords
            if getattr(self, 'roi_canvas_coords', None):
                try:
                    # Xóa id cũ nếu tồn tại (thường không vì chúng ta vừa xóa all)
                    if getattr(self, 'roi_rect_id', None):
                        try:
                            self.video_canvas.delete(self.roi_rect_id)
                        except Exception:
                            pass
                    x1_c, y1_c, x2_c, y2_c = self.roi_canvas_coords
                    # vẽ rectangle trên canvas
                    self.roi_rect_id = self.video_canvas.create_rectangle(x1_c, y1_c, x2_c, y2_c,
                                                                            outline='red', width=2)

                    # Tính offset của ảnh trong canvas (ảnh được căn giữa)
                    offset_x = (canvas_width - new_w) / 2.0
                    offset_y = (canvas_height - new_h) / 2.0

                    # Chuyển toạ độ canvas -> toạ độ ảnh (resized frame)
                    img_x1 = x1_c - offset_x
                    img_y1 = y1_c - offset_y
                    img_x2 = x2_c - offset_x
                    img_y2 = y2_c - offset_y

                    # Kiểm tra overlap với ảnh
                    if img_x2 <= 0 or img_y2 <= 0 or img_x1 >= new_w or img_y1 >= new_h:
                        # ROI không nằm trong vùng ảnh
                        self.roi_frame_coords = None
                    else:
                        ix1 = max(0.0, img_x1)
                        iy1 = max(0.0, img_y1)
                        ix2 = min(float(new_w), img_x2)
                        iy2 = min(float(new_h), img_y2)

                        # Chuyển về toạ độ frame gốc (trước khi resize to new_w/new_h)
                        fx1 = int(max(0, min(frame_w - 1, ix1 / scale)))
                        fy1 = int(max(0, min(frame_h - 1, iy1 / scale)))
                        fx2 = int(max(0, min(frame_w - 1, ix2 / scale)))
                        fy2 = int(max(0, min(frame_h - 1, iy2 / scale)))

                        self.roi_frame_coords = (fx1, fy1, fx2, fy2)
                except Exception:
                    # Nếu có lỗi khi tính toán ROI thì đặt thành None
                    self.roi_frame_coords = None
        
        # Cập nhật thông tin
        info_text = f"FPS: {self.fps:.1f} | Frame: {self.frame_count}"
        self.info_label.config(text=info_text)
        
        # # Cập nhật kết quả đếm
        # result_text = "📊 KẾT QUẢ NHẬN DIỆN:\n" + "="*50 + "\n\n"
        # for obj_name, expected_count in self.expected_objects.items():
        #     detected_count = self.detected_counts.get(obj_name, 0)
        #     difference = detected_count - expected_count
            
        #     if difference == 0:
        #         status = f"✅ {obj_name.upper()}: Đủ {expected_count}"
        #     elif difference < 0:
        #         status = f"❌ {obj_name.upper()}: Thiếu {abs(difference)} (có {detected_count}/{expected_count})"
        #     else:
        #         status = f"⚠️ {obj_name.upper()}: Thừa {difference} (có {detected_count}/{expected_count})"
            
        #     result_text += status + "\n"
        # Cập nhật kết quả đếm
        result_text = "📊 KẾT QUẢ NHẬN DIỆN:\n" + "="*50 + "\n\n"
        for obj_name, expected_count in self.expected_objects.items():
            detected_count = self.detected_counts.get(obj_name, 0)

            if detected_count >= expected_count:
                status = f"✅ {obj_name.upper()}: Đủ {expected_count}"
            else:
                status = f"❌ {obj_name.upper()}: Thiếu {expected_count - detected_count} (có {detected_count}/{expected_count})"
            
            result_text += status + "\n"

        
        if not self.expected_objects:
            result_text += "⚠️ Chưa có vật thể nào được cấu hình.\n"
            result_text += "Vui lòng thêm vật thể ở Tab 1: Quản lý vật thể"
        
        # Thêm thông tin Telegram
        if self.telegram_enabled:
            result_text += "\n" + "="*50 + "\n"
            result_text += "📱 Telegram: Đang bật\n"
            time_since_last = time.time() - self.last_telegram_send_time
            if time_since_last < 60:
                result_text += f"⏱️ Lần gửi gần nhất: {int(time_since_last)} giây trước\n"
        
        self.result_text.config(state='normal')
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert('1.0', result_text)
        self.result_text.config(state='disabled')

    # ----------------- ROI drawing handlers -----------------
    def start_draw_roi(self):
        """Bắt đầu chế độ vẽ ROI (một lần): click-drag-release để vẽ vùng"""
        # kích hoạt vẽ, xóa roi cũ
        self.drawing_roi = True
        self.roi_canvas_coords = None
        self.roi_frame_coords = None
        if self.roi_rect_id:
            try:
                self.video_canvas.delete(self.roi_rect_id)
            except Exception:
                pass
            self.roi_rect_id = None
        self.roi_status_label.config(text="ROI: Vẽ...", foreground='orange')

    def clear_roi(self):
        """Xoá vùng ROI hiện tại"""
        self.roi_canvas_coords = None
        self.roi_frame_coords = None
        if getattr(self, 'roi_rect_id', None):
            try:
                self.video_canvas.delete(self.roi_rect_id)
            except Exception:
                pass
            self.roi_rect_id = None
        self.roi_status_label.config(text="ROI: Không", foreground='gray')

    def on_canvas_button_press(self, event):
        if not getattr(self, 'drawing_roi', False):
            return
        # bắt đầu vẽ
        self._roi_start_x = event.x
        self._roi_start_y = event.y
        if self.roi_rect_id:
            try:
                self.video_canvas.delete(self.roi_rect_id)
            except Exception:
                pass
            self.roi_rect_id = None
        self.roi_rect_id = self.video_canvas.create_rectangle(self._roi_start_x, self._roi_start_y,
                                                               event.x, event.y, outline='red', width=2)

    def on_canvas_motion(self, event):
        if not getattr(self, 'drawing_roi', False) or not getattr(self, '_roi_start_x', None):
            return
        x0 = self._roi_start_x
        y0 = self._roi_start_y
        x1 = event.x
        y1 = event.y
        if self.roi_rect_id:
            try:
                self.video_canvas.coords(self.roi_rect_id, x0, y0, x1, y1)
            except Exception:
                pass

    def on_canvas_button_release(self, event):
        if not getattr(self, 'drawing_roi', False):
            return
        x0 = self._roi_start_x
        y0 = self._roi_start_y
        x1 = event.x
        y1 = event.y
        xa, xb = sorted([x0, x1])
        ya, yb = sorted([y0, y1])
        self.roi_canvas_coords = (xa, ya, xb, yb)
        # kết thúc chế độ vẽ (một lần)
        self.drawing_roi = False
        self.roi_status_label.config(text="ROI: Đã đặt", foreground='green')
    
    def save_result_json(self):
        """Lưu kết quả vào file JSON"""
        result_data = []
        for obj_name, expected_count in self.expected_objects.items():
            detected_count = self.detected_counts.get(obj_name, 0)
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
        
        with open("result_count.json", "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=4)
    
    def send_telegram_message(self, message):
        """Gửi text message đến Telegram"""
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print("✓ Đã gửi message đến Telegram")
                return True
            else:
                print(f"✗ Lỗi gửi message: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Exception khi gửi message: {e}")
            return False
    
    def send_telegram_document(self, file_path, caption=""):
        """Gửi file JSON đến Telegram"""
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendDocument"
        try:
            with open(file_path, 'rb') as file:
                files = {'document': file}
                data = {
                    'chat_id': self.telegram_chat_id,
                    'caption': caption
                }
                response = requests.post(url, files=files, data=data, timeout=30)
                if response.status_code == 200:
                    print("✓ Đã gửi file JSON đến Telegram")
                    return True
                else:
                    print(f"✗ Lỗi gửi file: {response.text}")
                    return False
        except Exception as e:
            print(f"✗ Exception khi gửi file: {e}")
            return False
    
    def check_and_send_telegram(self):
        """Kiểm tra và gửi Telegram theo logic thông minh"""
        if not self.telegram_enabled:
            return
        
        current_time = time.time()
        has_issue = False
        issue_changed = False
        
        # Kiểm tra có vấn đề không (thiếu hoặc thừa)
        for obj_name, expected_count in self.expected_objects.items():
            detected_count = self.detected_counts.get(obj_name, 0)
            if detected_count != expected_count:
                has_issue = True
                # Kiểm tra xem có thay đổi so với lần trước không
                last_detected = self.last_detected_counts.get(obj_name, expected_count)
                if detected_count != last_detected:
                    issue_changed = True
                    break
        
        # Logic gửi tin nhắn:
        should_send = False
        send_reason = ""
        
        # 1. Gửi ngay khi phát hiện vấn đề (nếu bật và đã qua cooldown)
        if self.telegram_send_on_issue and has_issue and issue_changed:
            if current_time - self.last_telegram_send_time >= self.telegram_cooldown:
                should_send = True
                send_reason = "phát hiện vấn đề"
        
        # 2. Gửi định kỳ (nếu bật và đã đến thời gian)
        if self.telegram_send_periodic:
            if current_time - self.last_periodic_send_time >= self.telegram_periodic_interval:
                should_send = True
                send_reason = "báo cáo định kỳ"
                self.last_periodic_send_time = current_time
        
        if should_send:
            # Lưu kết quả vào JSON
            self.save_result_json()
            
            # Tạo message
            telegram_message = "🤖 <b>KẾT QUẢ KIỂM ĐẾM ĐỐI TƯỢNG</b>\n"
            telegram_message += f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            telegram_message += f"📊 Frame: {self.frame_count}\n"
            telegram_message += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            for obj_name, expected_count in self.expected_objects.items():
                detected_count = self.detected_counts.get(obj_name, 0)
                difference = detected_count - expected_count
                
                if detected_count >= expected_count:
                    emoji = "✅"
                    telegram_message += f"{emoji} <b>{obj_name.upper()}</b>: Đủ {expected_count}\n"
                else :
                    emoji = "❌"
                    telegram_message += f"{emoji} <b>{obj_name.upper()}</b>: Thiếu {abs(difference)} (có {detected_count}/{expected_count})\n"
                # else:
                #     emoji = "⚠️"
                #     telegram_message += f"{emoji} <b>{obj_name.upper()}</b>: Thừa {difference} (có {detected_count}/{expected_count})\n"

            
            telegram_message += "\n━━━━━━━━━━━━━━━━━━━━━━"
            if send_reason == "phát hiện vấn đề":
                telegram_message += "\n🚨 <b>CẢNH BÁO: Phát hiện vấn đề!</b>"
            
            # Gửi message
            if self.send_telegram_message(telegram_message):
                # Gửi file JSON
                if os.path.exists("result_count.json"):
                    self.send_telegram_document("result_count.json", 
                                              caption="📄 File JSON chi tiết kết quả kiểm đếm")
                
                self.last_telegram_send_time = current_time
                print(f"✓ Đã gửi Telegram ({send_reason})")
        
        # Cập nhật last_detected_counts
        self.last_detected_counts = self.detected_counts.copy()
    
    def refresh_list(self):
        """Làm mới danh sách"""
        # Clear existing items
        for item in self.objects_tree.get_children():
            self.objects_tree.delete(item)
        
        if not self.objects:
            self.objects_tree.insert('', 'end', values=('', 'Chưa có vật thể nào', '', '', ''))
            return
        
        for obj in self.objects:
            self.objects_tree.insert('', 'end', values=(
                obj['id'],
                obj['name'],
                obj['expected_count'],
                obj['description'],
                obj['created_at']
            ))

    def get_next_borrow_id(self):
        """Sinh ID mới cho bản ghi mượn"""
        if not self.borrow_records:
            return 1
        return max(record['id'] for record in self.borrow_records) + 1

    def save_borrow_data(self):
        """Lưu danh sách mượn ra file"""
        try:
            with open(self.borrow_file, 'w', encoding='utf-8') as f:
                json.dump(self.borrow_records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi lưu borrow data: {e}")

    def load_borrow_data(self):
        """Tải danh sách mượn từ file"""
        try:
            if os.path.exists(self.borrow_file):
                with open(self.borrow_file, 'r', encoding='utf-8') as f:
                    self.borrow_records = json.load(f)
            else:
                self.borrow_records = []
        except Exception as e:
            print(f"Lỗi tải borrow data: {e}")
            self.borrow_records = []
    
    def save_data(self):
        """Lưu dữ liệu vào file JSON"""
        try:
            with open('objects_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.objects, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi lưu dữ liệu: {e}")
    
    def load_data(self):
        """Tải dữ liệu từ file JSON"""
        try:
            if os.path.exists('objects_data.json'):
                with open('objects_data.json', 'r', encoding='utf-8') as f:
                    self.objects = json.load(f)
            else:
                self.objects = []
        except Exception as e:
            print(f"Lỗi tải dữ liệu: {e}")
            self.objects = []
    
    def normalize_object_ids(self):
        """Đảm bảo ID vật thể là số nguyên dương và duy nhất, đồng bộ lịch sử mượn"""
        if not self.objects:
            return
        
        # Tạo mapping từ tên vật thể sang ID mới (1, 2, 3, ...)
        name_to_new_id = {}
        for index, obj in enumerate(self.objects, start=1):
            obj['id'] = index
            name_to_new_id[str(obj.get('name', '')).lower()] = index
        
        # Cập nhật object_id trong borrow_records dựa trên tên vật thể
        if self.borrow_records:
            for record in self.borrow_records:
                object_name = str(record.get('object_name', '')).lower()
                if object_name in name_to_new_id:
                    record['object_id'] = name_to_new_id[object_name]
    
    def get_next_object_id(self):
        """Sinh ID mới duy nhất cho vật thể"""
        self.normalize_object_ids()
        if not self.objects:
            return 1
        max_id = max(obj.get('id', 0) for obj in self.objects)
        return max_id + 1
    
    def on_closing(self):
        """Xử lý khi đóng ứng dụng"""
        # Dừng detection nếu đang chạy
        if self.is_detecting:
            self.stop_detection()
        
        self.save_data()
        self.root.destroy()

def main():
    """Hàm main"""
    root = tk.Tk()
    app = SimpleObjectManager(root)
    
    # Xử lý đóng ứng dụng
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Chạy ứng dụng
    root.mainloop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Gracefully handle Ctrl+C in console without stack trace
        pass
