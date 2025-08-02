import base64

def extract_and_decode(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Lỗi đọc file: {e}")
        return

    # Tách từ và lấy chữ cái đầu
    letters = ''.join(word[0] for word in content.split())

    print(f"🔤 Chữ đầu mỗi từ: {letters}")

    # Padding để đủ độ dài base64 (chia hết cho 4)
    padded = letters + "=" * (-len(letters) % 4)

    try:
        decoded = base64.b64decode(padded).decode('utf-8', errors='ignore')
        print(f"🔓 Base64 decoded: {decoded}")
    except Exception as e:
        print(f"⚠️  Lỗi giải mã base64: {e}")

if __name__ == "__main__":
    extract_and_decode("text.txt")

