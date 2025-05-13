import stepic
from PIL import Image
Image.MAX_IMAGE_PIXELS = None 

img = Image.open("upz.png")
message = stepic.decode(img)
print(message)
