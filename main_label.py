import os
import tkinter as tk
from tkinter import filedialog
from Region_labeling import Labeler
from icecream import ic
import cv2

class Slide_patches_index():
    def __init__(self, size, patch_size, overlap_percent):
        super(Slide_patches_index, self).__init__()

        h_img, w_img = size[:2]
        self.h_crop = patch_size if patch_size < h_img else h_img
        self.w_crop = patch_size if patch_size < w_img else w_img

        self.h_stride = self.h_crop - round(self.h_crop * overlap_percent) if self.h_crop < h_img else h_img
        self.w_stride = self.w_crop - round(self.w_crop * overlap_percent) if self.w_crop < w_img else w_img

        self.h_grids = max(h_img - self.h_crop + self.h_stride - 1, 0) // self.h_stride + 1
        self.w_grids = max(w_img - self.w_crop + self.w_stride - 1, 0) // self.w_stride + 1

        self.patches_list = []
        
        for h_idx in range(self.h_grids):
            for w_idx in range(self.w_grids):
                y1 = h_idx * self.h_stride
                x1 = w_idx * self.w_stride
                y2 = min(y1 + self.h_crop, h_img)
                x2 = min(x1 + self.w_crop, w_img)
                y1 = max(y2 - self.h_crop, 0)
                x1 = max(x2 - self.w_crop, 0)

                self.patches_list.append((y1, y2, x1, x2))

    def __getitem__(self, index):
        return self.patches_list[index]
    
    def __len__(self):
        return len(self.patches_list)

if __name__ == '__main__':

    PATCH_SIZE = 512
    OVERLAP_PERCENT = 0.5

    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title='Please select a directory containing HH/HV and segmentation results')
    root.destroy()

    if folder_path == '':
        print("No directory selected!!!")
        exit()

    obj = Labeler(folder_path)
    indexes = Slide_patches_index(obj.img_.shape, PATCH_SIZE, OVERLAP_PERCENT)

    i = 0
    while i < len(indexes):
        idx = indexes[i]
        v = obj.Label_image(x = idx[0], y = idx[2], patch_size = (idx[1]-idx[0], idx[3]-idx[2]))
        
        if   v == -10: i -= indexes.w_grids
        elif v ==  10: i += indexes.w_grids
        else: i += v

        i %= len(indexes)
