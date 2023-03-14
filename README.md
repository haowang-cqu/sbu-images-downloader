# A Multi-Threading Downloader for SBU Captions Dataset Images

[SBU Captions Dataset](https://www.cs.rice.edu/~vo9/sbucaptions/) is a collection of associated captions and images from Flickr. However, the authors only provide a [list of image URLs](https://www.cs.rice.edu/~vo9/sbucaptions/sbu-captions-all.tar.gz), which is not very convenient for downloading. This repository provides a multi-threading downloader for the images. 

## Features
- Multi-threading
- Automatically skip the images that have been downloaded
- Check the integrity of downloaded images
- Output the successfully downloaded images and captions as csv file

## Quick Start
Clone this repository and install dependencies:
```bash
git clone https://github.com/haowang-cqu/sbu-images-downloader.git
pip install -r requirements.txt
```
Download the metadata which contains the URLs of images and captions:
```bash
curl -O https://www.cs.rice.edu/~vo9/sbucaptions/sbu-captions-all.tar.gz
tar -xvf sbu-captions-all.tar.gz
```
Download the images:
```bash
python download.py
# you can use `python download.py -h` to see the usage
```
If your download is interrupted, you can resume it by re-running the above command. The downloader will automatically skip the images that have been downloaded.
