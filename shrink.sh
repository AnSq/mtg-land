#!/bin/sh
cd $1
mogrify -resize 120x -quality 80 *
