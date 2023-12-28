#!/bin/bash

IMAGE_NAME=xls2csv

LOCAL_FOLDER=~/Downloads/Banks

docker run -v "$LOCAL_FOLDER:/inout" $IMAGE_NAME
