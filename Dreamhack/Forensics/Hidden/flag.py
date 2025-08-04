import zlib as z
import base64 as b
from PIL import Image as I
d=b'DH{Fake_Flags?}';k=0x55
e=bytes([x^k for x in d]);q=b.b64encode(e);c=z.compress(q)
s=(100,100);im=I.new("RGB",s);px=im.load()
bt=''.join(f"{i:08b}"for i in c);i=0
for y in range(s[1]):
 for x in range(s[0]):
  if i>=len(bt):break
  r,g,b=px[x,y]
  r=(r&0xFE)|int(bt[i]);i+=1
  g=(g&0xFE)|int(bt[i])if i<len(bt)else g;i+=1
  b=(b&0xFE)|int(bt[i])if i<len(bt)else b;i+=1
  px[x,y]=(r,g,b)
 if i>=len(bt):break
im.save("flag.png")
with open("testfile.png","rb")as f:a=f.read()
with open("flag.png","rb")as f:h=f.read()
j=a.find(b'IEND')+12
open("base.png","wb").write(a[:j]+h)

