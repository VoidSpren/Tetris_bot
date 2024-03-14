import pyautogui as ag
from PIL import Image, ImageOps
import time
import os

count = 0

path = f'python/img/test{count}.png'
while(os.path.exists(path)):
  os.remove(path)
  count += 1
  path = f'python/img/test{count}.png'


# encontre que una buena region es (876, 359, 270, 370)
a = input()
count = 0
region = tuple(map(int, a.split()))

while(a != 's'):
  size = ag.size()
  if(len(region) == 4):
    im = ag.screenshot(region=region)
    im = ImageOps.grayscale(im)
    im.save(f'python/img/test{count}.png')
    print('screenshot taken')
  print(region)
  count += 1
