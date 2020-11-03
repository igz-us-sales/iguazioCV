# Facial Recognition Demo
This demo showcases the Iguazio Data Science Platform's abilities for real-time streaming and object detection. The demo is in the form of a Kubeflow pipeline that will deploy the following components.

## Pipeline Components Overview

1. `create-streams-tables` (MLRun Job): Will create two V3IO streams for raw incoming video data and for processed video data. Will also create a KV table to store information on the camera used.
2. `deploy-facial-recognition` (Nuclio Function): Will deploy a serverless nuclio function triggered by each frame of the raw video stream. This function will perform facial recognition via a Haar Cascade classifiers using CV2. The function will also write the video frames (with an overlaid bounding box for the faces) to an output stream for processed video data.
3. `deploy-image-retrieval` (Nuclio Function): Will deploy an endpoint to retrieve the latest image from a given video data stream.
4. `create-api-gateway` (MLRun Job): Will create an API gateway for the `deploy-image-retrieval` function. This will allow the Nuclio function to be invoked via a custom named public URL endpoint instead of a public IP.
5. `create-grafana-dashboard` (MLRun Job): Will create a Grafana Dashboard to consume images from V3IO video streams via AJAX calls to the previously deployed API gateway. Displays both raw video stream and processed video stream with facial recognition.

The demo also includes a client script to write local webcam footage to the raw V3IO video stream for processing within the Iguazio Platform.

## Getting Started

### Server Side (Iguazio Platform)
1. Open Jupyter service, clone GitHub repo, and open directory.
3. Duplicate `components/util/creds_template.py` as `components/util/creds.py` and populate with:
    - Iguazio Platform Password as `IGZ_AUTH` (required for `create-api-gateway`).
    - URL for Camera as `CAMERA_URL`. This step is required to prevent uploading credentials to source control.
    - *Note that `CAMERA_URL` will be a local IP address to the client as the client will be pushing to the raw V3IO video stream. This will be setup on the Client Side.*
3. Deploy Grafana service in the `Services` tab on the left-hand side of the Platform Dashboard.
4. Run `components/client/BuildVideoCaptureScript.ipynb`. This will create a client script `video_capture.py` with the required environment variables.
5. Setup Client Side Camera Stream (see below)
6. Run `FacialRecognitionDemo.ipynb` notebook to launch Kubeflow Pipeline.
8. Open Grafana service and find `Facial Recognition Demo Streams` dashboard and view outputs of both streams.

### Client Side (Local Machine)
1. [Setup Camera Stream](docs/CameraStreamViaVLC.md) from Webcam.
2. Download previously created `components/client/video_capture.py` from Iguazio Platform onto local machine.
3. Run `video_capture.py` on local machine to write webcam footage to V3IO raw video stream.