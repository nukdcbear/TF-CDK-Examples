#!/usr/bin/env python
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput, S3Backend
from cdktf_cdktf_provider_aws import AwsProvider
from imports.terraform_aws_modules.aws import Vpc


class MyStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        S3Backend(
            self,
            bucket="dcb-remote-states",
            encrypt=True,
            key="tfstates/domo-vpc",
            region="us-east-2",
        )

        AwsProvider(self, "aws", region="us-east-2")

        aws_vpc = Vpc(
            self,
            "aws_vpc",
            azs=["us-east-2a", "us-east-2b", "us-east-2c"],
            cidr="10.0.0.0/16",
            enable_dns_hostnames=True,
            enable_dns_support=True,
            enable_nat_gateway=True,
            enable_vpn_gateway=False,
            name="domo-vpc",
            private_subnets=["10.0.128.0/20", "10.0.144.0/20", "10.0.160.0/20"],
            public_subnets=["10.0.0.0/20", "10.0.16.0/20", "10.0.32.0/20"],
            tags={"Environment": "dev", "Name": "domo-vpc", "Terraform": "true"},
        )

        TerraformOutput(self, "private-subnets", value=aws_vpc.private_subnets_output)
        TerraformOutput(self, "public-subnets", value=aws_vpc.public_subnets_output)
        TerraformOutput(self, "vpc_id", value=aws_vpc.vpc_id_output)

app = App()
MyStack(app, "python-aws")

app.synth()
