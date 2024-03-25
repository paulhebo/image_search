from constructs import Construct
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    RemovalPolicy,
    Duration
)
import os

class ImageClassificationStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        # configure the lambda role
        _classification_role_policy = iam.PolicyStatement(
            actions=[
                'sagemaker:InvokeEndpointAsync',
                'sagemaker:InvokeEndpoint',
                'lambda:AWSLambdaBasicExecutionRole',
                'lambda:InvokeFunction',
            ],
            resources=['*']
        )
        classification_role = iam.Role(
            self, 'classification_role',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com')
        )
        classification_role.add_to_policy(_classification_role_policy)

        classification_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )
        
        
        function_name = 'image_classification'
        classification_function = _lambda.Function(
            self, function_name,
            function_name=function_name,
            runtime=_lambda.Runtime.PYTHON_3_9,
            role=classification_role,
            code=_lambda.Code.from_asset('../lambda/' + function_name),
            handler='lambda_function' + '.lambda_handler',
            timeout=Duration.minutes(10),
            reserved_concurrent_executions=100
        )
        
        image_classification_api = apigw.RestApi(self, 'image-classification-api',
                               default_cors_preflight_options=apigw.CorsOptions(
                                   allow_origins=apigw.Cors.ALL_ORIGINS,
                                   allow_methods=apigw.Cors.ALL_METHODS
                               ),
                               endpoint_types=[apigw.EndpointType.REGIONAL]
                               )
                               
        classification_integration = apigw.LambdaIntegration(
            classification_function,
            proxy=True,
            integration_responses=[
                apigw.IntegrationResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'"
                    }
                )
            ]
        )
        
        classification_resource = image_classification_api.root.add_resource(
            'image_classification',
            default_cors_preflight_options=apigw.CorsOptions(
                allow_methods=['GET', 'OPTIONS'],
                allow_origins=apigw.Cors.ALL_ORIGINS)
        )

        classification_resource.add_method(
            'GET',
            classification_integration,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ]
        )
