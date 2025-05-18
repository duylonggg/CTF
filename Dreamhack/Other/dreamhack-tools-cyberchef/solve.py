import codecs
import base64

rot13_decoded = codecs.decode("EUg5MJAyYJ9fYJ5iMKqio29iVK1VL2WlnTM0o3AyL2Elq3q3qlRu", 'rot_13')
decoded = base64.b64decode(rot13_decoded)
print(decoded.decode(errors="ignore"))
