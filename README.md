# SMA smart watches watch face editor

The goal of this project is to allow to create and modify watch faces for [SMA-based](https://www.smawatch.com/) smart watches.
Currently, code is developed with help of [Trevi T-Fit 400 C](https://www.trevi.it/catalog/articolo/146-smartwatch/yombjekdjj-t-fit-400-c-smart-fitness-band-curve-nero.html).

## Prerequisites

Python >= 3.10 is required.
There is `requirements.txt` file which provides required Python packages to run the scripts.

## Format

The watch face data format is described in [`smawf.py`](smawf.py) script.
TODO: describe data format.

## Decompressor

The first tool developed while looking at the watch face data format is [`decompress.py`](decompress.py), which allows to extract all the image resources from watch face file.
Example to extract the images from file `wf.bin` in directory `wf`:
```
python decompress.py -i wf.bin
```

## Watch faces

The directory `watch_face` currently contains watch faces extracted from the app.
