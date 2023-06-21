from aws_cdk import (
    Stack,
    CfnOutput,
    RemovalPolicy,
    aws_logs as logs,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_lambda as _lambda,
)

import aws_cdk as cdk
from aws_cdk.assertions import Capture, Template, Match

from app import ApiDdbLambdaStack

def test_synthesizes_properly():
    app = cdk.App()

    backend_stack = ApiDdbLambdaStack(app, "BackendStack")

    template = Template.from_stack(backend_stack)

    template.has_resource_properties("AWS::DynamoDB::Table", {
            "TableName": "counter-table",
        }
    )
    
    template.has_resource_properties("AWS::Lambda::Function", {
            "Handler": "index.lambda_handler",
            "Runtime": "python3.9"
        }
    )

    

                
