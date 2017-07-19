#!/bin/sh
echo "resizing images"
cd $1
mogrify -resize 120x *
