from extractComparisonFeatures.detectLines import get_detected_lines
from extractComparisonFeatures.our_utils.prepare_document import get_prepared_doc
import cv2
import sys


def main():
    if(len(sys.argv) < 2):
        print("Usage: python detectLines.py <file_name>")
        sys.exit(1)

    img_name = "data/" + str(sys.argv[1])
    img = get_prepared_doc(img_name)
    lines = get_detected_lines(img, img_name)

    # print(lines)
    # for line in lines:
    #     cv2.imshow('line', line)
    #     cv2.waitKey(0)

if __name__ == "__main__":
    main()