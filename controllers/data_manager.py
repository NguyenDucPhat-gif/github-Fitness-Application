
import json

class DataManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                return data if isinstance(data, list) else []
                
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print(f"Lỗi: File {self.file_path} sai định dạng. Trả về dữ liệu rỗng.")
            return []
        except Exception as e:
            print(f"Lỗi không xác định khi đọc file: {e}")
            return []

    def save_data(self, data):
       
        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Lỗi khi lưu file: {e}")
            return False

    def create(self, item_dict):
       
        data = self.load_data()
        data.append(item_dict)
        return self.save_data(data)

    def find_by_key(self, key, value):
        
        data = self.load_data()
        return [item for item in data if item.get(key) == value]

    def update(self, key, value, new_item_dict):
        
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
        
        data = self.load_data()
        new_data = [item for item in data if item.get(key) != value]
        
        if len(new_data) < len(data):
            self.save_data(new_data)
            return True
        return False