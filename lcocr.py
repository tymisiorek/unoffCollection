import os
import pandas as pd
import numpy as np

from matplotlib import pyplot as plt

from openai import OpenAI

from PIL import Image
import pdf2image

import cv2
import pytesseract


def plt_imshow(title, image, figsize=(10,5)):
    # convert the image frame BGR to RGB color space and display it
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    fig = plt.figure(figsize=figsize)
    plt.imshow(image)
    plt.title(title)
    plt.grid(False)
    plt.show()
    
def get_black_corners(image):
    black_pixels = np.column_stack(np.where(image > 0))
    if len(black_pixels) == 0:
        firstWhite = (0,0)
        lastWhite = (0,0)
    else:
        firstWhite = black_pixels[0]
        lastWhite = black_pixels[-1]
    
    return firstWhite, lastWhite

def detect_masked_areas(image, minArea=10000):
    
    #10,000 seems to be a good minimum area threshold that is always large enough to detect the underlying structure, but not detect the entire image.
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7,7), 0)
    threshold = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    threshold = cv2.bitwise_not(threshold)
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros_like(threshold)
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations = 1)

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > minArea:
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            #Draw convex hull of approximate contour, wrapping it around the whole page, essentially creating a border around the image
            hull = cv2.convexHull(approx)
            cv2.drawContours(mask,[hull], -1, 255, thickness = cv2.FILLED)
    result = cv2.bitwise_and(image, image, mask = mask)
    return np.array(result)

def rotate_image(image):
    
    masked_image = detect_masked_areas(image, minArea=10000)
    
    gray = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
    
    firstWhite, lastWhite = get_black_corners(gray)
    
    point_list = [[firstWhite, lastWhite]]
    
    #Find the rotation angle based on the skew of the image
    rotationAngle = np.abs(np.arctan2(lastWhite[1] - firstWhite[1], lastWhite[0] - firstWhite[0]) * 180 / np.pi)
    rows, columns = gray.shape
    
    #Find rotation matrix with fixed translation
    center = (columns// 2, rows // 2)
    rotationMatrix = cv2.getRotationMatrix2D(center, rotationAngle, 1)
    
    #Find new dimensions so that the rotated image fits inside the canvas
    cosine = np.abs(rotationMatrix[0,0])
    sine = np.abs(rotationMatrix[0,1])
    newColumns = int((columns * cosine) + (rows * sine))
    newRows = int((columns * sine) + (rows * cosine))
    rotationMatrix[0,2] += (newColumns - columns) / 2
    rotationMatrix[1,2] += (newRows - rows) / 2
    
    #Apply the rotation to the image
    rotated_masked_Image = cv2.warpAffine(gray, rotationMatrix, (newColumns, newRows))
    rotated_orig_Image = cv2.warpAffine(image, rotationMatrix, (newColumns, newRows))
    
    firstWhiteRotated, lastWhiteRotated = get_black_corners(rotated_masked_Image)
    
    point_list.append([firstWhiteRotated, lastWhiteRotated])
    return point_list, rotated_orig_Image

def straighten_image(point_list, image):
    
    firstWhite, lastWhite = point_list[0]
    firstWhiteRotated, lastWhiteRotated = point_list[1]
    
    #Find the rotation angle based on the skew of the image
    rotationAngle = np.abs(np.arctan2(lastWhite[1] - firstWhite[1], lastWhite[0] - firstWhite[0]) * 180 / np.pi)
    rows, columns, _ = image.shape
    
    #Find rotation matrix with fixed translation
    center = (columns// 2, rows // 2)
    rotationMatrix = cv2.getRotationMatrix2D(center, rotationAngle, 1)
    
    #Find new dimensions so that the rotated image fits inside the canvas
    cosine = np.abs(rotationMatrix[0,0])
    sine = np.abs(rotationMatrix[0,1])
    newColumns = int((columns * cosine) + (rows * sine))
    newRows = int((columns * sine) + (rows * cosine))
    rotationMatrix[0,2] += (newColumns - columns) / 2
    rotationMatrix[1,2] += (newRows - rows) / 2
    
    inverseRotationMatrix = cv2.getRotationMatrix2D(center,-rotationAngle, 1)
    inverseRotationMatrix = np.vstack([inverseRotationMatrix, [0, 0, 1]])
    # Calculate the new positions of the dots after rotation
    newFirstWhiteUnrotated = np.array([
      center[0] + int((firstWhiteRotated[0] - center[0]) * np.cos(np.radians(rotationAngle)) +
                      (firstWhiteRotated[1] - center[1]) * np.sin(np.radians(rotationAngle))),
      center[1] + int((firstWhiteRotated[1] - center[1]) * np.cos(np.radians(rotationAngle)) -
                      (firstWhiteRotated[0] - center[0]) * np.sin(np.radians(rotationAngle)))
    ])

    newLastWhiteUnrotated = np.array([
      center[0] + int((lastWhiteRotated[0] - center[0]) * np.cos(np.radians(rotationAngle)) +
                      (lastWhiteRotated[1] - center[1]) * np.sin(np.radians(rotationAngle))),
      center[1] + int((lastWhiteRotated[1] - center[1]) * np.cos(np.radians(rotationAngle)) -
                      (lastWhiteRotated[0] - center[0]) * np.sin(np.radians(rotationAngle)))
    ])

    unrotatedImage = cv2.warpAffine(image, inverseRotationMatrix[:2, :], (newColumns, newRows))
        
    return unrotatedImage, newFirstWhiteUnrotated, newLastWhiteUnrotated

class Rect:
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
    
    def rescale(self,rescale_factor=2.3):
        self.pos = tuple(map(int, (rescale_factor*self.pos[0], rescale_factor*self.pos[1])))
        self.size = tuple(map(int, (rescale_factor*self.size[0], rescale_factor*self.size[1])))

def add_cv2_rect(image, rect, rectangleColor = (255, 100, 0)):
    
    cv2.rectangle(image, rect.pos, (rect.pos[0] + rect.size[0], rect.pos[1] + rect.size[1]), rectangleColor, thickness = 2)
    
    return image
    
def get_cropped_region(image, rect):
    return image[rect.pos[1]:rect.pos[1] + rect.size[1], rect.pos[0]:rect.pos[0] + rect.size[0]]
        
def column_split(image, firstWhite, lastWhite):
    xdist = lastWhite[0] - firstWhite[0]
    ydist = firstWhite[1] - lastWhite[1]
    
    #I added extra to the midpoint and rectangle sizes because there's not really risk of messing up the text by having the boxes slightly too big, and this accounts for potential error inaccuracies in the bounding rectangles
    midpoint = (ydist//2) + 20
    
    rect1 = Rect(pos=(lastWhite[1] - 15, lastWhite[0] - xdist), size=(midpoint + 20, xdist + 35))
    
    #probably safe to make rectangle 2 larger than rectangle 1 because there's more space at the end without new words
    #going to make rectangle 2 start with a larger added value to its x position compared to rectangle 1
    rect2 = Rect(pos=(firstWhite[1] - midpoint + 25, firstWhite[0]), size=(midpoint + 30, xdist + 35))
    
    return image, rect1, rect2

def binarize_image(image, rescale_factor=2.3):
    image = cv2.resize(image, None, fx = rescale_factor, fy = rescale_factor)
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(image, (5,5), 1)
    adaptiveThresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 5, 2)
    
    return adaptiveThresh


def extract_text(image, rect=None, char_black = "[]{}|!«»+"):
    if rect is not None:
        croppedRegion = get_cropped_region(image, rect)
    else:
        croppedRegion = image
    return pytesseract.image_to_string(croppedRegion, config="-c tessedit_char_blacklist={}".format(char_black))

def extract_text_by_lines(image, rect=None, char_black = "[]{}|!«»+"):
    if rect is not None:
        croppedRegion = get_cropped_region(image, rect)
    else:
        croppedRegion = image

    dilated_thresh = cv2.dilate(croppedRegion, np.ones((3,100)))
    cnts = cv2.findContours(dilated_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # Use index [-2] to be compatible to OpenCV 3 and 4

    # Build a list of bounding boxes
    bounding_boxes = [cv2.boundingRect(c) for c in cnts]

    # Sort bounding boxes from "top to bottom"
    bounding_boxes = sorted(bounding_boxes, key=lambda b: b[1])
    
    extracted_text = ""
    for b in bounding_boxes:
        x, y, w, h = b

        if (h > 10) and (w > 10):
            # Crop a slice, and inverse black and white (tesseract prefers black text).
            line_slice = 255 - thresh[max(y-10, 0):min(y+h+10, thresh.shape[0]), max(x-10, 0):min(x+w+10, thresh.shape[1])]

            text = pytesseract.image_to_string(line_slice, config="--psm 4 -c tessedit_char_blacklist={}".format(char_black))

            extracted_text += text + "\n"
            
    return extracted_text


