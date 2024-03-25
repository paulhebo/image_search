import os
import aws_cdk as cdk
from lib.ss_classification_stack import ImageClassificationStack
from lib.ss_notebook import NotebookStack


ACCOUNT = os.getenv('AWS_ACCOUNT_ID', '')
REGION = os.getenv('AWS_REGION', '')
AWS_ENV = cdk.Environment(account=ACCOUNT, region=REGION)
env = AWS_ENV
print(env)
app = cdk.App()

image_classification_stack = ImageClassificationStack(app, "ImageClassificationStack",env=env)
notebookstack = NotebookStack(app, "NotebookStack", env=env)

app.synth()