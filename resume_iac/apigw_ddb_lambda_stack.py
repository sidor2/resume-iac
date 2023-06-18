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
from constructs import Construct

with open("./templates/get_counter_template.txt", "r", encoding="utf-8") as f:
    get_counter_template= f.read()

class ApiDdbLambdaStack(Stack):

    def __init__(self, scope: Construct, id: str, 
                domain_name: str, 
                **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create DynamoDB table
        ddb_table = dynamodb.Table(self, "CounterTable",
            table_name="counter-table",
            partition_key=dynamodb.Attribute(
                name="id", 
                type=dynamodb.AttributeType.NUMBER
                ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        lambda_role = iam.Role(
            self,
            'CounterLambdaRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    'service-role/AWSLambdaBasicExecutionRole'
                )
            ]
        )

        # Create a Lambda function to put records in the DynamoDB table
        counter_lambda = _lambda.Function(
            self,
            'CounterLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='index.lambda_handler',
            code=_lambda.Code.from_asset('./lambdas/counter_lambda'),
            role=lambda_role,
            # reserved_concurrent_executions=1,
            environment={
                'COUNTER_TABLE_NAME': ddb_table.table_name,
                'LOG_LEVEL': 'INFO'
            }
        )

        # Define the IAM policy statement
        table_policy_statement = iam.PolicyStatement(
            actions=['dynamodb:GetItem', 'dynamodb:UpdateItem'],
            resources=[ddb_table.table_arn],
        )
        
        # Attach the policy statement to the Lambda function's execution role
        counter_lambda.add_to_role_policy(table_policy_statement)

        logs.LogGroup(
            self,
            'CounterLambdaLogGroup',
            log_group_name=f'/aws/lambda/{counter_lambda.function_name}',
            retention=logs.RetentionDays.ONE_DAY
        )

        # Create API Gateway REST API
        self.rest_api = apigateway.RestApi(self, "RestApi",
            rest_api_name="MyApi",
            deploy_options=apigateway.StageOptions(
                throttling_rate_limit=10,
                throttling_burst_limit=2
            ),
            description="API Gateway for Counter Lambda",
            endpoint_types=[apigateway.EndpointType.EDGE]
        )

        # # Add POST method to the API
        resource = self.rest_api.root.add_resource("counter",)

        get_counter_method = resource.add_method("GET",
            apigateway.LambdaIntegration(counter_lambda),
            operation_name="GetCounter",
            api_key_required=True,
        )

        plan = self.rest_api.add_usage_plan("CounterUsagePlan",
            name="CounterUsagePlan",
            throttle=apigateway.ThrottleSettings(
                rate_limit=10,
                burst_limit=2
            ),
        )
        
        plan.add_api_stage(
            stage=self.rest_api.deployment_stage,
            throttle=[apigateway.ThrottlingPerMethod(
                    method=get_counter_method,
                    throttle=apigateway.ThrottleSettings(
                        rate_limit=10,
                        burst_limit=2
                    )
                )
            ]
        )

        self.api_key = self.rest_api.add_api_key("CounterApiKey",
            api_key_name="CounterApiKey",
            description="Counter API Key",
        )

        

        plan.add_api_key(self.api_key)

        # Output the API URL
        CfnOutput(self, "ApiEndpoint",
            value=self.rest_api.url,
            description="API Endpoint"
        )

