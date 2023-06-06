import aws_cdk as core
import aws_cdk.assertions as assertions

from resume_iac.s3_website__stack import WebsiteIacStack

# example tests. To run these tests, uncomment this file along with the example
# resource in resume_iac/resume_iac_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = WebsiteIacStack(app, "resume-iac")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
