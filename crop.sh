#!/bin/sh
cd $1
mogrify -crop 274x202+19+45 +repage *
