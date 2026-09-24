# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 12:20:12 2026

@author: this pc
"""

# -*- coding: utf-8 -*-
import json
import os

class DataManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        """Đọc dữ liệu từ file JSON an toàn."""
        if not os.path.exists(self.file_path):
            return []  # Trả về list rỗng nếu file chưa tồn tại
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # Đảm bảo dữ liệu trả về luôn là list
                return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            print(f"Lỗi: File {self.file_path} sai định dạng. Trả về dữ liệu rỗng.")
            return []
        except Exception as e:
            print(f"Lỗi không xác định khi đọc file: {e}")
            return []

    def save_data(self, data):
        """Ghi đè toàn bộ danh sách dữ liệu vào file JSON."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Lỗi khi lưu file: {e}")
            return False

    def create(self, item_dict):
        """Thêm một đối tượng mới (dạng dict) vào file."""
        data = self.load_data()
        data.append(item_dict)
        return self.save_data(data)

    def find_by_key(self, key, value):
        """Tìm kiếm các đối tượng khớp với 1 thuộc tính (VD: tìm username)."""
        data = self.load_data()
        return [item for item in data if item.get(key) == value]

    def update(self, key, value, new_item_dict):
        """Cập nhật đối tượng dựa trên key định danh."""
        data = self.load_data()
        updated = False
        for i, item in enumerate(data):
            if item.get(key) == value:
                data[i] = new_item_dict
                updated = True
                break
        
        if updated:
            self.save_data(data)
        return updated

    def delete(self, key, value):
        """Xóa đối tượng dựa trên key định danh."""
        data = self.load_data()
        new_data = [item for item in data if item.get(key) != value]
        
        if len(new_data) < len(data):
            self.save_data(new_data)
            return True
        return False