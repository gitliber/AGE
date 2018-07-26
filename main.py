# -*- coding: utf-8 -*-
"""
Created on Fr March 23 01:21:40 2018

@author: lav solanki
"""

import os
import cv2
import dlib
import numpy as np
import argparse
from wide_resnet import WideResNet


def get_args():
    parser = argparse.ArgumentParser(description="This script detects faces from web cam input, "
                                                 "and estimates age and gender for the detected faces.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--weight_file", type=str, default=None,
                        help="path to weight file (e.g. weights.18-4.06.hdf5)")
    parser.add_argument("--depth", type=int, default=16,
                        help="depth of network")
    parser.add_argument("--width", type=int, default=8,
                        help="width of network")
    args = parser.parse_args()
    return args


def draw_label(image, point, label, font=cv2.FONT_HERSHEY_SIMPLEX,
               font_scale=1, thickness=2):
    size = cv2.getTextSize(label, font, font_scale, thickness)[0]
    x, y = point
    cv2.rectangle(image, (x, y - size[1]), (x + size[0], y), (255, 0, 0), cv2.FILLED)
    cv2.putText(image, label, point, font, font_scale, (255, 255, 255), thickness)


def main():
    args = get_args()
    depth = args.depth
    k = args.width
    weight_file = args.weight_file

    if not weight_file:
        weight_file = os.path.join("data", "weights.18-4.06.hdf5")

 
    detector = dlib.get_frontal_face_detector()


    img_size = 64
    model = WideResNet(img_size, depth=depth, k=k)()
    model.load_weights(weight_file)

 
    cap = cv2.VideoCapture(0)
   
    while True:
    
        ret, img = cap.read()

        if not ret:
            print("error: failed to capture image")
            return -1

        input_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
  
        img_h, img_w, _ = np.shape(input_img)
       

        detected = detector(input_img, 1)
        print(detected)
        faces = np.empty((len(detected), img_size, img_size, 3))
        print(faces)

        for i, d in enumerate(detected):
            x1, y1, x2, y2, w, h = d.left(), d.top(), d.right() + 1, d.bottom() + 1, d.width(), d.height()
            xw1 = max(int(x1 - 0.4 * w), 0)
            yw1 = max(int(y1 - 0.4 * h), 0)
            xw2 = min(int(x2 + 0.4 * w), img_w - 1)
            yw2 = min(int(y2 + 0.4 * h), img_h - 1)
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
      
            faces[i,:,:,:] = cv2.resize(img[yw1:yw2 + 1, xw1:xw2 + 1, :], (img_size, img_size))

        if len(detected) > 0:
      
            res = model.predict(faces)
            predicted_genders = res[0]
            ages = np.arange(0, 101).reshape(101, 1)
            predicted_ages = res[1].dot(ages).flatten()

   
        for i, d in enumerate(detected):
            label = "{}, {}".format(int(predicted_ages[i]),
                                    "F" if predicted_genders[i][0] > 0.5 else "M")
            draw_label(img, (d.left(), d.top()), label)

        cv2.putText(img, "Estimated Age (Years): " + str(" %6.1f " % predicted_ages), (10, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 0, 0), 2)
        cv2.imshow("Age and Gender Estimation - Jair Ribeiro", img)

        key = cv2.waitKey(25)

        if key == 27:
            break



if __name__ == '__main__':
    main()
