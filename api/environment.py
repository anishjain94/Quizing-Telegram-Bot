import os
from PIL import Image

cwd = os.path.abspath('.')
wordsPath = cwd + '/static/words.txt'
backgroundImg = Image.open(cwd + '/static/background.jpg')
staticFilesPath = cwd + '/static/'