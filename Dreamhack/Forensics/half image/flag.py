from PIL import Image
img = Image.open("testfile.png").convert("RGB") 
width, height = img.size
hw = width // 2
left = img.crop((0, 0, hw, height))
right = img.crop((hw, 0, width, height))
left.save("left.png")
rdata = right.tobytes()
with open("left.png", "rb") as fl: lp = fl.read()
with open("flag.png", "wb") as f_out:
    f_out.write(lp)
    f_out.write(rdata)

