#!/usr/bin/env python
# coding: utf-8

import base64
import os
import sys
import time

import cv2
import requests
import urllib3
import v3io_frames as v3f
from cv2 import VideoWriter, VideoWriter_fourcc

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

os.environ["V3IO_ACCESS_KEY"] = "XXXXXXXXXXXX"
os.environ["V3IO_USERNAME"] = "XXXX"
os.environ[
    "V3IO_WEBAPI"
] = "https://webapi.default-tenant.app.XXXXXXXXXXX.com"
os.environ[
    "V3IO_FRAMES"
] = "https://framesd.default-tenant.app.XXXXXXXX.com"
os.environ["IGZ_CONTAINER"] = "bigdata"
os.environ["RAW_VIDEO_STREAM"] = "videostream"
os.environ["CAMERA_LIST_TBL"] = "camera_list"
os.environ["shardId"] = "0"
os.environ["cameraID"] = "0"
os.environ["cameraURL"] = "http://XXX.XXX.0.XXX:XXXX"


url = "%s/%s/%s/" % (
    os.getenv("V3IO_WEBAPI"),
    os.getenv("IGZ_CONTAINER"),
    os.getenv("RAW_VIDEO_STREAM"),
)
headers = {
    "Content-Type": "application/json",
    "X-v3io-function": "PutRecords",
    "X-v3io-session-key": os.getenv("V3IO_ACCESS_KEY"),
}


def stream_frame_write(cameraID, payload):
    print("stream_frame_write called")
    bef = time.time()
    r = requests.post(url, headers=headers, json=payload, verify=False)
    time_diff = time.time() - bef
    print("Post time %s. Response %s" % (time_diff, r.text))
    return r.text


def start_capture(cameraID: str, cameraURL: str, shard: int):
    print("start capture")

    # To capture video from webcam
    cap = cv2.VideoCapture(cameraURL)

    # To use a video file as input
    # cap = cv2.VideoCapture('filename.mp4')
    data_count = 1
    while True:

        fourcc = VideoWriter_fourcc(*"MPEG")
        running_size = 0
        Records = []
        while cap.isOpened():
            print(f"capture opened - {len(Records)}")
            ret, img = cap.read()
            ret, buffer = cv2.imencode(".jpg", img)
            data = base64.b64encode(buffer)
            Records.append({"Data": data.decode("utf-8"), "ShardId": shard})

            if data_count == 60:
                try:
                    payload = {"Records": Records}
                    r = stream_frame_write(cameraID, payload)
                    print(r)
                except:
                    print("Failed to write to shard %s" % shard)
                data_count = 1
                Records = []
            data_count += 1

    # Release the VideoCapture object
    cap.release()


def get_cameras_list():
    client = v3f.Client(os.getenv("V3IO_FRAMES"), container=os.getenv("IGZ_CONTAINER"))
    df = client.read("kv", os.getenv("CAMERA_LIST_TBL"))
    return df


def init_function():
    cameraID = os.getenv("cameraID")
    shardId = int(os.getenv("shardId"))
    cameraURL = os.getenv("cameraURL")

    if isinstance(cameraURL, int):
        cameraURL = int(cameraURL)

    cameras_list = get_cameras_list()
    print(cameras_list)
    for index, row in get_cameras_list().iterrows():
        if (
            index == cameraID
            and row["shard"] == shardId
            and row["url"] == cameraURL
            and row["active"] == True
        ):
            start_capture(cameraID, cameraURL, shardId)
    print("Invalid camera")


init_function()


# Variables needed for container operations
#
# V3IO_ACCESS_KEY
#
# V3IO_USERNAME
#
# V3IO_WEBAPI
#
# V3IO_FRAMES
#
# IGZ_CONTAINER
#
# RAW_VIDEO_STREAM
#
# CAMERA_LIST_TBL
#
# shardId
#
# cameraID
#
# cameraURL