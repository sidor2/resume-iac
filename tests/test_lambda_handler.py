import pytest
from moto import mock_dynamodb
import boto3
import json
import os

from lambdas.counter_lambda.index import lambda_handler

TABLE_NAME = 'test-table'

@pytest.fixture
def counter_table():
    with mock_dynamodb():
        resource = boto3.resource('dynamodb', region_name='us-east-1')
        test_table =resource.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {
                    'AttributeName': 'id', 
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id', 
                    'AttributeType': 'N'
                }
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )

        # test_table.put_item(Item={'id': 1, 'counter': 0})
        yield test_table


os.environ['COUNTER_TABLE_NAME'] = TABLE_NAME

@pytest.fixture
def counter_table_inital(counter_table):
    counter_table.put_item(Item={'id': 1, 'counter': 0})
    yield counter_table

def test_lambda_handler_200(counter_table_inital):
    event = {}
    context = {}
    
    response = lambda_handler(event, context)
    
    assert response['statusCode'] == 200
    assert type(json.loads(response['body'])) == dict
    assert json.loads(response['body']) == {'message': 'Success', 'data': '1'}

@pytest.fixture
def change_counter_value(counter_table):
    counter_table.put_item(Item={'id': 1, 'counter': 10})
    yield counter_table

def test_lambda_handler_count(change_counter_value):
    event = {}
    context = {}
    
    response = lambda_handler(event, context)
    
    assert response['statusCode'] == 200
    assert json.loads(response['body']) == {'message': 'Success', 'data': '11'}

@pytest.fixture
def wrong_counter_value_type(counter_table):
    counter_table.put_item(Item={'id': 1, 'counter': 'test'})
    yield counter_table

def test_lambda_handler_wrong_type(wrong_counter_value_type):
    event = {}
    context = {}
    
    response = lambda_handler(event, context)
    
    assert response['statusCode'] == 500
