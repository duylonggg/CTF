import sys
from PIL import Image
src,offset,W,H,pitch,out=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]),sys.argv[6]

need=pitch*H
with open(src,"rb") as f: f.seek(offset); buf=f.read(need)
rowbytes=W*4; tight=bytearray(W*H*4)
for y in range(H):
    row=buf[y*pitch:y*pitch+rowbytes]
    for x in range(0,rowbytes,4):
        b,g,r,a=row[x:x+4]; i=y*rowbytes+x
        tight[i:i+4]=bytes([r,g,b,255])
Image.frombytes("RGBA",(W,H),bytes(tight)).save(out)