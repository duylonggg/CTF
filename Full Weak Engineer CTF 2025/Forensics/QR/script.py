from PIL import Image
img = Image.open("qrgb.png").convert("RGB")
colors = sorted({img.getpixel((x,y)) for y in range(img.height) for x in range(img.width)})
colors = [c for c in colors if c != (255,255,255)]  # bỏ trắng

parts = [''.join(map(chr, c)) for c in colors]
print(colors)
print(parts)
