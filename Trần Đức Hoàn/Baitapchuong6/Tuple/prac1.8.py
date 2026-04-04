# 1.8 Luyện tập: Chương trình mã hóa và giải mã văn bản dựa trên một bảng mã (dictionary)

def encode_text(text, mapping):
    """Mã hóa văn bản dựa trên từ điển mapping"""
    encoded = ""
    for char in text:
        # Nếu ký tự có trong mapping thì thay thế, ngược lại giữ nguyên
        encoded += mapping.get(char, char)
    return encoded

def decode_text(encoded_text, mapping):
    """Giải mã văn bản dựa trên từ điển mapping"""
    # Tạo từ điển ngược để giải mã
    reverse_mapping = {v: k for k, v in mapping.items()}
    decoded = ""
    for char in encoded_text:
        # Nếu ký tự có trong mapping ngược thì thay thế, ngược lại giữ nguyên
        decoded += reverse_mapping.get(char, char)
    return decoded

def main():
    # Bảng mã ví dụ
    code_table = {
        'a': '!', 'b': '@', 'c': '#', 'd': '$',
        'e': '%', 'f': '^', 'g': '&', 'h': '*',
        'i': '(', 'j': ')', 'k': '-', 'l': '_',
        'm': '=', 'n': '+', 'o': '[', 'p': ']',
        'q': '{', 'r': '}', 's': ';', 't': ':',
        'u': '<', 'v': '>', 'w': '?', 'x': '/',
        'y': '|', 'z': '~', ' ': '.'
    }

    print("--- CHƯƠNG TRÌNH MÃ HÓA / GIẢI MÃ ---")
    print(f"Bảng mã mẫu: {code_table}")
    
    # Nhập văn bản từ người dùng
    original_text = input("\nNhập văn bản cần mã hóa: ").lower()
    
    # Thực hiện mã hóa
    encoded = encode_text(original_text, code_table)
    print(f"Văn bản đã mã hóa: {encoded}")
    
    # Thực hiện giải mã
    decoded = decode_text(encoded, code_table)
    print(f"Văn bản sau khi giải mã: {decoded}")

if __name__ == "__main__":
    main()
