from __future__ import print_function
import argparse
import os
import face_recognition
import numpy as np
import sklearn
import pickle
from face_recognition import face_locations
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
import cv2
import pandas as pd
import warnings 
warnings.filterwarnings('ignore')
# we are only going to use 4 attributes
COLS = ['Asian', 'White', 'Black']
N_UPSCLAE = 1
def extract_features(img_path):
    """Exctract 128 dimensional features
    """
    X_img = face_recognition.load_image_file(img_path)
    locs = face_locations(X_img, number_of_times_to_upsample = N_UPSCLAE)
    if len(locs) == 0:
        return None, None
    face_encodings = face_recognition.face_encodings(X_img, known_face_locations = locs)
    return face_encodings, locs

def predict_one_image(img_path, clf, labels):
    """Predict face attributes for all detected faces in one image
    """
    face_encodings, locs = extract_features(img_path)
    if not face_encodings:
        return None, None
    #pred = pd.DataFrame(clf.predict_proba(face_encodings),
    #                    columns = labels)
    #pred = pred.loc[:, COLS]
    return clf.predict_proba(face_encodings)[0], locs
def draw_attributes(img_path,text_showed, box, prob):
    """Write bounding boxes and predicted face attributes on the image
    """
    img = cv2.imread(img_path)
    # img  = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
    top, right, bottom, left = box
    cv2.rectangle(img, (left, top), (right, bottom), (0, 0, 255), 2)
    font = cv2.FONT_HERSHEY_DUPLEX
    img_width = img.shape[1]
    text_showed2  = text_showed + ":" + str(prob)
    cv2.putText(img, text_showed2, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
    return img



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--img_dir', type=str,
                        default='test/', required = True,
                        help='input image directory (default: test/)')
    parser.add_argument('--output_dir', type=str,
                        default='results/',
                        help='output directory to save the results (default: results/')
    parser.add_argument('--model', type=str,
                        default='face_model.pkl', required = True,
                        help='path to trained model (default: face_model.pkl)')

    args = parser.parse_args()
    output_dir = args.output_dir
    input_dir = args.img_dir
    model_path = args.model

    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    # load the model
    with open(model_path,'rb') as f:
        clf, labels = pickle.load(f, encoding='latin1')
    print("classifying images in {}".format(input_dir))
    all_list = []
    for folder in os.listdir(input_dir):
      count = 0
      for fname in os.listdir(input_dir + folder):
          img_path = os.path.join(input_dir + folder, fname)
          try:
              pred, locs = predict_one_image(img_path, clf, labels)
          except:
              print("Skipping {}".format(img_path))
          if not locs:
              continue
          race = np.argmax(pred[1:4])
          text_showed = COLS[race]
          if (text_showed != 'Asian') and (pred[race+1] > 0.5) :
            print(text_showed, pred[race+1], pred[:5], race)
            img = draw_attributes(img_path, text_showed, locs[0],pred[race+1])
            print(os.path.join(output_dir + folder , fname))
            if not os.path.exists(output_dir + folder):
              os.mkdir(output_dir + folder)
            cv2.imwrite(os.path.join(output_dir + folder , fname), img)
          count +=1
          if (count == 1):
            break
          #locs = \
          #    pd.DataFrame(locs, columns = ['top', 'right', 'bottom', 'left'])
          #df = pd.concat([pred, locs], axis=1)
          #img = draw_attributes(img_path, df)
          #cv2.imwrite(os.path.join(output_dir, fname), img)
          #os.path.splitext(fname)[0]
          #output_csvpath = os.path.join(output_dir,
          #                              os.path.splitext(fname)[0] + '.csv')
          #df.to_csv(output_csvpath, index = False)


if __name__ == "__main__":
    main()
