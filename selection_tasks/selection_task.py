###############################################################
'''

This is a compilation of functions to accomplish the selection tasks 
for the AWAKE project.

Author: Prakhar Choudhary
E-mail: prakhar2397@gmail.com
github: /prakharchoudhary

'''
###############################################################
import datetime
import h5py
from matplotlib import pyplot as plt
import numpy as np
import os
import pandas as pd
import pytz
import re
# performs a median filter on N-dim array
from scipy.signal import medfilt

DIR_PATH = '.'
CSV_FILE_NAME = "data_hierarchy.csv"
IMG_NAME = 'streak_image.png'
IMG_PATH = '/AwakeEventData/XMPP-STREAK/StreakImage/streakImageData'
WIDTH_PATH = '/AwakeEventData/XMPP-STREAK/StreakImage/streakImageWidth'
HEIGHT_PATH = '/AwakeEventData/XMPP-STREAK/StreakImage/streakImageHeight'


def create_timestamp(filename):
    """
    STEP 1:

    Parses the utc-time and CERN timezone time of the log,
    for the given file.

    Input:

    -direc: pass the path of directory that carries the h5
                    data file.

    Output:

    - Prints the UTC time and time in CERN's native timezone.
    """
    print("*" * 46, "|STEP 1|", "*" * 46)
    time_nsecs = int(filename[:18])
    utc_time = datetime.datetime.utcfromtimestamp(
        time_nsecs // 10**9)
    print("The UTC time is ", utc_time)
    cern_timezone = pytz.timezone("Europe/Zurich")
    cern_time = pytz.utc.localize(
        utc_time).astimezone(cern_timezone)
    print("Time in Zone ", cern_timezone, " is ", cern_time)


def hdf5_to_csv(file):
    """
    STEP 2:

    In the input hdf file, explores all banches of the directory tree,
    identifies all of the datasets in the file and generates a csv 
    file.

    Input:

    - file: pass the hdf file object along with its complete path.

    Output:

    - Generates a csv file which records the names of all of the groups 
      and datasets, and includes the size, shape and type of data in 
      each dataset.
    """
    print("*" * 46, "|STEP 2|", "*" * 46)
    struct = {}

    def prepare_struct(name, node):
        """
        To be passed as a callable in the visititems() function, for storing
        all elemnts and their corresponding info as key value pairs
        """
        if(isinstance(node, h5py.Dataset)):
            try:
                data_type = node.dtype
            except Exception as e:
                data_type = ''
            struct[name] = ['Dataset', node.size, node.shape, data_type]
        elif(isinstance(node, h5py.Group)):
            struct[name] = ['Group', '', '', '']
        else:
            struct[name] = ['Other types', '', '', node.dtype]

    try:
        file.visititems(prepare_struct)
        assert struct is not None

        # Convert above dict to dataframe for easily saving into csv
        # format.
        data_df = pd.DataFrame.from_dict(struct, orient='index', columns=[
                                         'element_type', 'size', 'shape', 'data_Type'])
        data_df.to_csv(CSV_FILE_NAME, sep=",")
        print("Data hierarchy is stored in ", CSV_FILE_NAME)

    except Exception as e:
        print(e)


def create_image(file, imgpath, widthPath, heightPath):
    """
    STEP 3:

    Plots and saves the given image from hdf files, in png format.

    Input:

    - file: Pass the file object
    - imgpath: 1D array of the image existing in hdf file
    - widthPath: info on width of the image in hdf file
    - heightPath: info on height of the image in hdf file

    Output:

    - Plots and saves the image in png format
    """
    print("*" * 46, "|STEP 3|", "*" * 46)
    img, width, height = file[imgpath], file[
        widthPath][0], file[heightPath][0]
    try:
        img = np.reshape(img, (height, width))
    except Exception as e:
        print(e)

    # apply median filter
    filtered_img = medfilt(img)

    # plot the image and store as png
    fig = plt.figure(
        figsize=(np.ceil(height / 100), np.ceil(width / 100)))
    plt.imshow(filtered_img)
    plt.title("Streak Image")
    plt.savefig(IMG_NAME)
    print("The image is saved in '.png' format as ", IMG_NAME)
    print("*" * 45, "|FINISHED|", "*" * 45)


def main():
    """
    One singly function to execute all above functions.
    """
    all_files = os.listdir(DIR_PATH)
    only_h5 = re.compile(r'^(.)+.h5$')
    h5_files = [file for file in all_files if only_h5.match(file)]
    for fname in h5_files:
        # Executing Step 1
        create_timestamp(fname)

        # Open the file
        file = h5py.File(fname, 'r')

        # Executing Step 2
        hdf5_to_csv(file)

        # Executing Step 3
        create_image(file, IMG_PATH, WIDTH_PATH, HEIGHT_PATH)

if __name__ == '__main__':
    main()
