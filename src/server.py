#!/usr/bin/env python
import argparse
parser = argparse.ArgumentParser(description=
'''Covid-19-Classification Server

The server accepts messages in the form of
"command image_id" e.g. "explain_lime f00091ff-cb7a"
on stdin. Once a command finished, the server
replies with the same message on stdout, 
followed by optional response parameters.
Allowed message types are: "classify", 
"explain_lime" and "explain_gradcam". 

The images have to be located in
"CACHE_DIR_PATH/IMAGE_ID.png".
''',
formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument(
    '-c',
    '--model-path',
    required=True,
    dest='model_path',
    help='path to classification model'
)
parser.add_argument(
    '-s',
    '--segmentation-model-path',
    required=True,
    dest='segmentation_model_path',
    help='path to segmentation model'
)
parser.add_argument(
    '--cache-dir-path',
    required=True,
    dest='cache_dir_path',
    help='path to segmentation model'
)
args = parser.parse_args()

# supress tqdm progess bar for lime explainer
# until changes from 
# https://github.com/marcotcr/lime/commit/26f2590da45aa402fc94f046e5d8e6f6cf32b32b 
# are shipped
import tqdm.auto as tqdm
def nop(it, *a, **k):
    return it
tqdm.tqdm = nop

import json
import os
import logging

# silence tensorflow
logging.getLogger('tensorflow').setLevel(logging.ERROR)
os.environ['KMP_AFFINITY'] = 'noverbose'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
tf.get_logger().setLevel('ERROR')
tf.autograph.set_verbosity(3)

tf.executing_eagerly()

# import metrics. Models can not be loaded without this
from tensorflow.keras.metrics import CategoricalAccuracy, Precision, Recall, AUC
from tensorflow_addons.metrics import F1Score
from tensorflow.keras.models import load_model

import threading
import sys
from explanation.lime_explainer import LimeExplainer
from explanation.grad_cam_explainer import GradCAMExplainer
from classification.classifier import Classfier
from segmentation.lung_segmenter import LungSegmenter
from classification.segmentation_classifier import SegmentationClassifier

config = {
  'DATA': {
    'CLASSES': [
      'NO FINDING',
      'COVID-19'
    ]    
  },
  'LIME': {
    'KERNEL_WIDTH': 4,
    'FEATURE_SELECTION': 'lasso_path',
    'NUM_FEATURES': 1000,
    'NUM_SAMPLES': 20,
    'COVID_ONLY': False
  }
}


# load classification modek
model = load_model(args.model_path)

# create instances of classification, segementation
# and explanation classes
lime_explainer = LimeExplainer(
  model,
  config['LIME']['KERNEL_WIDTH'],
  config['LIME']['FEATURE_SELECTION'],
  config['LIME']['NUM_FEATURES'],
  config['LIME']['NUM_SAMPLES'],
  explanation_prefix='explanation_lime_'
  )
gradcam_explainer = GradCAMExplainer(model, inner_model=model.get_layer("NASNet"), layer_name=None, explanation_prefix='explanation_gradcam_')
classifier = Classfier(model, config['DATA']['CLASSES'])
lung_segmenter = LungSegmenter(model_file_path=args.segmentation_model_path)
segmentation_classifier = SegmentationClassifier(lung_segmenter, classifier)

def explain_lime(message_prefix, image_path, image_id):
  print(
      message_prefix,
      lime_explainer.explain(
        lung_segmenter.mask(image_path),
        image_path
      )
  )

def explain_gradcam(message_prefix, image_path, image_id):
  print(
      message_prefix,
      gradcam_explainer.explain(
        lung_segmenter.mask(image_path),
        image_path
      )
  )

def classify(message_prefix, image_path, image_id):
  print(
      message_prefix, 
      json.dumps(segmentation_classifier.classify(image_path))
  )


def start_thread(fnc, message_prefix, image_path, image_id):
  thread = threading.Thread(
      target=fnc, 
      args=(
          message_prefix,
          image_path,image_id,
      )
  )
  thread.start()
  return thread


active_treads = []

while True or False:
    sys.stdout.flush()
    data = sys.stdin.readline()
    if len(data):
      # parse user input
      user_input = str(data).strip().split(' ', 1)
      if len(user_input) > 1:
        image_path = os.path.join(
            args.cache_dir_path,
            user_input[1] + '.png'
        )

        if user_input[0] == "explain_lime":
          active_treads.append(
            start_thread(
                explain_lime,
                user_input[0] + " " + user_input[1],
                image_path,
                user_input[1]
            )
          )
        elif user_input[0] == "explain_gradcam":
          active_treads.append(
            start_thread(
                explain_gradcam,
                user_input[0] + " " + user_input[1],
                image_path,
                user_input[1]
            )
          )
        elif user_input[0] == "classify":
          active_treads.append(
            start_thread(
                classify,
                user_input[0] + " " + user_input[1],
                image_path,
                user_input[1]
            )
          )
    else:
      break

# Wait for each remaining active thread to stop
for thread in active_treads:
  thread.join()