import json
import os
import logging
import boto3
import base64
import uuid

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
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


        if 'body' not in event or event['body'] is None:
            logger.error('Missing request body')
            return {
                'statusCode': 400,
                'body': 'Error: Missing request body'
            }

        body = json.loads(event['body'])
        content_type = event['headers'].get('Content-Type')

        if content_type is None:
            logger.error('Missing Content-Type header')
            return {
                'statusCode': 400,
                'body': 'Error: Missing Content-Type header'
            }

        if 'image' in body:
            image_bytes = base64.b64decode(body['image'])
        else:
            logger.error('Missing image parameter in request body')
            return {
                'statusCode': 400,
                'body': 'Error: Invalid request format. Image data not found.'
            }

        s3 = boto3.resource('s3')
        s3.Bucket(os.environ['BUCKET_NAME']).put_object(Key=f'{params.get('name')}', Body=image_bytes)
        url = s3_client.generate_presigned_url('get_object', Params={'Bucket': os.environ['BUCKET_NAME'], 'Key': f'{params.get('name')}'})
        update_dynamodb(params.get('name'), url)

        logger.info('Image received and processed successfully')
        return {
            'statusCode': 200,
            'body': 'Image received and processed successfully'
        }

    except Exception as e:
        logger.error(f'Error {str(e)}')
        return {
            'statusCode': 500,
            'body': 'Error: Internal server error'
        }

def update_dynamodb(name, url):
    resource_dynamodb = boto3.resource('dynamodb')
    table = resource_dynamodb.Table(os.environ['DYNAMO_TABLE'])
    id = str(uuid.uuid4())
    print(f'Atualizando database: {id}')
    response = table.put_item(
        Item={
            'id':  id,
            'name': name,
            'url': url,
        }
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        logger.info(f'DB atualizado: {name}')
    else:
        logger.error('ERRO de atualizacao')