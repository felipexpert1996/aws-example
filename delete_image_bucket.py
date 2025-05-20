import os
import logging
import boto3
from boto3.dynamodb.conditions import Attr

s3 = boto3.resource('s3')
resource_dynamodb = boto3.resource('dynamodb')
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
        s3.Bucket(os.environ['BUCKET_NAME']).Object(key=f'{params.get('name')}').delete()
        delete_from_db(params.get('name'))
        
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

def delete_from_db(file_name):
    table = resource_dynamodb.Table(os.environ['DYNAMO_TABLE'])
    response = table.scan(FilterExpression=Attr('name').eq(file_name))
    items = response['Items']
    for item in items:
        table.delete_item(Key={'id': item['id']})