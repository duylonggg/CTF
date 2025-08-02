import base64
import re

# Tag to hex mapping (same as the original C# program)
tag_hex = {
    "cite": "0", "h1": "1", "p": "2", "a": "3", "img": "4", "ul": "5", "ol": "6",
    "button": "7", "div": "8", "span": "9", "label": "a", "textarea": "b", "nav": "c",
    "b": "d", "i": "e", "blockquote": "f"
}

def decode_data(html_content):
    decoded_str = ""

    # Match opening tags like <tag ...> and convert to hex using tag_hex
    matches = re.findall(r'<(\w+)[\s>]', html_content)
    for match in matches:
        if match in tag_hex:
            decoded_str += tag_hex[match]

    print("🔢 Hex String:", decoded_str)

    try:
        decoded_bytes = bytes.fromhex(decoded_str)
        decoded_ascii = decoded_bytes.decode('ascii', errors='ignore')
        return decoded_bytes, decoded_ascii
    except ValueError as e:
        print(f"❌ Error decoding hex: {e}")
        return None, None

def decode_html(input_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return decode_data(html_content)
    except FileNotFoundError:
        print("❌ File not found.")
        return None, None
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None, None

if __name__ == "__main__":
    input_file = input("📂 Nhập đường dẫn đến file HTML: ").strip()
    decoded_bytes, decoded_ascii = decode_html(input_file)

    if decoded_ascii:
        print("\n✅ Decoded ASCII:")
        print(decoded_ascii)

    if decoded_bytes:
        print("\n📦 Decoded Bytes:")
        print(decoded_bytes)

