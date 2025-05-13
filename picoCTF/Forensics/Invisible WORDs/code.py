zip_file = open("output.zip","wb")
with open("output.bmp","rb") as f:
   hdr = f.read(0x8a)
   skip = f.read(2)
   while skip:
      keep = f.read(2)
      zip_file.write(keep)
      skip = f.read(2)
zip_file.close()