import os
import subprocess
import boto3
from botocore.exceptions import ClientError
import json


AWS_ACCESS_KEY_ID = 'aws-access-key-id'
AWS_SECRET_ACCESS_KEY='aws-secret-access-key'


def lambda_handler(event, context):
    s3_client = boto3.client('s3',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    # Get the input bucket and key from the S3 event
    input_bucket = event['Records'][0]['s3']['bucket']['name']
    input_key = event['Records'][0]['s3']['object']['key']

    # Extract the video name without extension
    video_name = os.path.splitext(os.path.basename(input_key))[0]

    # Set up the output bucket name
    output_bucket = input_bucket.replace('-input', '-stage-1')

    # Download the input video to /tmp
    input_path = f'/tmp/{input_key}'
    try:
        s3_client.download_file(input_bucket, input_key, input_path)
    except ClientError as e:
        print(f"Error downloading input file: {e}")
        return {
            'statusCode': 400,
            'body': 'Error downloading input file'
        }

    # Set up the output file path
    output_file = f'/tmp/{video_name}.jpg'

    # Run FFmpeg command
    ffmpeg_command = [
        'ffmpeg',
        '-i', input_path,
        '-vframes', '1',
        output_file,
        '-y',
        '-v', 'debug'
    ]
    
    try:
        result = subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        print("FFmpeg output:", result.stdout)
        print("FFmpeg error:", result.stderr)
    except subprocess.CalledProcessError as e:
        print("FFmpeg command failed:")
        print("Output:", e.output)
        print("Error:", e.stderr)
        return {
            'statusCode': 500,
            'body': 'Error processing video'
        }

    # Upload the output images to S3
    s3_key = f'{video_name}.jpg'
    try:
        s3_client.upload_file(output_file, output_bucket, s3_key)
    except ClientError as e:
        print(f"Error uploading {s3_key}: {e}")
        return {
            'statusCode': 500,
            'body': 'Error uploading processed image'
        }

    # Clean up temporary files
    os.remove(input_path)
    os.remove(output_file)

    # Invoke face-recognition function for each uploaded file
    # lambda_client = boto3.client('lambda',
    #                 aws_access_key_id=AWS_ACCESS_KEY_ID,
    #                 aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                    
    # try:
    #     lambda_client.invoke(
    #         FunctionName='face-recog-lf',
    #         InvocationType='Event',
    #         Payload=json.dumps({
    #             "bucket_name": output_bucket,
    #             "image_file_name": s3_key
    #         })
    #     )
    # except ClientError as e:
    #     print(f"Error invoking face-recognition function for {s3_key}: {e}")

    return {
        'statusCode': 200,
        'body': f'Successfully processed {input_key} and uploaded 1 frame',
        'bucket': output_bucket,
        'image_file_name': s3_key
    }