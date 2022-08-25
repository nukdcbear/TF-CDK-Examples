#!/usr/bin/env python
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput, S3Backend, Fn
from cdktf_cdktf_provider_aws import AwsProvider
from imports.terraform_aws_modules.aws import Vpc


class MyStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)


        myRegion = "us-east-2"
        myVpcCidrBlock = "10.0.0.0/16"

        publicSubnet = []
        privateSubnet = []
        aZones = []
        for index, item in enumerate(["a", "b", "c"]):
            aZones.append(myRegion + item)
            publicSubnet.append(Fn.cidrsubnet(myVpcCidrBlock, 5, index))
            privateSubnet.append(Fn.cidrsubnet(myVpcCidrBlock, 5, index + 3))

        S3Backend(
            self,
            bucket="dcb-remote-states",
            encrypt=True,
            key="tfstates/domo-vpc",
            region=myRegion,
        )

        AwsProvider(self, "aws", region="us-east-2")

        aws_vpc = Vpc(
            self,
            "aws_vpc",
            azs=aZones,
            cidr=myVpcCidrBlock,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            enable_nat_gateway=True,
            enable_vpn_gateway=False,
            name="domo-vpc",
            private_subnets=privateSubnet,
            public_subnets=publicSubnet,
            tags={"Environment": "dev", "Name": "domo-vpc", "Terraform": "true"},
        )

        TerraformOutput(self, "private-subnets", value=aws_vpc.private_subnets_output)
        TerraformOutput(self, "public-subnets", value=aws_vpc.public_subnets_output)
        TerraformOutput(self, "vpc_id", value=aws_vpc.vpc_id_output)

app = App()
MyStack(app, "python-aws")

app.synth()
