import os

import cv2
import numpy as np
import tensorflow as tf
from skimage.io import imsave
from tensorflow.image import per_image_standardization
from tensorflow.keras.metrics import (AUC, CategoricalAccuracy, Precision,
                                      Recall)
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow_addons.metrics import F1Score


class GradCAMExplainer():
    """
    Utilizes a tensorflow.keras.Model.


    Attributes
    ----------
    model: tensorflow.keras.Model
      classification model
    layer_name: string
      name of final conv. layer
    explanation_prefix: string:
      prefix to prepend to heatmap overlayed image filename
    """
    def __init__(
        self,
        model,
        inner_model=None,
        layer_name=None,
        explanation_prefix='explanation_'
        ):

        self.model = model
        self.classIdx = None
        self.inner_model = inner_model
        self.image_size = (331, 331)
        if self.inner_model == None:
            self.inner_model = model
        self.layer_name = layer_name 
        if self.layer_name is None:
            self.layer_name = self.__find_target_layer()
        self.explanation_prefix = explanation_prefix

    def explain(self, image_path, display_image_path=None):
        """Return the file path of the explain X-Ray image classification.

        Creates an explanation for the given X-Ray image,
        visualizes the explanation utilizing a heatmap,
        saves the visualization in the same folder as 
        the original X-Ray image

        Args:
            image_path: path of the image to be classified and explained
            display_image_path: if set, use different image to underlay
            heatmap. Useful, when the image used for classification has
            already been modified in previous stages (e.g. segmentation)
        """
        orig_img = image.load_img(image_path, target_size = self.image_size)
        orig_img = np.asarray(orig_img, dtype=np.float64)
        
        orig_img = np.expand_dims(orig_img, axis = 0)
        
        standardized_img = per_image_standardization(orig_img)

        orig_img = np.squeeze(orig_img, axis=0)
        orig_img = img_to_array(orig_img)
        
        # create explanation
        heatmap = self.__compute_heatmap(standardized_img)
        heatmap = cv2.resize(heatmap, self.image_size)
        heatmap = cv2.resize(heatmap, orig_img.shape[1::-1])

        if display_image_path is not None:
            # use different image to underlay heatmap
            orig_img = image.load_img(display_image_path, target_size = self.image_size)
            orig_img = np.asarray(orig_img, dtype=np.float64)
            orig_img = np.expand_dims(orig_img, axis = 0)
            orig_img = np.squeeze(orig_img, axis=0)
        
        # overlay heatmap
        _, visualization = self.__overlay_heatmap(
            heatmap,
            orig_img,
            alpha=0.5,
            colormap=cv2.COLORMAP_INFERNO
        )

        visualization = visualization.astype(np.uint8)
        
        # Save the image
        filename = None
        dir_path = os.path.dirname(image_path)
        img_filename = self.explanation_prefix + os.path.basename(image_path)
        if dir_path is not None:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        filename = os.path.join(dir_path, img_filename)
        imsave(filename, visualization)
        return filename

    def explain_batch(self, image_paths):
        """
        Creates explainations for each image specified in image_paths.
        :param image_paths: List of image paths. If tuple, second string
            sets display_image_path
        :return: List of paths of explained images
        """
        return [
            self.explain(image_path[0], image_path[1]) if isinstance(image_path, tuple) else self.explain(image_path)
            for image_path in image_paths
        ]

    def __overlay_heatmap(self, heatmap, image, alpha=0.5, colormap=cv2.COLORMAP_VIRIDIS):
        '''
        Overlays heatmap
        :return: tuple(heatmap, output)
        '''
        # apply the supplied color map to the heatmap and then
        # overlay the heatmap on the input image
        heatmap = cv2.applyColorMap(heatmap, colormap)
        output = cv2.addWeighted(image, alpha, heatmap, 1 - alpha, 0, dtype=cv2.CV_64F)
        # return a 2-tuple of the color mapped heatmap and the output,
        # overlaid image
        return (heatmap, output)
    def __compute_heatmap(self, image, eps=1e-8):
        '''
        Computes heatmap of given image
        :return: heatmap
        '''
        # construct our gradient model by supplying (1) the inputs
        # to our pre-trained model, (2) the output of the (presumably)
        # final 4D layer in the network, and (3) the output of the
        # softmax activations from the model
        gradModel = tf.keras.models.Model(
            inputs=[
                self.inner_model.inputs
            ],
            outputs=[
                self.inner_model.get_layer(self.layer_name).output,
                self.inner_model.output
            ]
        )                                   
        
        # record operations for automatic differentiation
        with tf.GradientTape() as tape:
            # cast the image tensor to a float-32 data type, pass the
            # image through the gradient model, and grab the loss
            # associated with the specific class index
            inputs = tf.cast(image, tf.float32)
            (convOutputs, predictions) = gradModel(inputs)
            loss = predictions[:, self.classIdx]
        # use automatic differentiation to compute the gradients
        grads = tape.gradient(loss, convOutputs)

        # compute the guided gradients
        castConvOutputs = tf.cast(convOutputs > 0, "float32")
        castGrads = tf.cast(grads > 0, "float32")
        guidedGrads = castConvOutputs * castGrads * grads
        # the convolution and guided gradients have a batch dimension
        # (which we don't need) so let's grab the volume itself and
        # discard the batch
        convOutputs = convOutputs[0]
        guidedGrads = guidedGrads[0]

            # compute the average of the gradient values, and using them
        # as weights, compute the ponderation of the filters with
        # respect to the weights
        weights = tf.reduce_mean(guidedGrads, axis=(0, 1))
        cam = tf.reduce_sum(tf.multiply(weights, convOutputs), axis=-1)

        # grab the spatial dimensions of the input image and resize
        # the output class activation map to match the input image
        # dimensions
        (w, h) = (image.shape[2], image.shape[1])
        heatmap = cv2.resize(cam.numpy(), (w, h))
        # normalize the heatmap such that all values lie in the range
        # [0, 1], scale the resulting values to the range [0, 255],
        # and then convert to an unsigned 8-bit integer
        numer = heatmap - np.min(heatmap)
        denom = (heatmap.max() - heatmap.min()) + eps
        heatmap = numer / denom
        heatmap = (heatmap * 255).astype("uint8")
        # return the resulting heatmap to the calling function
        return heatmap

    def __find_target_layer(self):
        '''
        Finds the final convolutional layer in the network
        :return: name of final conv. layer
        '''
        # attempt to find the final convolutional layer in the network
        # by looping over the layers of the network in reverse order
        for layer in reversed(self.inner_model.layers):
            # check to see if the layer has a 4D output
            if len(layer.output_shape) == 4:
                return layer.name
        # otherwise, we could not find a 4D layer so the GradCAM
        # algorithm cannot be applied
        raise ValueError("Could not find 4D layer. Cannot apply GradCAM.") 
