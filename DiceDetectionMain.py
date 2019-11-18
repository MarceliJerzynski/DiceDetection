import math
import sys
import cv2
import numpy as np
from statistics import mean
from glob import glob

files = glob('src/Photos/*.jpg')
number_of_pictures = len(files)


def distance(p1, p2):
    return math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))


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
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])

    cnt_norm = cnt - [cx, cy]
    cnt_scaled = cnt_norm * scale
    cnt_scaled = cnt_scaled + [cx, cy]
    cnt_scaled = cnt_scaled.astype(np.int32)

    return cnt_scaled


def main():
    i = 0
    while True:
        image_name = 'Image no ' + str(i + 1)
        cv2.namedWindow(image_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(image_name, 900, 600)
        cv2.moveWindow(image_name, 600, 100)

        original_image = cv2.imread(files[i], cv2.IMREAD_COLOR)
        print('File ' + files[i])
        to_show = original_image.copy()
        to_show_before = to_show.copy()
        original_image = rescale_frame(original_image, 25)
        if original_image.shape[0] > original_image.shape[1]:
            original_image = cv2.rotate(original_image, cv2.ROTATE_90_CLOCKWISE)
            to_show = cv2.rotate(to_show, cv2.ROTATE_90_CLOCKWISE)
            to_show_before = cv2.rotate(to_show_before, cv2.ROTATE_90_CLOCKWISE)
        gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
        # looking for dots
        blurred_image = cv2.GaussianBlur(gray_image, (15, 15), 0)
        thresh_image = cv2.adaptiveThreshold(blurred_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 1)
        kernel = np.ones((5, 5), np.uint8)
        eroded_image = cv2.erode(thresh_image, kernel, iterations=1)
        dilated_image = cv2.dilate(eroded_image, kernel, iterations=1)
        contours, hierarchy = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        dots_coordinates = []
        dots = []
        for j in range(len(contours)):
            area = cv2.contourArea(contours[j])
            perimeter = cv2.arcLength(contours[j], True)
            contours[j] = scale_contour(contours[j], 1.1)
            if perimeter == 0:
                break
            circularity = 4 * math.pi * (area / (perimeter * perimeter))
            if 0.8 < circularity and 1000 / 16 < area < 10000 / 16:
                x = []
                y = []
                color = []
                for k in range(len(contours[j])):
                    x.append(contours[j][k][0][1])
                    y.append(contours[j][k][0][0])
                    color.append(int(gray_image[contours[j][k][0][1], contours[j][k][0][0]]))
                if int(gray_image[mean(x), mean(y)]) < 150 and mean(color) > 100:
                    for contour in contours[j]:
                        contour[:, 0] = contour[:, 0] * 4
                        contour[:, 1] = contour[:, 1] * 4
                    cv2.drawContours(to_show, contours, j, (0, 0, 255), 12)
                    dots_coordinates.append([mean(x), mean(y)])
                    dots.append(contours[j])

        dices = list()
        for coord in dots_coordinates:
            dice = list()
            # print('coord: ' + str(coord))
            for other_coord in dots_coordinates:
                if distance(coord, other_coord) < 100:
                    dice.append(other_coord)
            dices.append(dice)


        print(len(dices))
        result = list()
        for dice in dices:
            if dice not in result:
                result.append(dice)

        results = 20 * [0]
        for dice in result:
            results[len(dice) - 1] += 1

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 3.2
        color = (0, 0, 255)
        thickness = 8
        alpha = 0.55

        overlay = to_show.copy()

        cv2.rectangle(to_show, (0, 0), (250 * 4, 230 * 4), (100, 100, 100), -1)

        cv2.addWeighted(overlay, 1 - alpha, to_show, alpha, 0, to_show)
        org = (10, 20 * 4 + 20)
        to_show = cv2.putText(to_show, "liczba jedynek: " + str(results[0]), org, font, font_scale, color, thickness, cv2.LINE_AA)
        org = (10, 60 * 4 + 20)
        to_show = cv2.putText(to_show, "liczba dwojek: " + str(results[1]), org, font, font_scale, color, thickness, cv2.LINE_AA)
        org = (10, 100 * 4 + 20)
        to_show = cv2.putText(to_show, "liczba trojek: " + str(results[2]), org, font, font_scale, color, thickness, cv2.LINE_AA)
        org = (10, 140 * 4 + 20)
        to_show = cv2.putText(to_show, "liczba czworek: " + str(results[3]), org, font, font_scale, color, thickness, cv2.LINE_AA)
        org = (10, 180 * 4 + 20)
        to_show = cv2.putText(to_show, "liczba piatek: " + str(results[4]), org, font, font_scale, color, thickness, cv2.LINE_AA)
        org = (10, 220 * 4 + 20)
        to_show = cv2.putText(to_show, "liczba szostek: " + str(results[5]), org, font, font_scale, color, thickness, cv2.LINE_AA)

        cv2.imshow(image_name, to_show_before)
        cv2.imwrite('out/' + str("{:02d}".format(i + 1)) + '.jpg', to_show)
        key = cv2.waitKey(0)

        if key == 13 or key == 32:  # enter or space
            cv2.imshow(image_name, to_show)
            key = cv2.waitKey(0)
        if key == 27:  # ESCAPE
            sys.exit()
        elif key == 100:  # d
            if i < number_of_pictures - 1:
                i = i + 1
            else:
                i = 0
        elif key == 97:  # a
            if i != 0:
                i = i - 1
            else:
                i = number_of_pictures - 1
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

