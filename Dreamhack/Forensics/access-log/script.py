import re
import urllib.parse

def extract_not_equal_numbers(log_path):
    result = []

    # Mã hóa URL của ký tự "!=" là "%21%3D"
    not_equal_encoded = '%21%3D'

    with open(log_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Chỉ xét các dòng chứa từ "flag" và có chứa dấu "!=" (mã hóa)
            if 'flag' in line and not_equal_encoded in line:
                # Giải mã URL để dễ tìm dấu != và số sau đó
                decoded_line = urllib.parse.unquote(line)

                # Tìm biểu thức kiểu: !=<số>
                matches = re.findall(r'!=\s*(\d+)', decoded_line)
                result.extend(matches)

    return result

# Ví dụ sử dụng
if __name__ == "__main__":
    path_to_log = "access.log"
    extracted_numbers = extract_not_equal_numbers(path_to_log)

    print("Các số xuất hiện ngay sau '!=' trong dòng có 'flag':")
    for num in extracted_numbers:
        print(num)

