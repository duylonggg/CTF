# Write Up

## Little-Endian

```c
char *find_little_endian(const char *word)
{
    size_t word_len = strlen(word);
    char *little_endian = (char *)malloc((2 * word_len + 1) * sizeof(char));

    for (size_t i = word_len; i-- > 0;)
    {
        snprintf(&little_endian[(word_len - 1 - i) * 2], 3, "%02X", (unsigned char)word[i]);
    }

    little_endian[2 * word_len] = '\0';
    return little_endian;
}
```

Có thể thấy little-endian chính là nó lấy giá trị nghịch đảo từ dưới lên (hex)

---

## Big-Endian

```c
char *find_big_endian(const char *word)
{
    size_t length = strlen(word);
    char *big_endian = (char *)malloc((2 * length + 1) * sizeof(char));

    for (size_t i = 0; i < length; i++)
    {
        snprintf(&big_endian[i * 2], 3, "%02X", (unsigned char)word[i]);
    }

    big_endian[2 * length] = '\0';
    return big_endian;
}
```

Có thể thể big-endian chính là nó lấy giá trị từ trên xuống (hex)

---

## Server

```bash
Welcome to the Endian CTF!
You need to find both the little endian and big endian representations of a word.
If you get both correct, you will receive the flag.
Word: ocpwj
```

```python
>>> print(''.join(f'{ord(c):02X}' for c in ("ocpwj")))
6F6370776A
>>> print(''.join(f'{ord(c):02X}' for c in reversed("ocpwj")))
6A7770636F
```

---

## Flag

Flag: picoCTF{3ndi4n_sw4p_su33ess_cfe38ef0}
