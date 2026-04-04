import json
import os

def load_key(key_file_path):
    """Đọc bộ mật mã từ tệp JSON."""
    try:
        with open(key_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy tệp mã '{key_file_path}'.")
        return None
    except json.JSONDecodeError:
        print(f"Lỗi: Tệp mã '{key_file_path}' không đúng định dạng JSON.")
        return None

def encode_file(input_file_path, output_file_path, key_mapping):
    """Mã hóa nội dung từ tệp đầu vào và lưu vào tệp đầu ra."""
    if not key_mapping:
        return False
    
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f_in:
            content = f_in.read()
        
        # Mã hóa từng ký tự
        encoded_content = "".join(key_mapping.get(char, char) for char in content.lower())
        
        with open(output_file_path, 'w', encoding='utf-8') as f_out:
            f_out.write(encoded_content)
        
        return True
    except Exception as e:
        print(f"Lỗi khi mã hóa: {e}")
        return False

def decode_file(input_file_path, output_file_path, key_mapping):
    """Giải mã nội dung từ tệp đầu vào và lưu vào tệp đầu ra."""
    if not key_mapping:
        return False
    
    # Tạo bộ mã ngược (giá trị -> khóa)
    reverse_mapping = {v: k for k, v in key_mapping.items()}
    
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f_in:
            content = f_in.read()
        
        # Giải mã từng ký tự
        decoded_content = "".join(reverse_mapping.get(char, char) for char in content)
        
        with open(output_file_path, 'w', encoding='utf-8') as f_out:
            f_out.write(decoded_content)
        
        return True
    except Exception as e:
        print(f"Lỗi khi giải mã: {e}")
        return False

def main():
    key_file = "key.json"
    input_file = "input.txt"
    encoded_file = "encoded.txt"
    decoded_file = "decoded_text.txt"

    print("--- CHƯƠNG TRÌNH MÃ HÓA/GIẢI MÃ TẬP TIN ---")
    
    # Tải bộ mật mã
    key = load_key(key_file)
    if not key:
        return

    while True:
        print("\n1. Mã hóa tệp 'input.txt'")
        print("2. Giải mã tệp 'encoded.txt'")
        print("3. Thoát")
        choice = input("Chọn chức năng (1-3): ")

        if choice == '1':
            if os.path.exists(input_file):
                if encode_file(input_file, encoded_file, key):
                    print(f"Thành công! Đã mã hóa '{input_file}' vào '{encoded_file}'.")
            else:
                print(f"Lỗi: Không tìm thấy tệp '{input_file}'.")
        
        elif choice == '2':
            if os.path.exists(encoded_file):
                if decode_file(encoded_file, decoded_file, key):
                    print(f"Thành công! Đã giải mã '{encoded_file}' vào '{decoded_file}'.")
            else:
                print(f"Lỗi: Không tìm thấy tệp mã hóa '{encoded_file}'.")
        
        elif choice == '3':
            print("Đang thoát...")
            break
        else:
            print("Lựa chọn không hợp lệ.")

if __name__ == "__main__":
    main()
