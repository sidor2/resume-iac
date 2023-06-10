import boto3
import json
import os


TABLE_NAME = os.environ.get('COUNTER_TABLE_NAME')

def lambda_handler(event, context):
    try:
        # Read the current value of the 'counter' key from DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(TABLE_NAME)
    
        # Read the current item with id = 1 and counter = 0
        response = table.get_item(Key={'id': 1})
        item = response.get('Item')
    
        # Increment the counter by 1
        updated_counter = int(item.get('counter', 0)) + 1
    
        # Update the item with the incremented counter
        table.update_item(
            Key={'id': 1},
            UpdateExpression='SET #counter = :new_counter',
            ExpressionAttributeNames={'#counter': 'counter'},
            ExpressionAttributeValues={':new_counter': updated_counter}
        )

        print(f'The counter value is now {updated_counter}')

        # Create a response object
        response = {
            'statusCode': 200,
            'body': json.dumps({'message': 'Success', 'data': f'{updated_counter}'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        return response
    
    except Exception as e:
        
        print("Maybe missing an initial counter value")
        print(e)

        return {
            'statusCode': 500,
            'body': f'Maybe missing an initial counter value: {e}'
        }
