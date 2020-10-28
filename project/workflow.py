
import os
from kfp import dsl
from mlrun import mount_v3io

funcs = {}

# Configure function resources and local settings
def init_functions(functions: dict, project=None, secrets=None):
    for f in functions.values():
        f.apply(mount_v3io())

# Create a Kubeflow Pipelines pipeline
@dsl.pipeline(
    name="Facial Recognition Demo",
    description="Real-time facial recognition using Iguazio Data Science Platform, Nuclio, and MLRun"
)
def kfpipeline():
    # Note: Using env/params to order components as everything has been defined in environment variables.
    # "env" is the input for nuclio functions which output a function "endpoint"
    # "params" is the input for jobs which output a "run_id"

    # Create streams and tables
    create_streams_tables = funcs['create-streams-tables'].as_step(outputs=['tagged_video_stream_url', 
                                                                            'raw_video_stream_url'])
    
    # Deploy facial recognition
    facial_recognition = funcs['deploy-facial-recognition'].deploy_step(env={'RUN_ORDER' : create_streams_tables.outputs['run_id'],
                                                                             'TAGGED_VIDEO_STREAM_URL' : create_streams_tables.outputs['tagged_video_stream_url']})

    # Deploy image retrieval
    image_retrieval = funcs['deploy-image-retrieval'].deploy_step(env={'RUN_ORDER' : facial_recognition.outputs['endpoint']})

    # Create API gateway
    api_gateway = funcs['create-api-gateway'].as_step(params={'RUN_ORDER' : image_retrieval.outputs['endpoint']})
    
    # Create Grafana dashboard
    api_gateway = funcs['create-grafana-dashboard'].as_step(params={'RUN_ORDER' : api_gateway.outputs['run_id']})
