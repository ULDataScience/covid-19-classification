from os import path

class SegmentationClassifier:
    """
    Orchestrates lung segmentation and classification

    Creates masked images and runs them through the classifier

    Attributes
    ----------
    lung_segmenter: lung segmenter instance 
    classfier: classifier instance
    """
    def __init__(self, lung_segmenter, classfier):
        self.lung_segmenter = lung_segmenter
        self.classfier = classfier


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

        masked_image_path = self.lung_segmenter.mask(image_path)
        return self.classfier.classify(masked_image_path)

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