'''
    Arducam RAW Converter.

    Copyright (c) 2023-3 Arducam <http://www.arducam.com>.
    
    Author: Arducam <support@arducam.com>

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
    OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
    OR OTHER DEALINGS IN THE SOFTWARE.
'''

import numpy as np
import cv2
import argparse

bayer_order_maps = {
    "RGGB": cv2.COLOR_BayerBG2BGR,
    "GRBG": cv2.COLOR_BayerGB2BGR,
    "BGGR": cv2.COLOR_BayerRG2BGR,
    "GBRG": cv2.COLOR_BayerGR2BGR, 
    "GREY": 0,
}

bit_depth_maps = {
    "RAW10": 10,
    }

def unpack_mipi_raw10(byte_buf):
    data = np.frombuffer(byte_buf, dtype=np.uint8)
    # 5 bytes contain 4 10-bit pixels (5x8 == 4x10)
    b1, b2, b3, b4, b5 = np.reshape(
        data, (data.shape[0]//5, 5)).astype(np.uint16).T
    o1 = (b1 << 2) + ((b5) & 0x3)
    o2 = (b2 << 2) + ((b5 >> 2) & 0x3)
    o3 = (b3 << 2) + ((b5 >> 4) & 0x3)
    o4 = (b4 << 2) + ((b5 >> 6) & 0x3)
    unpacked = np.reshape(np.concatenate(
        (o1[:, None], o2[:, None], o3[:, None], o4[:, None]), axis=1),  4*o1.shape[0])
    return unpacked

def show(img):
    cv2.namedWindow("Arducam",0)
    # cv2.cvResizeWindow
    cv2.resizeWindow("Arducam", 640, 480)
    cv2.imshow("Arducam", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def save_image(img, name):
    cv2.imwrite(name, img)

def convert(args):
    input_name = args.input
    output_name = args.output
    width = args.width
    height = args.height
    cvt_code = bayer_order_maps[args.bayer_order]
    depth = 10
    data = np.fromfile(input_name, np.uint8)
    img = unpack_mipi_raw10(data)
    img = (img >> 2).astype(np.uint8)
    img = img.reshape(height, width)
    if cvt_code != 0:
        img = cv2.cvtColor(img, cvt_code)
    save_image(img, output_name)
    show(img)


def parse_cmdline():
    parser = argparse.ArgumentParser(description='Arducam RAW Converter.')

    parser.add_argument('-i', '--input', type=str, nargs=None, required=True,
                        help='Input file name.')
    parser.add_argument('-o', '--output', type=str, nargs=None, required=True,
                        help="Output file name.")
    parser.add_argument('--width', type=lambda x: int(x, 0), nargs=None, required=True,
                        help="Specified width.")
    parser.add_argument('--height', type=lambda x: int(x, 0), nargs=None, required=True,
                        help="Specified height.")
    parser.add_argument('-b', '--bayer-order', choices=list(bayer_order_maps.keys()), type=str, required=True,
                        help="Set bayer order.")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_cmdline()
    convert(args)
