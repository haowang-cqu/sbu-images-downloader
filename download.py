# Download images with multithreading
import io
import os
import json
import requests
import argparse
from PIL import Image
from tqdm import tqdm
import pandas as pd
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from collections import Counter

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'

progress = [0, 0, 0]  # exists, succeeded, failed
pbar = None
result_df = pd.DataFrame(columns=['image', 'width', 'height', 'user_id', 'caption'])
mutex = Lock()


def fetch_single_image(image_url, timeout=None, retries=0):
    for _ in range(retries + 1):
        try:
            response = requests.get(image_url, timeout=timeout, headers={'user-agent': USER_AGENT}, allow_redirects=True)
            # check if the image is valid
            image = Image.open(io.BytesIO(response.content))
            break
        except Exception:
            image = None
            response = None
    return image, response


def parse_args():
    parser = argparse.ArgumentParser(prog='SBU Downloader', description='fetch SBU Captions Dataset images')
    parser.add_argument('-c', '--captions', type=str, default='sbu-captions-all.json', help='path to captions json file')
    parser.add_argument('-o', '--output', type=str, default='images', help='path to output directory')
    parser.add_argument('-t', '--timeout', type=int, default=5, help='timeout for fetching images')
    parser.add_argument('-r', '--retries', type=int, default=3, help='number of retries for fetching images')
    parser.add_argument('--result', type=str, default='result.csv', help='path to result csv file')
    parser.add_argument('--max_workers', type=int, default=64, help='max workers for multithreading')
    return parser.parse_args()


def check_exists(image_file_name, output):
    image_file_path = os.path.join(output, image_file_name)
    image = None
    if os.path.exists(image_file_path):
        try:
            # check if the image is valid
            image = Image.open(image_file_path)
        except Exception:
            image = None
    return image


def action(image_url, user_id, caption, args):
    image_file_name = image_url.split('/')[-1]
    image = check_exists(image_file_name, args.output)
    status = -1
    if image is not None:
        status = 0 # exists
    else:
        image, response = fetch_single_image(image_url, timeout=args.timeout, retries=args.retries)    
        if image is not None:
            with open(os.path.join(args.output, image_file_name), 'wb') as fp:
                fp.write(response.content)
            status = 1 # succeeded
        else:
            status = 2 # failed
    mutex.acquire()
    if image is not None:
        result_df.loc[len(result_df)] = [image_file_name, image.width, image.height, user_id, caption]
    progress[status] += 1
    pbar.set_postfix(exists=progress[0], succeeded=progress[1], failed=progress[2])
    pbar.update(1)
    mutex.release()
    return status


def main():
    args = parse_args()
    if not os.path.exists(args.output):
        os.mkdir(args.output)
    with open(args.captions, 'r') as fp:
        captions_all = json.load(fp)
    image_urls = captions_all['image_urls']
    user_ids = captions_all['user_ids']
    captions = captions_all['captions']
    # create thread pool
    global pbar
    pbar = tqdm(total=len(image_urls), dynamic_ncols=True)
    pbar.set_postfix(exists=progress[0], succeeded=progress[1], failed=progress[2])
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        result = executor.map(action, image_urls, user_ids, captions, [args] * len(image_urls))
    pbar.close()
    counter = Counter(result)
    print(counter)
    result_df.to_csv(args.result, index=False)


if __name__ == '__main__':
    main()
