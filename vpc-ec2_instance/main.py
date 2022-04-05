#!/usr/bin/env python
from typing import Protocol
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput
from cdktf_cdktf_provider_aws import AwsProvider, vpc, ec2


class MyStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        AwsProvider(self, "AWS", region="us-east-2")

        vpcdcb = vpc.Vpc(self, "CustomVpc",
                        tags = {"Name":"cdktf-dcb-vpc"},
                        cidr_block = '10.0.0.0/16')

        subnet1 = vpc.Subnet(self, "Subnet1",
                            vpc_id = vpcdcb.id,
                            availability_zone = "us-east-2a",
                            cidr_block = '10.0.1.0/24',
                            tags = {"Name":"cdktf-dcb-subnet1"})

        subnet2 = vpc.Subnet(self, "Subnet2",
                            vpc_id = vpcdcb.id,
                            availability_zone = "us-east-2b",
                            cidr_block = '10.0.2.0/24',
                            tags = {"Name":"cdktf-dcb-subnet2"})

        subnet3 = vpc.Subnet(self, "Subnet3",
                            vpc_id = vpcdcb.id,
                            availability_zone = "us-east-2c",
                            cidr_block = '10.0.3.0/24',
                            tags = {"Name":"cdktf-dcb-subnet3"})

        ingress1 = vpc.SecurityGroupIngress(from_port = 22, to_port = 22, protocol = "tcp", cidr_blocks = ['65.189.75.63/32'])
        egress1 = vpc.SecurityGroupEgress(from_port = 0, to_port = 0, protocol = "tcp", cidr_blocks = ['0.0.0.0/0'])

        sg = vpc.SecurityGroup(self, "SecurityGroup",
                            vpc_id = vpcdcb.id,
                            description = "cdktf-dcb-sg",
                            tags = {"Name":"cdktf-dcb-sg"},
                            ingress = [ingress1],
                            egress = [egress1])

        amiFilter1 = ec2.DataAwsAmiFilter(name = "name", values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"])
        amiFilter2 = ec2.DataAwsAmiFilter(name = "virtualization-type", values = ["hvm"])

        ami = ec2.DataAwsAmi(self, "ami",
                            most_recent = True,
                            owners = ["099720109477"],
                            filter = [amiFilter1, amiFilter2]
                            )

        instance = ec2.Instance(self, "Instance",
                                instance_type = "t2.micro",
                                ami = ami.id,
                                vpc_security_group_ids = [sg.id],
                                subnet_id = subnet1.id,
                                tags = {"Name":"cdktf-dcb-instance"})

        TerraformOutput(self, "vpc_id",
                        value=vpcdcb.id)
        TerraformOutput(self, "subnet1_id",
                        value=subnet1.id)
        TerraformOutput(self, "subnet2_id",
                        value=subnet2.id)
        TerraformOutput(self, "subnet3_id",
                        value=subnet3.id)
        TerraformOutput(self, "sg_id",
                        value=sg.id)
        TerraformOutput(self, "ami_id",
                        value=ami.id)
        TerraformOutput(self, "instance_id",
                        value=instance.id,
                        )

app = App()
MyStack(app, "learn-cdktf-vpc")

app.synth()