import os
import logging
import boto3

s3 = boto3.resource('s3')
logger = logging.getLogger()
logger.setLevel("INFO")

def lambda_handler(event, context):

    try:

        params = event.get('queryStringParameters')
        if params is None or params.get('name') is None:
            logger.error('Missing query string parameters')
            return {
                'statusCode': 400,
                'body': 'Error: Missing query string parameters'
            }

        s3 = boto3.resource('s3')
        logger.info(s3.Bucket(os.environ['BUCKET_NAME']).Object(key=f'{params.get('name')}').delete())
        
        logger.info('Image deleted successfully')
        return {
            'statusCode': 204,
            'body': 'Image deleted successfully'
        }

    except Exception as e:
        logger.error(f'Error {str(e)}')
        return {
            'statusCode': 500,
            'body': 'Error: Internal server error'
        }
