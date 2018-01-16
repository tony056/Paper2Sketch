import cv2
import argparse
import imutils
import numpy as np

def show(image):
    cv2.imshow("Image", image)
    cv2.waitKey(0)

def mser_func(image):
    mser = cv2.MSER_create()
    source = image.copy()
    regions, _ = mser.detectRegions(source)
    hulls = [cv2.convexHull(p.reshape(-1, 1, 2)) for p in regions]
    # cv2.polylines(source, hulls, 1, (0, 255, 0))
    return hulls

def sort_contours(hulls):
    nhulls = sorted(hulls, key=cv2.contourArea, reverse=False)
    indices = [-1 for i in range(0, len(nhulls))]
    for i, contour in enumerate(nhulls):
        if i + 1 < len(hulls):
            x, y, w, h = cv2.boundingRect(contour)
            for j in range(i + 1, len(hulls)):
                bx, by, bw, bh = cv2.boundingRect(nhulls[j])
                x_range = [bx, bx + bw]
                y_range = [by, by + bh]
                if w < 10:
                    indices[i] = 1
                if x + w/2 > x_range[0] and x + w/2 < x_range[1]:
                    if y + h/2 > y_range[0] and y + h/2 < y_range[1]:
                        indices[i] = 1
    new_hulls = []
    for i in range(0, len(hulls)):
        if indices[i] == -1:
            new_hulls.append(nhulls[i])
    return new_hulls, indices

def show_contours(hulls, image, indices):
    new_image = image.copy()
    for i, contour in enumerate(hulls):
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(new_image, (x, y), (x + w, y + h), (255, 0, 0), 2)
    return new_image

def main():
    # read the command line argument
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True,
    	help="path to the input image")
    args = vars(ap.parse_args())

    # read source image from the file
    image = cv2.imread(args['image'])
    width, height, channels = image.shape
    resized = imutils.resize(image, width=300)
    ratio = image.shape[0] / float(resized.shape[0])

    # RGB -> B & W, background as dark
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    show(gray)

    # use Canny edge detection
    canny = cv2.Canny(gray, 100, 200)
    kernel = np.ones((3,3), np.uint8)
    # do the dilation to highlight detected edges
    dilation = cv2.dilate(canny, kernel, iterations=1)
    show(dilation)

    # MSER to mark stable blobs
    hulls = mser_func(dilation)
    # sort the contours by size
    hulls, indices = sort_contours(hulls)

    # show contours with bounding boxes
    new_image = np.zeros((width, height, 3), np.uint8)
    cv2.namedWindow('Image')
    img = show_contours(hulls, image, indices)
    show(img)

if __name__ == '__main__':
    main()
