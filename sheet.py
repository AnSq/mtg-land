#!/usr/bin/env python

import sys
import os
import subprocess
from PIL import Image

import util


wubrg = "WUBRG"
target_dir = "docs/card_sheets"


def main(folder):
    util.init_docs()

    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    img_list = os.listdir(folder)

    with Image.open(os.path.join(folder, img_list[0])) as card_img:
        card_width  = card_img.width
        card_height = card_img.height

    scale_factor = 120.0 / card_width

    print "card size: %dx%d" % (card_width, card_height)
    print

    img_colors = {c:[] for c in wubrg}
    coords = {}

    for i in img_list:
        img_colors[i[0]].append(os.path.join(folder, i))

    with open("docs/cards.css", "w") as f:
        for c in wubrg:
            print c + "..."

            sheet_path = os.path.join(target_dir, c + ".jpg")
            img_colors[c].sort()

            subprocess.call(["montage"] + img_colors[c] + ["-geometry", "+0+0", "-quality", "85", sheet_path])

            with Image.open(sheet_path) as im:
                width  = im.width
                height = im.height

            print "\t%dx%d pixels" % (width, height)

            num_width  = width  / card_width
            num_height = height / card_height

            print "\t%dx%d cards" % (num_width, num_height)

            for i, fname in enumerate(img_colors[c]):
                x_card_offset = i %  num_width
                y_card_offset = i // num_width

                x_pixel_offset = x_card_offset * card_width
                y_pixel_offset = y_card_offset * card_height

                x_scaled_offset = int(x_pixel_offset * scale_factor)
                y_scaled_offset = int(y_pixel_offset * scale_factor)

                card_code = fname.split("/")[-1].split(".")[0]
                coords[card_code] = (x_scaled_offset, y_scaled_offset)

            f.write(".card.color_%s .img {background-size: %dpx %dpx;}\n" % (c.lower(), width * scale_factor, height * scale_factor))

        print "\nGenerating stylesheet..."

        for card_code in sorted(coords):
            f.write("#%s + label > .img {background-position: -%dpx -%dpx;}\n" % (card_code, coords[card_code][0], coords[card_code][1]))


if __name__ == "__main__":
    main(sys.argv[1])
