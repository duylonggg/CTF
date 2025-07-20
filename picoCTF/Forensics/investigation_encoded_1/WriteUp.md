# Write Up

## Phân tích

Nguyên lý: Binary `encode` sử dụng hai cấu trúc dữ liệu:

1. `matrix[27][2]` (start, length) cho mỗi ký tự `'a'…'z'` và space.

2. `secret[]` (một buffer byte) chứa các bit mã hóa liên tiếp.

Mỗi ký tự flag được ánh xạ thành một chuỗi bit: từ bit thứ start dài length lấy từ secret[]. Kết quả ghép nối các chuỗi bit đó thành output.

---

## Lấy dữ liệu

**Dump dữ liệu thô**:

- Dùng Radare2

```bash
$ r2 -AA ./mystery
WARN: Relocs has not been applied. Please use `-e bin.relocs.apply=true` or `-e bin.cache=true` next time
INFO: Analyze all flags starting with sym. and entry0 (aa)
INFO: Analyze imports (af@@@i)
INFO: Analyze entrypoint (af@ entry0)
INFO: Analyze symbols (af@@@s)
INFO: Analyze all functions arguments/locals (afva@@@F)
INFO: Analyze function calls (aac)
INFO: Analyze len bytes of instructions for references (aar)
INFO: Finding and parsing C++ vtables (avrr)
INFO: Analyzing methods (af @@ method.*)
INFO: Recovering local variables (afva@@@F)
INFO: Type matching analysis for all functions (aaft)
INFO: Propagate noreturn information (aanr)
INFO: Scanning for strings constructed in code (/azs)
INFO: Finding function preludes (aap)
INFO: Enable anal.types.constraint for experimental type propagation
[0x000007c0]> is~secret
36  0x00000d80 0x00000d80 LOCAL  OBJ    37       secret
[0x000007c0]> bf obj.secret
[0x000007c0]> pc @ obj.secret
#define _BUFFER_SIZE 37
const uint8_t buffer[_BUFFER_SIZE] = {
  0xb8, 0xea, 0x8e, 0xba, 0x3a, 0x88, 0xae, 0x8e, 0xe8, 0xaa,
  0x28, 0xbb, 0xb8, 0xeb, 0x8b, 0xa8, 0xee, 0x3a, 0x3b, 0xb8,
  0xbb, 0xa3, 0xba, 0xe2, 0xe8, 0xa8, 0xe2, 0xb8, 0xab, 0x8b,
  0xb8, 0xea, 0xe3, 0xae, 0xe3, 0xba, 0x80
};
[0x000007c0]> bf obj.matrix
[0x000007c0]> pcw @ obj.matrix
#define _BUFFER_SIZE 54
const uint32_t buffer[_BUFFER_SIZE] = {
  0x00000008U, 0x00000000U, 0x0000000cU, 0x00000008U, 0x0000000eU,
  0x00000014U, 0x0000000aU, 0x00000022U, 0x00000004U, 0x0000002cU,
  0x0000000cU, 0x00000030U, 0x0000000cU, 0x0000003cU, 0x0000000aU,
  0x00000048U, 0x00000006U, 0x00000052U, 0x00000010U, 0x00000058U,
  0x0000000cU, 0x00000068U, 0x0000000cU, 0x00000074U, 0x0000000aU,
  0x00000080U, 0x00000008U, 0x0000008aU, 0x0000000eU, 0x00000092U,
  0x0000000eU, 0x000000a0U, 0x00000010U, 0x000000aeU, 0x0000000aU,
  0x000000beU, 0x00000008U, 0x000000c8U, 0x00000006U, 0x000000d0U,
  0x0000000aU, 0x000000d6U, 0x0000000cU, 0x000000e0U, 0x0000000cU,
  0x000000ecU, 0x0000000eU, 0x000000f8U, 0x00000010U, 0x00000106U,
  0x0000000eU, 0x00000116U, 0x00000004U, 0x00000124U
};
[0x000007c0]> exit
```

---

## Dịch ngược

Xem trong Ghidra

`main`

```c
undefined8 main(void)
{
  long lVar1;
  size_t sVar2;
  undefined4 local_18;
  int local_14;
  FILE *flag_file;
  
  flag_file = fopen("flag.txt","r");
  if (flag_file == (FILE *)0x0) {
    fwrite("./flag.txt not found\n",1,0x15,stderr);
                    // WARNING: Subroutine does not return
    exit(1);
  }
  flag_size = 0;
  fseek(flag_file,0,2);
  lVar1 = ftell(flag_file);
  flag_size = (int)lVar1;
  fseek(flag_file,0,0);
  if (0xfffe < flag_size) {
    fwrite("Error, file bigger that 65535\n",1,0x1e,stderr);
                    // WARNING: Subroutine does not return
    exit(1);
  }
  flag = malloc((long)flag_size);
  sVar2 = fread(flag,1,(long)flag_size,flag_file);
  local_14 = (int)sVar2;
  if (local_14 < 1) {
                    // WARNING: Subroutine does not return
    exit(0);
  }
  local_18 = 0;
  flag_index = &local_18;
  output = fopen("output","w");
  buffChar = 0;
  remain = 7;
  fclose(flag_file);
  encode();
  fclose(output);
  fwrite("I\'m Done, check ./output\n",1,0x19,stderr);
  return 0;
}
```

`encode`

```c
void encode(void)
{
  byte current_char;
  int end;
  undefined8 is_valid;
  ulong uVar1;
  int current_index;
  char current_lower;
  
  while( true ) {
    if (flag_size <= *flag_index) {
      while (remain != 7) {
        save(0);
      }
      return;
    }
    current_char = *(byte *)(*flag_index + flag);
    is_valid = isValid(current_char);
    if ((char)is_valid != '\x01') break;
    uVar1 = lower(current_char);
    current_lower = (char)uVar1;
    if (current_lower == ' ') {
      current_lower = '{';
    }
    current_index = *(int *)(matrix + (long)((int)current_lower + -'a') * 8 + 4);
    end = current_index + *(int *)(matrix + (long)((int)current_lower + -'a') * 8);
    while (current_index < end) {
      uVar1 = getValue(current_index);
      save((byte)uVar1);
      current_index = current_index + 1;
    }
    *flag_index = *flag_index + 1;
  }
  fwrite("Error, I don\'t know why I crashed\n",1,0x22,stderr);
                    // WARNING: Subroutine does not return
  exit(1);
}
```

`isValid`

```c
undefined8 isValid(char param_1)

{
  undefined8 uVar1;
  
  if ((param_1 < 'a') || ('z' < param_1)) {
    if ((param_1 < 'A') || ('Z' < param_1)) {
      if (param_1 == ' ') {
        uVar1 = 1;
      }
      else {
        uVar1 = 0;
      }
    }
    else {
      uVar1 = 1;
    }
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}
```

`getValue`

```c
ulong getValue(int param_1)
{
  byte bVar1;
  int iVar2;
  
  iVar2 = param_1;
  if (param_1 < 0) {
    iVar2 = param_1 + 7;
  }
  bVar1 = (byte)(param_1 >> 0x37);
  return (ulong)((int)(uint)(byte)secret[iVar2 >> 3] >>
                 (7 - (((char)param_1 + (bVar1 >> 5) & 7) - (bVar1 >> 5)) & 0x1f) & 1);
}
```

`save`

```c
void save(byte param_1)
{
  buffChar = buffChar | param_1;
  if (remain == 0) {
    remain = 7;
    fputc((int)(char)buffChar,output);
    buffChar = '\0';
  }
  else {
    buffChar = buffChar * '\x02';
    remain = remain + -1;
  }
  return;
}
```

Dịch ngược, tạo file `dict.c`

```c
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>

// Definitions from Ghidra
typedef unsigned char    byte;
typedef unsigned int     uint;
typedef unsigned long    ulong;

// r2: pc 216 @ obj.matrix
const uint8_t matrix[] = {
  0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0c, 0x00,
  0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0x0e, 0x00, 0x00, 0x00,
  0x14, 0x00, 0x00, 0x00, 0x0a, 0x00, 0x00, 0x00, 0x22, 0x00,
  0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x2c, 0x00, 0x00, 0x00,
  0x0c, 0x00, 0x00, 0x00, 0x30, 0x00, 0x00, 0x00, 0x0c, 0x00,
  0x00, 0x00, 0x3c, 0x00, 0x00, 0x00, 0x0a, 0x00, 0x00, 0x00,
  0x48, 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x52, 0x00,
  0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x58, 0x00, 0x00, 0x00,
  0x0c, 0x00, 0x00, 0x00, 0x68, 0x00, 0x00, 0x00, 0x0c, 0x00,
  0x00, 0x00, 0x74, 0x00, 0x00, 0x00, 0x0a, 0x00, 0x00, 0x00,
  0x80, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0x8a, 0x00,
  0x00, 0x00, 0x0e, 0x00, 0x00, 0x00, 0x92, 0x00, 0x00, 0x00,
  0x0e, 0x00, 0x00, 0x00, 0xa0, 0x00, 0x00, 0x00, 0x10, 0x00,
  0x00, 0x00, 0xae, 0x00, 0x00, 0x00, 0x0a, 0x00, 0x00, 0x00,
  0xbe, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0xc8, 0x00,
  0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0xd0, 0x00, 0x00, 0x00,
  0x0a, 0x00, 0x00, 0x00, 0xd6, 0x00, 0x00, 0x00, 0x0c, 0x00,
  0x00, 0x00, 0xe0, 0x00, 0x00, 0x00, 0x0c, 0x00, 0x00, 0x00,
  0xec, 0x00, 0x00, 0x00, 0x0e, 0x00, 0x00, 0x00, 0xf8, 0x00,
  0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x06, 0x01, 0x00, 0x00,
  0x0e, 0x00, 0x00, 0x00, 0x16, 0x01, 0x00, 0x00, 0x04, 0x00,
  0x00, 0x00, 0x24, 0x01, 0x00, 0x00
};

// r2: pc 37 @ obj.secret
const uint8_t secret[] = {
  0xb8, 0xea, 0x8e, 0xba, 0x3a, 0x88, 0xae, 0x8e, 0xe8, 0xaa,
  0x28, 0xbb, 0xb8, 0xeb, 0x8b, 0xa8, 0xee, 0x3a, 0x3b, 0xb8,
  0xbb, 0xa3, 0xba, 0xe2, 0xe8, 0xa8, 0xe2, 0xb8, 0xab, 0x8b,
  0xb8, 0xea, 0xe3, 0xae, 0xe3, 0xba, 0x80
};

ulong getValue(int param_1) {
  byte bVar1;
  int iVar2;
  
  iVar2 = param_1;
  if (param_1 < 0) {
    iVar2 = param_1 + 7;
  }
  bVar1 = (byte)(param_1 >> 0x37);
  return (ulong)((int)(uint)(byte)secret[iVar2 >> 3] >>
                 (7 - (((char)param_1 + (bVar1 >> 5) & 7) - (bVar1 >> 5)) & 0x1f) & 1);
}

void encode(char c) {
    int end;
    ulong uVar1;
    int current_index;
    
    printf("%c: ", c);
    
    if (c == ' ') {
        c = '{';
    }

    current_index = *(int *)(matrix + (long)((int)c + -'a') * 8 + 4);
    end = current_index + *(int *)(matrix + (long)((int)c + -'a') * 8);
    while (current_index < end) {
        uVar1 = getValue(current_index);
        printf("%d", uVar1);
        current_index = current_index + 1;
    }
    printf("\n");
}

int main(int argc, char* argv[]) {
    char c;
    for (c = 'a'; c <= 'z'; c++) {
        encode(c);
    }
    encode(' ');
    return 0;
}
```

Script python: `decode.py`

```python
from pwn import *

p = process("./dict")
dict_output = p.recvall().decode().rstrip()

encoding_dict = {}
for line in dict_output.split("\n"):
    char, encoding = line.split(": ")
    encoding_dict[encoding] = char

with open("output", "rb") as f:
    data = f.read()
    bin_data = bits_str(data)
    res = ""
    while bin_data:
        for k in encoding_dict:
            if bin_data.startswith(k):
                res += encoding_dict[k]
                bin_data = bin_data[len(k):]
                break 
print("Flag:", res)
```

---

## Flag

Flag: encodedyizvbdqluv