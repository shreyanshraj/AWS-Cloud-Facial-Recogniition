import os
import boto3
import torch
import cv2
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
from botocore.exceptions import ClientError
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Set environment variables for cache directories
os.environ['TORCH_HOME'] = '/tmp'

def face_recognition_function(image_path, data_path):
    logger.info(f"Starting face recognition for image: {image_path}")
    try:
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Failed to read image: {image_path}")

        # Initialize models with error handling
        try:
            mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20)
            # resnet = InceptionResnetV1(pretrained='vggface2').eval()
            resnet = InceptionResnetV1(pretrained='vggface2', num_classes=None).eval()
        except Exception as e:
            logger.error(f"Error initializing models: {str(e)}")
            return f"Error initializing models: {str(e)}"

        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        face, prob = mtcnn(img, return_prob=True)

        if face is not None:
            logger.info(f"Face detected with probability: {prob}")
            saved_data = torch.load(data_path)
            emb = resnet(face.unsqueeze(0)).detach()
            embedding_list = saved_data[0]
            name_list = saved_data[1]
            dist_list = [torch.dist(emb, emb_db).item() for emb_db in embedding_list]
            idx_min = dist_list.index(min(dist_list))
            # Similarity threshold
            # SIMILARITY_THRESHOLD = 0.6  # Adjust this value based on testing
            # min_dist = min(dist_list)
            # if min_dist > SIMILARITY_THRESHOLD:
            #     return "No match found"

            recognized_name = name_list[idx_min]
            logger.info(f"Recognized name: {recognized_name}")
            return recognized_name
        else:
            logger.info("No face detected in the image")
            return "No face detected"
    except Exception as e:
        logger.error(f"Error in face recognition: {str(e)}")
        return f"Error: {str(e)}"

def lambda_handler(event, context):
    logger.info("Starting lambda_handler")
    logger.info(f"Received event: {event}")
    s3_client = boto3.client('s3')

    try:
        # Get the input bucket and key
        # if 'Records' in event:
        #     s3_event = event['Records'][0]['s3']
        #     input_bucket = s3_event['bucket']['name']
        #     if not input_bucket.endswith('-stage-1'):
        #         input_bucket = '1229566873-stage-1'
        #         input_key = s3_event['object']['key']

        # elif 'requestPayload' in event and 'Records' in event['requestPayload']:
        #     s3_event = event['requestPayload']['Records'][0]['s3']
        #     input_bucket = s3_event['bucket']['name']
        #     if not input_bucket.endswith('-stage-1'):
        #         input_bucket = '1229566873-stage-1'
        #         input_key = s3_event['object']['key']


# new
        # input_bucket = event['responsePayload']['bucket']
        # input_key = event['responsePayload']['image_file_name']

        # if not input_bucket or not input_key:
        #     raise ValueError("Missing bucket or image_file_name in event responseContext")
        # logger.info(f"Processing image {input_key} from bucket {input_bucket}")
        # logger.info(f"Full event structure: {json.dumps(event, indent=2)}")



        try:
            if 'responsePayload' in event:
                input_bucket = event['responsePayload']['bucket']
                input_key = event['responsePayload']['image_file_name']
            elif 'responsePayload' in event.get('responseContext', {}):
                input_bucket = event['responseContext']['responsePayload']['bucket']
                input_key = event['responseContext']['responsePayload']['image_file_name']
            else:
                raise ValueError("Unable to find bucket and image_file_name in event structure")

            if not input_bucket or not input_key:
                raise ValueError("Missing bucket or image_file_name in event")
            
            logger.info(f"Extracted input_bucket: {input_bucket}, input_key: {input_key}")
        except KeyError as e:
            logger.error(f"KeyError when extracting bucket and image_file_name: {str(e)}")
            raise 




        # Validate file type
        if not input_key.lower().endswith(('.jpg', '.jpeg', '.png')):
            logger.error(f"Unsupported file type: {input_key}")
            return {
                'statusCode': 400,
                'body': f'Unsupported file type: {input_key}'
            }

        # Download the image file
        image_path = f'/tmp/{input_key}'
        try:
            s3_client.download_file(input_bucket, input_key, image_path)
            logger.info(f"Successfully downloaded image to {image_path}")
        except ClientError as e:
            logger.error(f"Error downloading image file: {e}")
            return {'statusCode': 400, 'body': 'Error downloading image file'}

        # Download the data.pt file
        data_path = '/tmp/data.pt'
        try:
            s3_client.download_file('datafilecontainer', 'data.pt', data_path)
            logger.info("Successfully downloaded data.pt file")
        except ClientError as e:
            logger.error(f"Error downloading data.pt file: {e}")
            return {'statusCode': 400, 'body': 'Error downloading data.pt file'}

        # Perform face recognition
        recognized_name = face_recognition_function(image_path, data_path)

        # Check if face recognition failed
        if isinstance(recognized_name, str) and recognized_name.startswith("Error:"):
            logger.error(f"Face recognition failed: {recognized_name}")
            return {
                'statusCode': 500,
                'body': recognized_name
            }

        # Write result to output bucket
        output_bucket = '1229566873-output'
        output_key = os.path.splitext(input_key)[0] + '.txt'
        try:
            s3_client.put_object(Bucket=output_bucket, Key=output_key, Body=recognized_name)
            logger.info(f"Successfully uploaded result to {output_bucket}/{output_key}")
        except ClientError as e:
            logger.error(f"Error uploading result: {e}")
            return {'statusCode': 500, 'body': 'Error uploading result'}

        # Clean up
        os.remove(image_path)
        os.remove(data_path)
        logger.info("Cleaned up temporary files")

        return {
            'statusCode': 200,
            'body': 'Face recognition complete'
        }
    except Exception as e:
        logger.error(f"Unexpected error in lambda_handler: {str(e)}")
        return {'statusCode': 500, 'body': f'Unexpected error: {str(e)}'}