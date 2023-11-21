import cv2
from skimage.segmentation import mark_boundaries, slic
# import matplotlib.pyplot as plt
import numpy as np
import scipy.io as scio
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from skimage.util import img_as_float
from PIL import Image
import os
from skimage import measure
# import argparse
from icecream import ic
# import time

class Labeler():

    def __init__(self, folder_path):

        self.folder_path = folder_path
        self.display_mode = True            # True to show polygons
        self.channel = 'HV'
        self.flag = 0
        # self.label_temp = 0

        root = tk.Tk()
        self.r = int(root.winfo_screenheight() / 1.5)
        # self.c = int(root.winfo_screenwidth()  / 2.2)
        root.destroy()

        # =================== LOAD IMAGES AND SEGMENTED MAP
        IRGS_path =  self.folder_path + "/Result_002.bmp"
        img_path = self.folder_path + "/imagery_HH_UW_4_by_4_average.tif"
        img_path_HV = self.folder_path + "/imagery_HV_UW_4_by_4_average.png"

        self.img_HH_ = cv2.imread(img_path)
        self.img_HV_ = cv2.imread(img_path_HV)

        self.IRGS_ = np.array(Image.open(IRGS_path)).astype('float')

        # Assign a unique label per region
        self.IRGS_[self.IRGS_==32] = -1                 # landmask
        self.IRGS_, n_reg = measure.label(self.IRGS_, background=-1, return_num=True, connectivity=2)
        print("Number of regions: %d"%(n_reg))
        # Or you can use slic to generate regions
        # self.IRGS_ = slic(self.img_HH)

        # =================== ADDITIONAL VARIABLES
        if os.path.exists(self.folder_path + '/labeled_img_RGB.png'):
            self.labeled_img_BGR = cv2.imread(self.folder_path + '/labeled_img_RGB.png')
            self.labeled_img_gray = cv2.imread(self.folder_path + '/labeled_img_gray.png')[:,:,0]
        else:
            self.labeled_img_gray = np.zeros(self.img_HV_.shape[:2], dtype=np.uint8)
            self.labeled_img_BGR = self.img_HV_.copy()

        self.Change_channel()


    def Change_channel(self):
        
        if self.channel == 'HH':
            self.img_    = self.img_HV_.copy()
            self.channel = 'HV'

        elif self.channel == 'HV':
            self.img_    = self.img_HH_.copy()
            self.channel = 'HH'
        
        x, y = np.where(self.labeled_img_gray == 0)
        self.labeled_img_BGR[x, y] = self.img_[x, y]
        self.img_boundary_ = mark_boundaries(img_as_float(cv2.cvtColor(self.img_, cv2.COLOR_BGR2RGB)), self.IRGS_, color=(1, 1, 1), mode='inner')

        if self.flag == 0: self.flag = 1


    def Label_image(self, x = 0, y = 0, patch_size = (512, 512)):

        self.x = x
        self.y = y
        self.patch_size = patch_size

        self.img    = self.img_   [x:x+patch_size[0], y:y+patch_size[1]]
        self.IRGS   = self.IRGS_  [x:x+patch_size[0], y:y+patch_size[1]]
        self.img_boundary = self.img_boundary_[x:x+patch_size[0], y:y+patch_size[1]]

        self.c = int(self.r * self.IRGS.shape[1] / self.IRGS.shape[0])

        # =================== ROI IN CONTEXT
        mask = np.zeros((self.img_HH_.shape[:2]))
        mask[x:x+patch_size[0], y:y+patch_size[1]] = 1
        img_HH = mark_boundaries(img_as_float(cv2.cvtColor(self.img_HH_.copy(), cv2.COLOR_BGR2RGB)), mask, color=(1, 1, 1), mode='thick')
        img_HV = mark_boundaries(img_as_float(cv2.cvtColor(self.img_HV_.copy(), cv2.COLOR_BGR2RGB)), mask, color=(1, 1, 1), mode='thick')
        c = int(self.r * img_HH.shape[1] / img_HH.shape[0])        # maintain aspect ratio
        cv2.namedWindow('HH', cv2.WINDOW_NORMAL) 
        cv2.resizeWindow('HH', c, self.r)
        cv2.imshow("HH", img_HH)
        cv2.namedWindow('HV', cv2.WINDOW_NORMAL) 
        cv2.resizeWindow('HV', c, self.r)
        cv2.imshow("HV", img_HV)

        self.Show_applied_labels()

        # =================== LABEL
        cv2.namedWindow('HH_seg', cv2.WINDOW_NORMAL) 
        cv2.resizeWindow('HH_seg', self.c, self.r)
        cv2.imshow('HH_seg', self.img_boundary)

        # if self.channel == 'HH':
            # cv2.setWindowTitle('HV_seg', "HH_seg")
            # cv2.setWindowTitle('HV_Applied', "HH_Applied")
            # cv2.setWindowTitle('HV_Applied_patch', "HH_Applied_patch")
        # elif self.channel == 'HV':
            # cv2.setWindowTitle('HH_seg', "HV_seg")
            # cv2.setWindowTitle('HH_Applied', "HV_Applied")
            # cv2.setWindowTitle('HH_Applied_patch', "HV_Applied_patch")

        while 1:

            cv2.setMouseCallback('HH_seg', self.mousePoints)
            key = cv2.waitKey(0) & 0xFF
            # if key == ord('p'):
            #     if display_mode:
            #         cv2.imshow('HH_seg', self.img)
            #         display_mode = not display_mode
            #     elif not display_mode:
            #         cv2.imshow('HH_seg', self.img_boundary)
            #         display_mode = not display_mode
            if key == ord('q'):     # Change channel (polarization)
                self.Change_channel()
                self.img = self.img_[x:x+patch_size[0], y:y+patch_size[1]]
                # cv2.destroyAllWindows()
                return 0
            if key == ord('d'):     # right patch
                return 1
            if key == ord('a'):     # left patch
                return -1
            if key == ord('w'):     # up patch
                return -10
            if key == ord('s'):     # down patch
                return 10
            if key == 27 or not cv2.getWindowProperty('HH_seg', cv2.WND_PROP_VISIBLE):
                # break
                # root = tk.Tk()
                MsgBox = messagebox.askquestion ('Exit Application','Are you sure you want to exit the application?',icon = 'warning')
                if MsgBox == 'yes':
                    MsgBox_save = messagebox.askquestion ('Exit Application','Do you want to save labeling results before exit?',icon = 'warning')
                    # root.destroy()
                    if MsgBox_save == 'yes':
                        self.save_result()
                        messagebox.showinfo(title='Successful!', message='Labeling results have been saved!')
                        cv2.destroyAllWindows()
                        exit()
                    else:
                        cv2.destroyAllWindows()
                        exit()
                # else:
                #     messagebox.showinfo('Return','You will now return to the application screen')
                #     # root.destroy()
            if key == ord('g'):
                self.save_result()

    def mousePoints(self, event, x, y, flags, params):
        # global img, labeled_img_BGR, labeled_img_gray, label_temp
        if event != 0:
            segVal = self.IRGS[y][x]
            i, j = np.where(self.IRGS == segVal)

            if event == cv2.EVENT_MBUTTONDOWN:
                # Isolate region in another window
                highlight_img_mask = np.zeros(self.img.shape[:2], dtype=np.uint8)
                highlight_img_mask[i, j] = 1
                highlight_img = cv2.bitwise_and(self.img, self.img, mask = highlight_img_mask)
                a,b,w,h = cv2.boundingRect(highlight_img_mask)
                # focused_highlight_img = highlight_img[a:a+w,b:b+h]
                focused_highlight_img = highlight_img[b:b+h,a:a+w]

                highlight_boundary = mark_boundaries(img_as_float(cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)), highlight_img_mask, color=(1, 1, 1), mode='thick')
                cv2.imshow('HH_seg', highlight_boundary)

                cv2.namedWindow('Selected Region', cv2.WINDOW_NORMAL)
                c = int(self.r * focused_highlight_img.shape[1] / focused_highlight_img.shape[0])        # maintain aspect ratio
                cv2.resizeWindow('Selected Region', c, self.r)
                cv2.imshow("Selected Region", focused_highlight_img)

                # highlight_img = cv2.cvtColor(cv2.bitwise_and(self.img, self.img, mask = highlight_img_mask), cv2.COLOR_BGR2RGB)
                # plt.imshow(highlight_img)
                # plt.axis('off')
                # plt.show()

                label = self.labelChoose()
                cv2.destroyWindow('Selected Region')

                i += self.x
                j += self.y
                if label == 0:
                    self.labeled_img_BGR[i, j, :] = self.img_[i,j]
                    self.labeled_img_gray[i, j] = 0
                elif label == 1:
                    self.labeled_img_BGR[i, j, :] = (255, 200, 150)
                    self.labeled_img_gray[i, j] = 1
                elif label == 2:
                    self.labeled_img_BGR[i, j, :] = (193, 182, 255)
                    self.labeled_img_gray[i, j] = 2
                elif label == 3:
                    self.labeled_img_BGR[i, j, :] = (240, 40, 170)
                    self.labeled_img_gray[i, j] = 3
                elif label == 4:
                    self.labeled_img_BGR[i, j, :] = (0, 255, 255)
                    self.labeled_img_gray[i, j] = 4
                elif label == 5:
                    self.labeled_img_BGR[i, j, :] = (0, 0, 255)
                    self.labeled_img_gray[i, j] = 5
                elif label == 6:
                    self.labeled_img_BGR[i, j, :] = (93,41,48)
                    self.labeled_img_gray[i, j] = 6  
                # elif label == 7:
                #     self.labeled_img_BGR[i, j, :] = (144,238,144)
                #     self.labeled_img_gray[i, j] = 7

                self.Show_applied_labels()    
                if cv2.getWindowProperty('HH_seg', 0) >= 0:
                    cv2.imshow('HH_seg', self.img_boundary)

            elif event == cv2.EVENT_LBUTTONDOWN:

                i += self.x
                j += self.y
                self.labeled_img_BGR[i, j, :] = (255, 200, 150)
                self.labeled_img_gray[i, j] = 1 # water

                self.Show_applied_labels()    
                if cv2.getWindowProperty('HH_seg', 0) >= 0:
                    cv2.imshow('HH_seg', self.img_boundary)

            elif event == cv2.EVENT_RBUTTONDOWN:

                i += self.x
                j += self.y
                self.labeled_img_BGR[i, j, :] = self.img_[i,j]
                self.labeled_img_gray[i, j] = 0 # unlabeled

                self.Show_applied_labels()    
                if cv2.getWindowProperty('HH_seg', 0) >= 0:
                    cv2.imshow('HH_seg', self.img_boundary)


    def Show_applied_labels(self):

        cv2.namedWindow('HH_Applied', cv2.WINDOW_NORMAL)
        c = int(self.r * self.labeled_img_BGR.shape[1] / self.labeled_img_BGR.shape[0])        # maintain aspect ratio
        cv2.resizeWindow('HH_Applied', c, self.r)
        cv2.imshow('HH_Applied', self.labeled_img_BGR )
        
        cv2.namedWindow('HH_Applied_patch', cv2.WINDOW_NORMAL)
        c = int(self.r * self.img.shape[1] / self.img.shape[0])        # maintain aspect ratio
        cv2.resizeWindow('HH_Applied_patch', c, self.r)
        cv2.imshow('HH_Applied_patch', self.labeled_img_BGR[self.x:self.x+self.patch_size[0], 
                                                         self.y:self.y+self.patch_size[1]])

    def save_result(self):
        # root = tk.Tk()
        # folder_save_path = filedialog.askdirectory(title='Please select a directory to save the labeling results')
        cv2.imwrite(self.folder_path+'/labeled_img_RGB.png', self.labeled_img_BGR)
        cv2.imwrite(self.folder_path+'/labeled_img_gray.png', self.labeled_img_gray)
        # messagebox.showinfo(title='Successful!', message='Labeling results have been saved!')
        # root.destroy()
        # confirmation

    def labelChoose(self):
        global label_temp
        label_temp = -1

        def label_Unknow():
            global label_temp
            label_temp = 0
            win.destroy()

        def label_OW():
            global label_temp
            label_temp = 1
            win.destroy()

        def label_NI():
            global label_temp
            label_temp = 2
            win.destroy()

        def label_YI():
            global label_temp
            label_temp = 3
            win.destroy()

        def label_FYI():
            global label_temp
            label_temp = 4
            win.destroy()

        def label_MYI():
            global label_temp
            label_temp = 5
            win.destroy()

        def label_Mixed():
            global label_temp
            label_temp = 6
            win.destroy()


        win = tk.Tk()
        button0 = tk.Button(win, text="Unknown", width=10, padx=10, command=label_Unknow)
        button0.pack()
        button1 = tk.Button(win, text="Open Water", fg = "white", bg="blue", width=10, padx=10, command=label_OW)
        button1.pack()
        button2 = tk.Button(win, text="New Ice", bg="lightpink", width=10, padx=10, command=label_NI)
        button2.pack()
        button3 = tk.Button(win, text="Yong Ice", bg="purple", width=10, padx=10, command=label_YI)
        button3.pack()
        button4 = tk.Button(win, text="First-year Ice", bg="yellow", width=10, padx=10, command=label_FYI)
        button4.pack()
        button5 = tk.Button(win, text="Multi-year Ice", bg="red", width=10, padx=10, command=label_MYI)
        button5.pack()
        button6 = tk.Button(win, text="Mixed region", bg="lightgreen", width=10, padx=10, command=label_Mixed)
        button6.pack()
        win.geometry("220x220")
        win.mainloop()

        return label_temp

