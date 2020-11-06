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

import yaml
with open("client_config.yaml") as f:
    config = yaml.safe_load(f)

url = f"{config['v3io']['webapi']}/{config['project']['container']}/{config['stream']['raw_video_stream']}/"    

headers = {
    "Content-Type": "application/json",
    "X-v3io-function": "PutRecords",
    "X-v3io-session-key": config['v3io']['access_key']
}

def stream_frame_write(cameraID, payload):
    print("stream_frame_write called")
    bef = time.time()
    r = requests.post(url, headers=headers, json=payload, verify=False)
    time_diff = time.time() - bef
    print("Post time %s. Response %s" % (time_diff, r.text))
    return r.text


def start_capture():
    print("start capture")

    # To capture video from webcam
    cap = cv2.VideoCapture(config['camera']['url'])

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
            Records.append({"Data": data.decode("utf-8"), "ShardId": config['stream']['shard_id']})

            if data_count == 60:
                try:
                    payload = {"Records": Records}
                    r = stream_frame_write(config['camera']['id'], payload)
                    print(r)
                except:
                    print("Failed to write to shard %s" % shard)
                data_count = 1
                Records = []
            data_count += 1

    # Release the VideoCapture object
    cap.release()


def get_cameras_list():
    client = v3f.Client(config['v3io']['frames'], container=config['project']['container'])
    df = client.read("kv", config['camera']['list_table'])
    return df


def init_function():
    cameraID = config['camera']['id']
    shardId = int(config['stream']['shard_id'])
    cameraURL = config['camera']['url']

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
            start_capture()
    print("Invalid camera")


init_function()