"""LungSegmentor, which creates masks for lungs from X-Ray Images."""

from os import path

from cv2 import (INTER_CUBIC, MORPH_CLOSE, MORPH_OPEN, dilate, imread, imwrite,
                 morphologyEx, resize)
from numpy import expand_dims, float32, ones, squeeze, uint8
from numpy.ma import masked_where
from tensorflow.image import per_image_standardization
from tensorflow.keras.models import load_model


class LungSegmenter():
    """
    Loads and utilizes a tensorflow.keras.Model from a given path.

    Attributes
    ----------
    model_file_path : string
        file_path of the model to load
    mask_binarization_treshold: float
        threshold which is used to convert the prediction of the model to binary mask
    morphology_kernel_size: tuple(int, int)
        size of the kernel for posterior morphology operations on the mask
        see __remove_small_regions_and_dilate
    dilation_kernel_size: tuple(int, int)
        size of the kernel for posterior dilation operations on the mask
        see __remove_small_regions_and_dilate
    dilation_iterations: int
        number of iterations of dilation applied on the mask
        see __remove_small_regions_and_dilate
    input_dimension: tuple(int, int):
        input shape of the model to which all the images are resized to
        it is derived from the loaded model
    """

    def __init__(self,
                 model_file_path=None,
                 mask_binarization_treshold=0.5,
                 morphology_kernel_size=(5, 5),
                 dilation_kernel_size=(2, 2),
                 dilation_iterations=3
                 ):
        """Construct a new LungSegmentor.

        Constructor for LungSegmentor
        """
        try:
            if model_file_path is None:
                raise FileNotFoundError('model_file_path cannot be None!')
            if model_file_path == '':
                raise FileNotFoundError(
                    'model_file_path cannot be an empty String!')
            if not path.exists(model_file_path):
                raise FileNotFoundError(
                    '{} cannot be found!'.format(model_file_path))
            self.u_net = load_model(model_file_path)
            self.mask_binarization_treshold = mask_binarization_treshold
            self.morphology_kernel_size = morphology_kernel_size
            self.dilation_kernel_size = dilation_kernel_size
            self.dilation_iterations = dilation_iterations
            self.input_dimension = tuple(
                squeeze(self.u_net.layers[0].input_shape, axis=0)[1:3])
        except FileNotFoundError as fnfe:
            print(fnfe)
        except IOError as ioe:
            print(ioe)

    def mask(self, file_path):
        """Return the file path of the masked X-Ray image.

        Predicts a mask for the lungs in a given X-Ray image,
        saves the mask and the masked image in the same
        folder as the original X-Ray image
        """
        try:
            if file_path is None:
                raise FileNotFoundError('file_path cannot be None!')
            if file_path == '':
                raise FileNotFoundError('file_path cannot be an empty String!')
            if not path.exists(file_path):
                raise FileNotFoundError(
                    '{} cannot be found!'.format(file_path))
            dot_index = file_path.rfind('.')
            masked_image_file_path = '{}{}{}'.format(
                file_path[:dot_index], '_masked', file_path[dot_index:])
            mask_file_path = '{}{}{}'.format(
                file_path[:dot_index], '_mask', file_path[dot_index:])
            original_image = imread(file_path, 0).astype(float32)/255.0
            original_image_size = original_image.shape[::-1]

            downsized_image = resize(
                original_image, dsize=self.input_dimension, interpolation=INTER_CUBIC)
            downsized_image = expand_dims(downsized_image, axis=0)
            downsized_image = per_image_standardization(downsized_image)

            mask_prediction = self.u_net.predict(downsized_image)

            mask = mask_prediction > self.mask_binarization_treshold
            mask = self.__remove_small_regions_and_dilate(mask)
            upsized_mask = resize(squeeze(mask).astype(
                float32), dsize=original_image_size, interpolation=INTER_CUBIC)
            masked_image = self.__mask_image(original_image, upsized_mask)
            imwrite(mask_file_path, upsized_mask*255)
            imwrite(masked_image_file_path, masked_image*255)
            return masked_image_file_path
        except FileNotFoundError as fnfe:
            print(fnfe)
        except IOError as ioe:
            print(ioe)

    def mask_batch(self, dataframe, file_path_column_name='file_path'):
        """Return a new dataframe with paths to masked files.

        Masks all X-Ray images in the given dataframe and returns
        a new dataframe with a new column (masked_{file_path_column_name})
        which holds file_paths to the masked lung images.
        """
        try:
            if dataframe is None:
                raise AttributeError('dataframe cannot be None!')
            if file_path_column_name == '':
                raise AttributeError(
                    'file_path_column_name cannot be an empty String!')
            if file_path_column_name is None:
                raise AttributeError('file_path_column_name cannot be None!')
            masked_file_paths = []
            for file_path in dataframe[file_path_column_name]:
                masked_file_paths.append(self.mask(file_path))
            dataframe.insert(1, 'masked_{}'.format(
                file_path_column_name), masked_file_paths)
            return dataframe
        except FileNotFoundError as fnfe:
            print(fnfe)
        except IOError as ioe:
            print(ioe)

    def __mask_image(self, image, mask):
        """Return masked X-Ray image."""
        return masked_where(mask == 0, image)

    def __remove_small_regions_and_dilate(self, image):
        """Return dilated and and morphologically improved mask.

        Morphologically removes small (< morphology_kernel_size) connected regions of 0s or 1s
        and dilates mask with dilation_kernel_size for dilation_iterations.
        """
        morphology_kernel = ones(self.morphology_kernel_size, uint8)
        dilation_kernel = ones(self.dilation_kernel_size, uint8)
        image = squeeze(image).astype(float32)
        image = morphologyEx(image, MORPH_CLOSE, morphology_kernel)
        image = morphologyEx(image, MORPH_OPEN, morphology_kernel)
        image = dilate(image, dilation_kernel,
                       iterations=self.dilation_iterations)
        return image
