import subprocess

pos_pw_list = ["8c86", "7692", "a519", "3e61", "7dd6", "8919", "aaea", "f34b", "d9a2", "39f7", "626b", "dc78", "2a98", "7a85", "cd15", "80fa", "8571", "2f8a", "2ca6", "7e6b", "9c52", "7423", "a42c", "7da0", "95ab", "7de8", "6537", "ba1e", "4fd4", "20a0", "8a28", "2801", "2c9a", "4eb1", "22a5", "c07b", "1f39", "72bd", "97e9", "affc", "4e41", "d039", "5d30", "d13f", "c264", "c8be", "2221", "37ea", "ca5f", "fa6b", "5ada", "607a", "e469", "5681", "e0a4", "60aa", "d8f8", "8f35", "9474", "be73", "ef80", "ea43", "9f9e", "77d7", "d766", "55a0", "dc2d", "a970", "df5d", "e747", "dc69", "cc89", "e59a", "4f68", "14ff", "7928", "36b9", "eac6", "5c87", "da48", "5c1d", "9f63", "8b30", "5534", "2434", "4a82", "d72c", "9b6b", "73c5", "1bcf", "c739", "6c31", "e138", "9e77", "ace1", "2ede", "32e0", "3694", "fc92", "a7e2"]

for pw in pos_pw_list:
    # Mở tiến trình level4.py
    process = subprocess.Popen(
        ['python3', 'level4.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Gửi password, đọc output
    try:
        out, err = process.communicate(input=pw, timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        out, err = process.communicate()

    if "Welcome back" in out:
        print(f"Password found: {pw}")
        print("Flag output:")
        # Flag thường in ngay sau dòng "Welcome back..."
        lines = out.split('\n')
        for i, line in enumerate(lines):
            if "Welcome back" in line:
                # In dòng tiếp theo thường là flag
                if i+1 < len(lines):
                    print(lines[i+1])
                break
        break
else:
    print("Password not found in list.")

