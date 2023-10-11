# %%
import cv2
import pytesseract
import os
import csv
import time

# %%
class Img():
    def __init__(self, path):
        self.path = path
        self.img = cv2.imread(path)
    
    def get_grayscale(self):
        return cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
    
    def remove_noise(self):
        return cv2.medianBlur(self.img, 5)
    
    def thresholding(self):
        return cv2.threshold(self.img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    def preprocess(self):
        try:
            self.img = self.get_grayscale()
        except:
            pass
        try:
            self.img = self.thresholding()
        except:
            pass
        try:
            self.img = self.remove_noise()
        except:
            pass

    def get_text(self):
        return pytesseract.image_to_string(self.img)

# %%
class ImgToText():
    def __init__(self, dir):
        self.dir = dir + '/images'
        self.output = dir + '/image_text.csv'
        self.image_paths = self.get_image_paths()
        self.data = [] # image_path, text
    
    def get_image_paths(self):
        return [self.dir + '/' + path for path in os.listdir(self.dir)]

    def save(self):
        with open(self.output, 'w') as f:
            writer = csv.writer(f)
            # header
            writer.writerow(['image_path', 'text'])
            writer.writerows(self.data)

    def run(self):
        for path in self.image_paths:
            img = Img(path)
            img.preprocess()
            text = img.get_text()
            self.data.append((path, text))
        self.save()

# %%
if __name__ == '__main__':
    # run this for all posts that don't have image_text.csv
    for hashtag in os.listdir('./posts'):
        for date in os.listdir('./posts/' + hashtag):
            if os.path.exists('./posts/' + hashtag + '/' + date + '/image_text.csv'):
                continue
            print('Running OCR for ' + hashtag + ' on ' + date)
            img_to_text = ImgToText('./posts/' + hashtag + '/' + date)
            stime = time.time()
            img_to_text.run()
            print('Finished in ' + str(time.time() - stime) + ' seconds')