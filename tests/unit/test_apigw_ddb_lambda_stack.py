import pytest
from aws_cdk import Stack
from resume_iac.apigw_ddb_lambda_stack import ApiDdbLambdaStack

@pytest.fixture
def stack():
    scope = Stack()
    stack_id = "ApiDdbLambdaStack"
    domain_name = "example.com"
    stack = ApiDdbLambdaStack(scope, stack_id, domain_name)
    return stack

def test_ddb_table_created(stack):
    assert any(resource.resource_type == "AWS::DynamoDB::Table" for resource in stack.node.find_all())

def test_lambda_function_created(stack):
    assert any(resource.resource_type == "AWS::Lambda::Function" for resource in stack.node.find_all())

def test_api_gateway_created(stack):
    assert any(resource.resource_type == "AWS::ApiGateway::RestApi" for resource in stack.node.find_all())

def test_cors_configured(stack):
    api_gateway = stack.node.find_child("RestApi")
    assert api_gateway is not None
    assert hasattr(api_gateway, "default_cors_preflight_endpoint")

def test_api_endpoint_output(stack):
    output = stack.node.find_child("ApiEndpoint").value
    assert output.startswith("https://")
