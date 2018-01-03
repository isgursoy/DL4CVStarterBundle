from keras.applications import ResNet50
from keras.applications import InceptionV3
from keras.applications import Xception  # TensorFlow ONLY
from keras.applications import VGG16
from keras.applications import VGG19
from keras.applications import imagenet_utils
from keras.applications.inception_v3 import preprocess_input
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import load_img
import numpy as np
import argparse
import cv2

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
                help="path to the input image")
ap.add_argument("-model", "--model", type=str, default="vgg16",
                help="name of pre-trained network to use")
args = vars(ap.parse_args())

# Define a dictionary that maps model names to their classes inside Keras
MODELS = {
    "vgg16": VGG16,
    "vgg19": VGG19,
    "inception": InceptionV3,
    "xception": Xception,  # TensorFlow ONLY
    "resnet": ResNet50
}

# Ensure a valid model name was supplied via command line argument
if args["model"] not in MODELS.keys():
    raise AssertionError("The --model command line argument should be a key in the `MODELS` dictionary")

# Initialize the input image shape (224x224 pixels) along with the pre-processing function (this might need to be
# changed based on which model we use to classify our image)
inputShape = (224, 224)
preprocess = imagenet_utils.preprocess_input

# if we are using the InceptionV3 or Xception networks, then we
# need to set the input shape to (299x299) [rather than (224x224)]
# and use a different image processing function
if args["model"] in ("inception", "xception"):
    input_shape = (299, 299)
    preprocess = preprocess_input

# Load our the network weights from disk (NOTE: if this is the first time you are running this script for a given
# network, the weights will need to be downloaded first -- depending on which network you are using, the weights can
# be 90-575MB, so be patient; the weights will be cached and subsequent runs of this script will be *much* faster)
print("[INFO]: Loading {}....".format(args["model"]))
network = MODELS[args["model"]]
model = network(weights="imagenet")

# Load the input image using the Keras helper utility while ensuring the image is resized to `inputShape`, the required
# input dimensions for the ImageNet pre-trained network
print("[INFO]: Loading and pre-processing image....")
image = load_img(args["image"], target_size=inputShape)
image = img_to_array(image)

# Our input image is now represented as a NumPy array of shape (inputShape[0], inputShape[1], 3) however we need to
# expand the dimension by making the shape (1, inputShape[0], inputShape[1], 3) so we can pass it through the network
image = np.expand_dims(image, axis=0)

# Pre-process the image using the appropriate function based on the model that has been loaded
image = preprocess(image)

# Classify the image
print("[INFO]: Classifying image with '{}'...".format(args["model"]))
preds = model.predict(image)
P = imagenet_utils.decode_predictions(preds)

# Loop over the predictions and display the rank-5 predictions + probabilities to our terminal
for (i, (imagenetID, label, prob)) in enumerate(P[0]):
    print("{}. {}: {:.2f}%".format(i + 1, label, prob * 100))

# Load the image via OpenCV, draw the top prediction on the image, and display the image to our screen
orig = cv2.imread(args["image"])
(imagenetID, label, prob) = P[0][0]
cv2.putText(orig, "Label: {}".format(label), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
cv2.imshow("Classification", orig)
cv2.waitKey(0)
