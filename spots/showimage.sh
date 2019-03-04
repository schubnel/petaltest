#!/bin/bash
fitsfile=$1
regionsfile="${fitsfile/fits/pos}"
ds9 $fitsfile -cmap bb -scale log -zoom to fit -regions -format xy $regionsfile &
