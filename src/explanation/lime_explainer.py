import os
import numpy as np
from keras.preprocessing import image
from lime.lime_image import *
from skimage.io import imsave
from skimage.segmentation import mark_boundaries
from tensorflow.image import per_image_standardization
from tensorflow.keras.preprocessing.image import ImageDataGenerator


class LimeExplainer():
  """
  Utilizes a tensorflow.keras.Model from a given path.

  Attributes
  ----------
  model : tensorflow.keras.Model
      classification model
  kernel_width: float
      kernel width for the exponential kernel
  feature_selection: string
      feature selection method. can be
                'forward_selection', 'lasso_path', 'none' or 'auto'
  num_features: int
      maximum number of features present in explanation
  num_samples: int
      size of the neighborhood to learn the linear model
  explanation_prefix: string:
      prefix to prepend to heatmap overlayed image filename
  """

  def __init__(
        self,
        model,
        kernel_width,
        feature_selection,
        num_features = 1000,
        num_samples = 1000,
        explanation_prefix='explanation_'
    ):
    
    self.model = model
    self.KERNEL_WIDTH = kernel_width
    self.FEATURE_SELECTION = feature_selection
    self.image_size = (331, 331)
    self.num_features = num_features
    self.num_samples = num_samples
    self.exp = LimeImageExplainer(
      kernel_width=self.KERNEL_WIDTH,
      feature_selection=self.FEATURE_SELECTION
    )
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
    standardized_img = np.squeeze(standardized_img, axis=0)

    # create explanation
    explanation = self.__predict_and_explain(
      standardized_img,
      self.model,
      self.exp, 
      self.num_features,
      self.num_samples
    )

    if display_image_path is not None:
        # use different image to underlay heatmap
        orig_img = image.load_img(display_image_path, target_size = self.image_size)
        orig_img = np.asarray(orig_img, dtype=np.float64)
        orig_img = np.expand_dims(orig_img, axis = 0)
        orig_img = np.squeeze(orig_img, axis=0)
    else:
        orig_img = np.squeeze(orig_img, axis=0)

    # overlay heatmap
    visualization = self.__visualize_explanation(
      orig_img,
      explanation
    )

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
        self.explain(image_path[0], image_path[1]) if isinstance(image_paths, tuple) else self.explain(image_path)
        for image_path in image_paths
    ]
      
  
  def __predict_instance(self, x, model):
    """
    Runs model prediction on 1 or more input images.
    :param x: Image(s) to predict
    :param model: A Keras model
    :return: A numpy array comprising a list of class probabilities for each prediction
    """
    y = model.predict(x)  # Run prediction on the perturbations
    if y.shape[1] == 1:
        probs = np.concatenate([1.0 - y, y], axis=1)  # Compute class probabilities from the output of the model
    else:
        probs = y
    return probs

  def __predict_and_explain(self, x, model, exp, num_features, num_samples):
    """
    Use the model to predict a single example and apply LIME to generate an explanation.
    :param x: Preprocessed image to predict
    :param model: The trained neural network model
    :param exp: A LimeImageExplainer object
    :param num_features: # of features to use in explanation
    :param num_samples: # of times to perturb the example to be explained
    :return: explanation
    """

    def predict(x):
      """
      Helper function for LIME explainer. Runs model prediction on perturbations of the example.
      :param x: List of perturbed examples from an example
      :return: A numpy array constituting a list of class probabilities for each predicted perturbation
      """
      return self.__predict_instance(x, model)

    # Algorithm for superpixel segmentation. Parameters set to limit size of superpixels and promote border smoothness
    segmentation_fn = SegmentationAlgorithm(
        'quickshift',
        kernel_size=2.25,
        max_dist=50,
        ratio=0.1,
        sigma=0.15
    )
    # Generate explanation for the example
    x = np.asarray(x)
    explanation = exp.explain_instance(
        x.astype(np.float64),
        predict,
        num_features=num_features,
        num_samples=num_samples,
        segmentation_fn=segmentation_fn
    )
    probs = self.__predict_instance(
        np.expand_dims(x, axis=0),
        model
    )
    return explanation

  def __visualize_explanation(self, orig_img, explanation):
    """
    Visualize an explanation for the prediction of a single X-ray image.
    :param orig_img: Original X-Ray image
    :param explanation: ImageExplanation object
    :return: explained image
    """

    label_to_see = explanation.top_labels[0]
    explanation.image = orig_img
    temp, mask = explanation.get_image_and_mask(
      label_to_see,
      positive_only=False, 
      num_features=10,
      hide_rest=False
    )

    explained_image = mark_boundaries(temp, mask)
    explained_image = explained_image.astype(np.uint8)
    return explained_image
