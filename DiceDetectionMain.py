import numpy as np
import cv2
import random
import sys
import argparse

amount_of_pictures = 14
header = 'd'


def adjust_gamma(image, gamma):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")

    return cv2.LUT(image, table)


def main():
    i = 0
    thresh = 170
    min_threshold = 10  # these values are used to filter our detector.
    max_threshold = 100  # they can be tweaked depending on the camera distance, camera angle, ...
    min_area = 20  # ... focus, brightness, etc.
    min_circularity = 0.3
    min_inertia_ratio = 0.5

    while( True ):

        image_name = 'Dices nr ' + str( i + 1 )
        cv2.namedWindow( image_name, cv2.WINDOW_NORMAL )
        cv2.resizeWindow( image_name, 900, 600 )
        cv2.moveWindow( image_name, 600, 100 )

        image_name_original = 'Original dices nr ' + str( i + 1 )
        cv2.namedWindow( image_name_original, cv2.WINDOW_NORMAL )
        cv2.resizeWindow( image_name_original, 450, 300 )
        cv2.moveWindow( image_name_original, 0, 100 )

        # params = cv2.SimpleBlobDetector_Params()  # declare filter parameters.
        # params.filterByArea = True
        # # params.filterByCircularity = True
        # # params.filterByInertia = True
        # # params.minThreshold = min_threshold
        # # params.maxThreshold = max_threshold
        # params.minArea = 12
        # params.minCircularity = min_circularity
        # params.minInertiaRatio = min_inertia_ratio

        # params = cv2.SimpleBlobDetector_Params()
        #
        # params.filterByArea = True
        # params.minArea = min_area
        #
        # params.filterByConvexity = True
        # params.minConvexity = obj.Convexity / 200

        # detector = cv2.SimpleBlobDetector_create(params)
        original_image = cv2.imread('src\\' + header + str(i+1) + '.jpg', cv2.IMREAD_COLOR)
        gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
        gray_image = 255 - gray_image
        # keypoints = detector.detect(gray_image)
        # print(len(keypoints))
        # endpoints_image = cv2.drawKeypoints(gray_image, keypoints, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS )

        noise_removal = cv2.bilateralFilter( gray_image, 9, 75, 75 )

        _, after_threshold = cv2.threshold( noise_removal, 70, 255, cv2.THRESH_OTSU )

        canny_image = cv2.Canny( after_threshold, 250, 255 )


        kernel = np.ones( (3, 3), np.uint8 )
        # Creating the kernel for dilation
        dilated_image = cv2.dilate( canny_image, kernel, iterations = 1 )

        contours, h = cv2.findContours( dilated_image, 1, 2 )
        contours = sorted( contours, key = cv2.contourArea, reverse = True )[:]

        cv2.drawContours(original_image, contours, -1, (0, 0, 255), 9)
        blurred_image = cv2.GaussianBlur(gray_image,(15,15), 0)
        thresh_image = cv2.adaptiveThreshold(blurred_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 1)
        kernel = np.ones((3,3), np.uint8)
        erosion_image= cv2.erode(thresh_image, kernel, iterations = 0)
        dilate_image = cv2.dilate( erosion_image, kernel, iterations = 3 )
        contours, hierarchy = cv2.findContours( dilate_image, 1, 2 )
        # print(len(contours))
        for j in range(len(contours)):
            # if (len(contours[j]) < 5 ):
            # ellipse = cv2.fitEllipse(contours[j])
            #     continue
            if ( 3500 < cv2.contourArea(contours[j])  ):# and hierarchy[0][j][3] == -1):
                cv2.drawContours(original_image, contours, j,  (0,0,25), 3)
            #     cv2.ellipse(original_image, ellipse, (0,255,0), 3)

        # erosion_image = cv2.erode( blurred_image2, kernel, iterations = 3 )
        # dilate_image = cv2.dilate( erosion_image, kernel, iterations = 3 )

        blurred_image2 = cv2.GaussianBlur( dilate_image, (5, 5), cv2.BORDER_DEFAULT )

        blurred_image3 = cv2.GaussianBlur(blurred_image2, (5, 5), cv2.BORDER_DEFAULT)

        blurred_image4 = cv2.GaussianBlur( blurred_image3, (5, 5), cv2.BORDER_CONSTANT )

        # erosion_image2 = cv2.erode(blurred_image4, kernel, iterations = 3)
        #
        # dilate_image2 = cv2.dilate( erosion_image2, kernel, iterations = 4 )
        # colored = cv2.cvtColor(blurred_image3, cv2.COLOR_GRAY2BGR)
        # houghed = cv2.HoughCircles(colored, cv2.HOUGH_GRADIENT, 1, 120, param1 = 100, param2 = 2, minRadius = 0, maxRadius = 0)
        # houghed = np.unit16(houghed)

        # circles = cv2.HoughCircles(blurred_image4, cv2.HOUGH_GRADIENT, 100, 30, minRadius = 0, maxRadius = 10)
        # circles = np.uint16(np.around(circles))
        median = cv2.medianBlur(blurred_image4, 3)
        median = 255 - median
        median = cv2.medianBlur( median, 5 )
        # median = cv2.erode(median, kernel, iterations = 3)
        median = cv2.medianBlur( median, 3 )
        median = cv2.medianBlur( median, 3 )
        median = cv2.medianBlur( median, 3 )
        median = cv2.medianBlur( median, 3 )
        median = cv2.medianBlur( median, 3 )
        median = cv2.erode(median, kernel, iterations = 2)

        median = cv2.dilate( median, kernel, iterations = 2 )

        # median = 255 - median

        # contours, hier = cv2.findContours( median, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE )
        # for cnt in contours:
        #     if 4000 < cv2.contourArea( cnt ) < 5000 and True:
        #         cv2.drawContours( original_image, [ cnt ], 0, (0, 255, 0), 2)

        cv2.imshow(image_name, median)
        # for i in circles[0, :]:
        #     cv2.circles(blurred_image4, (i[0], i[1]), i[2], (0, 255, 0), 2)
        #
        #     cv2.circles( blurred_image4, (i[ 0 ], i[ 1 ]), i[ 2 ], (0, 255, 0), 3 )
        #
        # cv2.imshow("Circle", original_image)
        # lower_black = np.array([0,0,0])
        # upper_black = np.array([140,140,140])
        #
        # dots = cv2.inRange(original_image, lower_black, upper_black)
        #
        # params = cv2.SimpleBlobDetector_Params()  # declare filter parameters.
        # params.filterByArea = True
        # params.filterByCircularity = True
        # params.filterByInertia = True
        # params.minThreshold = min_threshold
        # params.maxThreshold = max_threshold
        # params.minArea = 12
        # params.minCircularity = min_circularity
        # params.minInertiaRatio = min_inertia_ratio
        #
        # params = cv2.SimpleBlobDetector_Params()
        #
        # detector = cv2.SimpleBlobDetector_create(params)
        # #original_image = cv2.imread( 'src\\' + header + str( i + 1 ) + '.jpg', cv2.IMREAD_COLOR )
        # #gray_image = cv2.cvtColor( original_image, cv2.COLOR_BGR2GRAY )
        # #gray_image = 255 - gray_image
        # keypoints = detector.detect(dots)
        # print(len(keypoints))
        # endpoints_image = cv2.drawKeypoints(original_image, keypoints, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS )
        #
        # noise_removal = cv2.bilateralFilter( endpoints_image, 9, 75, 75 )
        # gray = cv2.cvtColor(noise_removal, cv2.COLOR_BGR2GRAY)
        # _, after_threshold = cv2.threshold( gray, 70, 255, cv2.THRESH_OTSU )
        #
        # canny_image = cv2.Canny( after_threshold, 250, 255 )
        #
        #
        # kernel = np.ones( (3, 3), np.uint8 )
        # # Creating the kernel for dilation
        # dilated_image = cv2.dilate( canny_image, kernel, iterations = 1 )
        #
        # contours, h = cv2.findContours( dilated_image, 1, 2 )
        # contours = sorted( contours, key = cv2.contourArea, reverse = True )[:]
        #
        # cv2.drawContours(original_image, contours, -1, (0, 0, 255), 9)
        # cv2.imshow( image_name, dilated_image )
        # cv2.imshow( image_name_original, original_image)
        key = cv2.waitKey( 0 )
        if key == 27: # ESCAPE
            sys.exit()
        elif key == 100: #D
            if ( i < amount_of_pictures - 1):
                i = i + 1
            else:
                i = 0
        elif key == 97: #A
            if (i != 0):
                i = i - 1
            else:
                i = amount_of_pictures - 1
        elif key == 101:  # E
            thresh = thresh + 5
            print('thresh = ', thresh )
        elif key == 113:  # Q
            thresh = thresh - 5
            print('thresh = ', thresh )

        cv2.destroyAllWindows()



if __name__ == '__main__':
    main()