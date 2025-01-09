#!/bin/python
#
# MIT License
#
# Copyright (c) 2022 EASE lab, University of Edinburgh
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Author: David Schall

import requests
import json
import tarfile
from tqdm import tqdm
import os
import sys
import tarfile
import shutil
import logging as log


RESOURCES = os.environ.get('RESOURCES', './')
if RESOURCES == "./":
    log.warning(" 'RESOURCES' variable not set!!")


import argparse

parser = argparse.ArgumentParser(description="Script to up and download release assets")
parser.add_argument("--file", default=f"~/gem5-svr-bench/image/release.json",
                    help="Path to the release file. Default 'resources/release.json'")
parser.add_argument("--download","-d", default=False, action="store_true", help = "Download release assets")
# parser.add_argument("--upload","-u", default=False, action="store_true", help = "Upload release assets")
parser.add_argument("--version", "-v", type=str, default="latest", help="Set version from where to download")
parser.add_argument("--output", "-o", type=str, default=f"/users/Lakshman/gem5-svr-bench/image/",
                    help="Output directory to store the assets to. Default: 'resources/'")
parser.add_argument("--os-version", "-l", type=str, default="jammy", choices=["focal", "jammy"],
                    help="The ubuntu version of the disk image and kernel")
parser.add_argument("--arch", "-a", type=str, default="arm64", choices=["amd64", "arm64"],
                    help="The target architecture")
args = parser.parse_args()


def download(f,url):
    # Streaming, so we can iterate over the response.
    response = requests.get(url, stream=True)
    total_size_in_bytes= int(response.headers.get('content-length', 0))
    # print(total_size_in_bytes)
    block_size = 1024 #1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

    # response.raw.read(block_size)
    for data in response.iter_content(block_size):
        progress_bar.update(len(data))
        f.write(data)

    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        log.error("ERROR, something went wrong")



def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

# pigz -cd tmp2.tar.gz | tar xf -
# rm tmp2.tar.gz
import subprocess
import time

def decompressParallel(tar_file):
    print(f"Decompress file: {tar_file}")
    # args = ["tar", "--use-compress-program=pigz", "xf" "-cf", tar_file, file]
    # subprocess.call(args=args)
    # p = subprocess.Popen(args)
    ps = subprocess.Popen(["pigz", "-cd", tar_file], stdout=subprocess.PIPE)
    ps2 = subprocess.Popen(['tar', 'xf', '-'], stdin=ps.stdout)

    spinner = spinning_cursor()
    while ps.poll() is None and ps2.poll() is None:
        sys.stdout.write('\r')
        sys.stdout.write("Decompressing... " + next(spinner))
        sys.stdout.flush()
        time.sleep(0.2)

## Download disk
def downloadDiskImage(asset_urls):
    tmpfile="disk.tmp"
    # progress = tqdm(range(len(urls)+1))
    with open(tmpfile,'wb') as f:
        for i,url in enumerate(asset_urls):
            name = url.split("/")[-1]
            print(f"Download: {i+1}/{len(asset_urls)} " + name)
            # progress.set_description("Download %s: %s" % (i, name))
            download(f,url)

    # print("Extract Disk: ")
    # my_tar = tarfile.open(tmpfile,"r:gz")
    # my_tar.extractall("") # specify which folder to extract to
    # my_tar.close()
    decompressParallel(tmpfile)
    os.remove(tmpfile)


def downloadAsset(asset_url):
    name = asset_url.split("/")[-1]
    print("Download: " + name)
    with open(name,"wb") as f:
        download(f,asset_url)


## Get the release info
def get_latest_release():
    RELEASES_API = "https://api.github.com/repos/vhive-serverless/vSwarm-u/releases/latest"

    print("Releases API: " + RELEASES_API)
    headers = {}
    response = requests.get(RELEASES_API, headers=headers)

    # print("debug: " + str(response.status_code))

    RELEASE = response.json()
    # with open("rel.json", "w") as f:
    #     json.dump(RELEASE, f)
    RELEASES_LEN = len(RELEASE)
    return RELEASE

def get_release(tag_name="latest"):
    if tag_name =="latest":
        return get_latest_release()

    RELEASES_API = "https://api.github.com/repos/vhive-serverless/vSwarm-u/releases"
    print("Releases API: " + RELEASES_API)
    headers = {}
    response = requests.get(RELEASES_API, headers=headers)

    print("debug: " + str(response.status_code))

    RELEASES = response.json()
    # with open("rel.json", "w") as f:
    #     json.dump(RELEASES, f)
    RELEASES_LEN = len(RELEASES)

    for i in range(0, RELEASES_LEN):
        if RELEASES[i]["tag_name"] == tag_name:
            RELEASES_NUMBER = i
            break
    try:
        print(
            f"Found the target tagname '{tag_name}', " + str(RELEASES_NUMBER))
    except:
        print(f"Can't found the target tagname '{tag_name}'")
        sys.exit(1)

    return RELEASES[RELEASES_NUMBER]


def get_assets(release):
    # print(release["assets"])
    assets = []
    for a in release["assets"]:
        assets += [{"name": a["name"], "url": a["browser_download_url"]}]

    return assets


def get_version(release):
    return release["tag_name"]


def get_url(release, name):
    for a in release["assets"]:
        if name in a["name"]:
            return a["browser_download_url"]
    return None


def get_urls(release, name=""):
    urls = []
    for a in release["assets"]:
        if "sums" in a["name"]:
            continue
        if name in a["name"]:
            urls += [a["browser_download_url"]]
    return urls




def downloadMoveAssets(version="latest"):

    if version == "latest":
        release=get_latest_release()
    else:
        release=get_release(version)

    print(f"Download Artifacts from version: {get_version(release)}")
    name = f"vmlinux-{ args.os_version }-{ args.arch }"
    kernel_url = get_url(release=release,name=name)
    print(kernel_url)
    if kernel_url == None:
        raise Exception("kernel not found!: " + name)
    downloadAsset(kernel_url)

    name = f"test-client-{ args.arch }"
    client_url = get_url(release=release,name=name)
    if client_url == None:
        raise Exception("client not found!: " + name)
    downloadAsset(client_url)

    disk_name = f"disk-image-{ args.os_version }-{ args.arch }.qcow2"
    disk_urls = get_urls(release=release,name=disk_name)
    if len(disk_urls) == None:
        raise Exception("disk-image not found!: " + name)

    print("Download Disk image.. This could take a few minutes")
    downloadDiskImage(disk_urls)

    ## Move assets to destination
    print("Copy artifacts to: " + args.output)
    name, artifact_name = "kernel", kernel_url.split("/")[-1]
    shutil.move(artifact_name, args.output)
    name, artifact_name = "client", client_url.split("/")[-1]
    shutil.move(artifact_name, args.output)
    # name, artifact_name = "disk-image.qcow2", disk_urls[0].split("/")[-1].split(".")[0]
    # The disk remains in the temp folder.
    name, source_path = "disk-image.qcow2", "temp/disk-image.qcow2"
    shutil.move(source_path, args.output)

def downloadAssets():
    with open(args.file) as f:
        artifacts = json.load(f)

    release=get_latest_release()
    print("Download Artifacts")
    name = "vmlinux"
    url = get_url(release=release,name=name)
    downloadAsset(url)

    name = "client"
    url = get_url(release=release,name=name)
    downloadAsset(url)

    name = "disk-image"
    urls = get_urls(release=release,name=name)
    print("Download Disk image.. This could take a few minutes")
    downloadDiskImage(urls)

def moveAssets():
    with open(args.file) as f:
        artifacts = json.load(f)

    ## Move assets to destination
    print("Copy artifacts to: " + args.output)
    name, artifact_name = "kernel", artifacts["kernel"].split("/")[-1]
    shutil.move(artifact_name, args.output + name)
    name, artifact_name = "client", artifacts["client"].split("/")[-1]
    shutil.move(artifact_name, args.output + name)
    name, artifact_name = "disk-image.qcow2", artifacts["disk-image"][0].split("/")[-1].split(".")[0]
    shutil.move(artifact_name, args.output + name)


def getVersion():
    with open(args.file) as f:
        artifacts = json.load(f)
        print(artifacts["tag_name"])


if __name__ == '__main__':
    downloadMoveAssets(args.version)
