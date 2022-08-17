#!/usr/bin/env python

from constructs import Construct
from cdktf import App, NamedRemoteWorkspace, TerraformStack, TerraformOutput, S3Backend, DataTerraformRemoteStateS3
from cdktf_cdktf_provider_aws import AwsProvider, ec2, s3

class MyStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        AwsProvider(self, "AWS", region="us-east-2")

        S3Backend(self,
                bucket = "dcb-remote-states",
                key = ".cdktf/remote-state" + ns,
                region = "us-east-2"
        )

        amiFilter1 = ec2.DataAwsAmiFilter(name = "name", values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"])
        amiFilter2 = ec2.DataAwsAmiFilter(name = "virtualization-type", values = ["hvm"])

        ami = ec2.DataAwsAmi(self, "ami",
                            most_recent = True,
                            owners = ["099720109477"],
                            filter = [amiFilter1, amiFilter2]
                            )

        instance = ec2.Instance(self, "compute",
                                ami=ami.id,
                                instance_type="t2.micro",
                                )

        TerraformOutput(self, "public_ip",
                        value=instance.public_ip,
                        )


app = App()

stack = MyStack(app, "aws_instance")

app.synth()
