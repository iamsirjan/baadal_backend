import cv2
import numpy as np
import pytesseract
import re

img = cv2.imread('main_app/back.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
th, threshed = cv2.threshold(gray, 127, 255, cv2.THRESH_TRUNC)

result = pytesseract.image_to_string(threshed, lang='ind')


match = re.search(r'\d{2}-\d{2}-\d{2}-\d{5}', result)
if match:
    cc_number = match.group(0)
    print(cc_number)
else:
    print("Citizenship Certificate number not found")
