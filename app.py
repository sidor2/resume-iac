#!/usr/bin/env python3
import os

import aws_cdk as cdk

from resume_iac.s3_website__stack import S3WebsiteStack


app = cdk.App()

S3WebsiteStack(app, "S3WebsiteStack",
    env=cdk.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"], 
        region=os.environ["CDK_DEFAULT_REGION"]
    ),
)

app.synth()

