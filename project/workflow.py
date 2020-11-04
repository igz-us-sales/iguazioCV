
import os
from kfp import dsl
from mlrun import mount_v3io
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)

funcs = {}

# Configure function resources and local settings
def init_functions(functions: dict, project=None, secrets=None):
    
    image = f"docker-registry.{os.getenv('IGZ_NAMESPACE_DOMAIN')}:80/{config['project']['docker_image']}"
    
    for fn in functions.values():
        
        # Set resources for jobs
        if fn.to_dict()["kind"] == "job":
            fn.spec.build.image = image
            
        # Set resources for nuclio functions
        elif fn.to_dict()["kind"] == "remote":
            fn.with_http(workers=1)
            fn.spec.base_spec['spec']['build']['baseImage'] = image
            fn.spec.base_spec['spec']['loggerSinks'] = [{'level': 'info'}]
            fn.spec.min_replicas = 1
            fn.spec.max_replicas = 1
        
        # Apply environment variables
        fn.set_env('V3IO_ACCESS_KEY', os.getenv('V3IO_ACCESS_KEY'))
        fn.set_env('V3IO_USERNAME', os.getenv('V3IO_USERNAME'))
        fn.set_env('IGZ_NAMESPACE_DOMAIN', os.getenv('IGZ_NAMESPACE_DOMAIN'))
        fn.set_env('RAW_VIDEO_STREAM', config['stream']['raw_video_stream'])
        fn.set_env('TAGGED_VIDEO_STREAM', config['stream']['tagged_video_stream'])
        fn.set_env('IGZ_CONTAINER', config['project']['container'])
        fn.set_env('CAMERA_LIST_TBL', config['camera']['list_table'])
        fn.set_env('CAMERA_ID', config['camera']['id'])
        fn.set_env('SHARD_ID', config['stream']['shard_id'])
        fn.set_env('CAMERA_URL', config['camera']['url'])
        fn.set_env('ROTATE_180', config['stream']['rotate_180'])
        fn.set_env('FACIAL_RECOGNITION_FUNCTION', config['api']['facial_recognition_function'])
        fn.set_env('GET_IMAGE_FUNCTION', config['api']['get_image_function'])
        fn.set_env('API_GATEWAY', config['api']['gateway'])
        fn.set_env('PROJECT', config['project']['name'])
        fn.set_env('IGZ_AUTH', config['api']['auth'])
        
        # Set default handler
        fn.spec.default_handler = "handler"
        
        # Apply V3IO mount
        fn.apply(mount_v3io())
        
    # Apply V3IO trigger
    facial_recognition_trigger_spec={
        'kind': 'v3ioStream',
        'url' : f"http://v3io-webapi:8081/{config['project']['container']}/{config['stream']['raw_video_stream']}@processorgrp",
        "password": os.getenv('V3IO_ACCESS_KEY'),  
        'attributes': {"pollingIntervalMs": 500,
            "seekTo": "earliest",
            "readBatchSize": 100,
            "partitions": "0-100",                          
          }
    }
    functions['deploy-facial-recognition'].add_trigger('image-proc', facial_recognition_trigger_spec)

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
    create_streams_tables = funcs['create-streams-tables'].as_step()
    
    # Deploy facial recognition
    facial_recognition = funcs['deploy-facial-recognition'].deploy_step(env={'RUN_ORDER' : create_streams_tables.outputs['run_id']})

    # Deploy image retrieval
    image_retrieval = funcs['deploy-image-retrieval'].deploy_step(env={'RUN_ORDER' : facial_recognition.outputs['endpoint']})

    # Create API gateway
    api_gateway = funcs['create-api-gateway'].as_step(params={'RUN_ORDER' : image_retrieval.outputs['endpoint']})
    
    # Create Grafana dashboard
    api_gateway = funcs['create-grafana-dashboard'].as_step(params={'RUN_ORDER' : api_gateway.outputs['run_id']})
