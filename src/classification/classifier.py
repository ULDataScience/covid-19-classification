from os import path

import numpy as np
from tensorflow.image import per_image_standardization
from tensorflow.keras.metrics import (AUC, CategoricalAccuracy, Precision,
                                      Recall)
from tensorflow.keras.preprocessing import image
from tensorflow_addons.metrics import F1Score


class Classfier():
    """
    Utilizes a tensorflow.keras.Model.


    Attributes
    ----------
    model : tensorflow.keras.Model
      classification model
    classes: list
        list of output classes
    """
    def __init__(self, model, classes):
        self.model = model
        self.image_size = (331, 331)
        self.classes = classes

    def classify(self, image_path):
        '''
        Classifies image specified in image_path
        :return: dict containing classification probabilities
            for each class
        '''
        if image_path is None:
            raise FileNotFoundError('image_path cannot be None!')
        if image_path == '':
            raise FileNotFoundError(
                'image_path cannot be an empty String!')
        if not path.exists(image_path):
            raise FileNotFoundError(
                '{} cannot be found!'.format(image_path))
        img = image.load_img(image_path,target_size = self.image_size)
        img = image.img_to_array(img)
        
        img = np.expand_dims(img, axis = 0)
        img = per_image_standardization(img)
        prediction = self.model.predict([img])
        return {
            v: prediction[0][k].astype(float)
            for k, v in enumerate(self.classes)
        }

    def classify_batch(self, image_paths):
        '''
        Creates classifications for each image specified in image_paths.
        :param image_paths: List of image paths
        :return: List of classifications
        '''
        return [
            self.classify(image_path) 
            for image_path in image_paths
        ]
