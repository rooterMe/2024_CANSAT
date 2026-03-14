import base64
from PIL import Image, ImageFile
from io import BytesIO
ImageFile.LOAD_TRUNCATED_IMAGES = True


base64_image_data = r'C:\Users\user\Desktop\cansat\base64data.txt'

data = ''
with open(base64_image_data, 'r') as f:
    data = f.readline().strip()



data = bytes.fromhex(data)
image_data = base64.b64decode(data)

with open('decode img.jpg','wb') as f:
    f.write(image_data)

#image_data = BytesIO(image_data)
#image = Image.open(image_data)
#image.save('decoded_image.jpg')


