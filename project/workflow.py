
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
    
    # Custom docker image with cv2 and grafwiz
#     image = f"docker-registry.{os.getenv('IGZ_NAMESPACE_DOMAIN')}:80/{os.getenv('DOCKER_IMAGE')}"

    # Create streams and tables
    setup = funcs['create-streams-tables'].as_step(outputs=['raw_video_stream_url', 'tagged_video_stream_url'])
    
    # Deploy facial recognition
    # Note: image specified in function yaml due to nuclio syntax differences
    deploy = funcs['deploy-facial-recognition'].deploy_step(env={'TAGGED_VIDEO_STREAM_URL' : setup.outputs['tagged_video_stream_url']})

    
#     # Create data bunches
#     bunches = funcs['create-data-bunches'].as_step(
#         name="create-data-bunches",
#         handler='create_data_bunches',
#         inputs={'data_path': ingest.outputs['data'], 'split' : split},
#         outputs=['data_lm', 'data_clas'],
#         image=image)
    
#     # Language model Hyperparameters
#     hyperparams = {"bs" : hyper_lm_bs,
#                    "drop_mult" : hyper_lm_drop_mult}
    
#     params = {"epochs" : hyper_lm_epochs,
#               "num_samples" : data_size,
#               "data_lm_path" : bunches.outputs['data_lm']}
    
#     # Language model Hyperparameter tuning
#     hyper_tune_lm = funcs['hyper-lm'].as_step(
#         name="hyper-lm",
#         handler='train_lm_model',
#         params=params,
#         hyperparams=hyperparams,
#         selector='max.accuracy',
#         outputs=['best_params'],
#         image=image)
    
#     # Language model training
#     train_lm = funcs['train-lm'].as_step(
#         name="train-lm",
#         handler='train_lm',
#         inputs={'train_lm_epochs': train_lm_epochs,
#                 'data_lm_path' : bunches.outputs['data_lm'],
#                 'num_samples' : data_size,
#                 'hyper_lm_best_params_path' : hyper_tune_lm.outputs['best_params']},
#         outputs=['train_lm_model', 'train_lm_model_enc', 'train_lm_accuracy'],
#         image=image)
    
#     # Classification model Hyperparameters
#     hyperparams = {"bs" : hyper_clas_bs,
#                    "thresh" : hyper_clas_thresh,
#                    "drop_mult" : hyper_clas_drop_mult}
    
#     params = {"epochs" : hyper_clas_epochs,
#               "num_samples" : data_size,
#               "encodings" : train_lm.outputs['train_lm_model_enc'],
#               "data_clas_path" : bunches.outputs['data_clas']}
    
#     # Classification model Hyperparameter tuning
#     hyper_tune_clas = funcs['hyper-clas'].as_step(
#         name="hyper-clas",
#         handler='train_clas_model',
#         params=params,
#         hyperparams=hyperparams,
#         selector='max.fbeta',
#         outputs=['best_params'],
#         image=image)
    
#     # Classification model training
#     train_clas = funcs['train-clas'].as_step(
#         name="train-clas",
#         handler='train_clas',
#         inputs={'train_clas_epochs': train_clas_epochs,
#                 'data_clas_path' : bunches.outputs['data_clas'],
#                 'num_samples' : data_size,
#                 'encodings' : train_lm.outputs['train_lm_model_enc'],
#                 'hyper_clas_best_params_path' : hyper_tune_clas.outputs['best_params']},
#         outputs=['train_clas_model', 'train_clas_fbeta'],
#         image=image)

#     # Serve model
#     deploy = funcs['model-server'].deploy_step(env={'DATA_CLAS_PATH' : bunches.outputs['data_clas'],
#                                                    'MODEL_PATH' : train_clas.outputs['train_clas_model'],
#                                                    f'SERVING_MODEL_{model_endpoint_name}': train_clas.outputs['train_clas_model'],
#                                                    'NUM_PREDS' : num_preds})

#     # Model serving tester
#     tester = funcs['model-server-tester'].as_step(
#         name='model-tester',
#         inputs={'model_endpoint': deploy.outputs['endpoint'],
#                 'model_name' : model_endpoint_name,
#                 'data_size' : data_size,
#                 'data_path' : ingest.outputs['data'],
#                 'num_tests' : num_tests})
