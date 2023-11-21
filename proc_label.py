#%%
import os
import glob
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

if __name__ == '__main__':
    file_paths = glob.glob('./*/enhanced_images/labeled_img_gray.png')

    for i in range(len(file_paths)):
        file_paths[i] = '/'.join(file_paths[i].split('\\'))     # correct windows/linux ambiguity
        print(file_paths[i])

        head, _ = os.path.split(file_paths[i])
        head, _ = os.path.split(head)
        output_folder = os.path.join(head, 'Noa_labels')
        os.makedirs(output_folder, exist_ok=True)

        image = np.asarray(Image.open(file_paths[i]))
        new_img = 1 - image

        Image.fromarray(new_img).save(os.path.join(output_folder, 'ice_water_labels.png'))
        


