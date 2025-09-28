#!/usr/bin/env python3
"""
Simple Desktop App - Giao diện quản lý vật thể đơn giản
Không sử dụng database, chỉ lưu trong memory
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class SimpleObjectManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản lý vật thể - Simple Version")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Danh sách vật thể trong memory
        self.objects = []
        self.load_data()
        
        # Tạo giao diện
        self.create_widgets()
        
    def create_widgets(self):
        """Tạo giao diện chính"""
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text="🎯 QUẢN LÝ VẬT THỂ", 
                 font=('Arial', 16, 'bold')).pack()
        ttk.Label(header_frame, text="Thêm, sửa, xóa các vật thể cần theo dõi", 
                 font=('Arial', 10)).pack()
        
        # Frame thêm vật thể
        add_frame = ttk.LabelFrame(self.root, text="Thêm vật thể mới")
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
        list_frame = ttk.LabelFrame(self.root, text="Danh sách vật thể")
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview
        columns = ('ID', 'Tên', 'Số lượng', 'Mô tả', 'Ngày tạo')
        self.objects_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
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
        self.edit_btn.pack(side='left', padx=5)
        
        self.delete_btn = ttk.Button(control_frame, text="🗑️ Xóa", command=self.delete_object, state='disabled')
        self.delete_btn.pack(side='left', padx=5)
        
        self.refresh_btn = ttk.Button(control_frame, text="🔄 Làm mới", command=self.refresh_list)
        self.refresh_btn.pack(side='left', padx=5)
        
        # Bind selection event
        self.objects_tree.bind('<<TreeviewSelect>>', self.on_object_select)
        
        # Load dữ liệu
        self.refresh_list()
    
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
            'id': len(self.objects) + 1,
            'name': name,
            'expected_count': count,
            'description': description,
            'created_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        self.objects.append(new_object)
        self.save_data()
        self.refresh_list()
        
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
            self.save_data()
            self.refresh_list()
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
    
    def on_closing(self):
        """Xử lý khi đóng ứng dụng"""
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
    main()
