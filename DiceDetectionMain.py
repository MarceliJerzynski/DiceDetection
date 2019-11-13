import math
import sys
import cv2
import numpy as np
from statistics import mean

amount_of_pictures = 54
header = '('
ender = ')'


def rescale_frame(frame, percent=75):
    width = int(frame.shape[1] * percent / 100)
    height = int(frame.shape[0] * percent / 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)


def adjust_gamma(image, gamma):
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")

    return cv2.LUT(image, table)


def scale_contour(cnt, scale):
    M = cv2.moments(cnt)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])

    cnt_norm = cnt - [cx, cy]
    cnt_scaled = cnt_norm * scale
    cnt_scaled = cnt_scaled + [cx, cy]
    cnt_scaled = cnt_scaled.astype(np.int32)

    return cnt_scaled


def main():
    i = 0
    thresh = 195
    # min_threshold = 10  # these values are used to filter our detector.
    # max_threshold = 100  # they can be tweaked depending on the camera distance, camera angle, ...
    # min_area = 20  # ... focus, brightness, etc.
    # min_circularity = 0.3
    # min_inertia_ratio = 0.5

    while True:
        image_name = 'Original image no ' + str(i + 1)
        cv2.namedWindow(image_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(image_name, 900, 600)
        cv2.moveWindow(image_name, 600, 100)

        image_name_dots = 'Processed image (dots) no ' + str(i + 1)
        cv2.namedWindow(image_name_dots, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(image_name_dots, 450, 300)
        cv2.moveWindow(image_name_dots, 0, 0)

        image_name_dices = 'Processed image (dices) no ' + str(i + 1)
        cv2.namedWindow(image_name_dices, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(image_name_dices, 450, 300)
        cv2.moveWindow(image_name_dices, 0, 500)

        original_image = cv2.imread('src\\Photos\\' + header + str(i + 1) + ender + '.jpg', cv2.IMREAD_COLOR)
        original_image = rescale_frame(original_image, 25)
        gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
        # looking for dots
        blurred_image = cv2.GaussianBlur(gray_image, (15, 15), 0)
        thresh_image = cv2.adaptiveThreshold(blurred_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 1)
        kernel = np.ones((5, 5), np.uint8)
        eroded_image = cv2.erode(thresh_image, kernel, iterations=1)
        dilated_image = cv2.dilate(eroded_image, kernel, iterations=1)
        contours, hierarchy = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # looking for cubes edges
        blurred_image = cv2.GaussianBlur(gray_image, (15, 15), 0)
        dilated_image2 = cv2.dilate(blurred_image, kernel, iterations=1)
        canny = cv2.Canny(dilated_image2, 80, 200)
        _, thresh_image2 = cv2.threshold(canny, 100, 255, cv2.THRESH_BINARY)
        try:
            dots_coordinates = []
            for j in range(len(contours)):
                area = cv2.contourArea(contours[j])
                perimeter = cv2.arcLength(contours[j], True)
                contours[j] = scale_contour(contours[j], 1.1)
                if perimeter == 0:
                    break
                circularity = 4 * math.pi * (area / (perimeter * perimeter))
                if 0.6 < circularity and 1000 / 16 < area < 10000 / 16:
                    x = []
                    y = []
                    color = []
                    for k in range(len(contours[j])):
                        x.append(contours[j][k][0][1])
                        y.append(contours[j][k][0][0])
                        color.append(int(gray_image[contours[j][k][0][1], contours[j][k][0][0]]))
                    if int(gray_image[mean(x), mean(y)]) < 150 and mean(color) > 100:
                        cv2.drawContours(original_image, contours, j, (0, 0, 255), 3)
                        dots_coordinates.append([mean(x), mean(y)])
                        if hierarchy[0][j][3] >= 0:
                            cv2.drawContours(original_image, contours, hierarchy[0][j][3], (255, 0, 0), 2)
            print(dots_coordinates)
            cv2.imshow(image_name, original_image)
            cv2.imshow(image_name_dots, thresh_image)
            cv2.imshow(image_name_dices, thresh_image2)
        except:
            print("error, something went wrong :/")
            i = i+1
            continue
        key = cv2.waitKey(0)
        if key == 27:  # ESCAPE
            sys.exit()
        elif key == 100:  # D
            if i < amount_of_pictures - 1:
                i = i + 1
            else:
                i = 0
        elif key == 97:  # A
            if i != 0:
                i = i - 1
            else:
                i = amount_of_pictures - 1
        elif key == 101:  # E
            thresh = thresh + 5
            print('thresh = ', thresh)
        elif key == 113:  # Q
            thresh = thresh - 5
            print('thresh = ', thresh)
        elif key == 49: #1
            print(i, " : Good")
        elif key == 50: #2
            print(i, " : I cant see dice contour")
        elif key == 51: #3
            print(i, " : I can see to many pips")
        elif key == 52: #4
            print(i, " : Bad photo")

        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
