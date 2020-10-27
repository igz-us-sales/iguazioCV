FROM python:3.6-jessie
RUN pip install opencv-python v3io_frames requests
RUN mkdir /video_capture
COPY video_capture.py /video_capture/video_capture.py
ENTRYPOINT /video_capture/video_capture.py