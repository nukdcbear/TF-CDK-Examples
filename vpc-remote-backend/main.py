#!/usr/bin/env python

from constructs import Construct
from cdktf import App, NamedRemoteWorkspace, TerraformStack, TerraformOutput, S3Backend, Fn
from cdktf_cdktf_provider_aws import AwsProvider, datasources, vpc

class MyStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)


        AwsProvider(self, "AWS", region="us-east-2")

        S3Backend(self,
                bucket = "dcb-remote-states",
                key = ".cdktf/remote-state" + ns,
                region = "us-east-2"
        )

        azones = datasources.DataAwsAvailabilityZones(self, "zones",
                                                    state = "available")

        myVpc = vpc.Vpc(self, "CustomVpc",
                        tags = {"Name":"cdktf-dcb-vpc"},
                        cidr_block = '10.0.0.0/16')

        subnet = vpc.Subnet(self, "Subnet",
                            vpc_id = myVpc.id,
                            availability_zone="${data." + azones.terraform_resource_type + "." + azones.friendly_unique_id + ".names[count.index]}",
                            cidr_block="${cidrsubnet(\"10.0.0.0/16\", 8, count.index)}",
                            tags = {"Name":"cdktf-dcb-subnet"})

        subnet.add_override("count", Fn.length_of(azones.names))

        TerraformOutput(self, "azs",
                        value=azones.names)
        TerraformOutput(self, "subnet_ids",
                        value="${" + subnet.terraform_resource_type + "." + subnet.friendly_unique_id + ".*.id}")

app = App()
MyStack(app, "vpc-remote-backend")

app.synth()
