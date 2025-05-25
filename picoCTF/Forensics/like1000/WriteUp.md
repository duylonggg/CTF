# Write Up

Giải nén file `.tar`

Gợi ý bảo dùng Script vậy nên rất có khả năng là file được nén nhiều lần, cụ thể chắc là 1000 lần vì tên file là `1000.tar`

Script

```python
import tarfile
import os
import shutil

TAR_NAME = '1000.tar'
TMP_DIR = 'tmp_extract'

while True:
    try:
        # Tạo thư mục tạm nếu chưa có
        if not os.path.exists(TMP_DIR):
            os.makedirs(TMP_DIR)
        else:
            shutil.rmtree(TMP_DIR)
            os.makedirs(TMP_DIR)

        # Mở và giải nén 1000.tar
        with tarfile.open(TAR_NAME, 'r') as tar:
            tar.extractall(TMP_DIR)
            print(f'[*] Extracted {TAR_NAME} into {TMP_DIR}')

        # Tìm file 1000.tar tiếp theo bên trong thư mục tạm
        next_tar = None
        for root, dirs, files in os.walk(TMP_DIR):
            for file in files:
                if file.endswith('.tar'):
                    next_tar = os.path.join(root, file)
                    break
            if next_tar:
                break

        if not next_tar:
            print('[!] No more .tar file found. Exiting.')
            break

        # Ghi đè 1000.tar bằng file .tar mới
        shutil.copyfile(next_tar, TAR_NAME)
        print(f'[+] Found nested tar file, replaced {TAR_NAME}')

    except Exception as e:
        print(f'[X] Error: {e}')
        break
```

Flag: picoCTF{l0t5_0f_TAR5}
