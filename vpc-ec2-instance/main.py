#!/usr/bin/env python
from re import sub
import requests
from typing import Protocol
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput, Fn, Token, S3Backend
from cdktf_cdktf_provider_aws import AwsProvider, vpc, ec2, datasources

def get_my_ip():
    r = requests.get('https://api.ipify.org?format=json')
    response = r.json()

    return response["ip"]

def get_username():
    r = requests.get('https://randomuser.me/api/')
    response = r.json()

    return response["results"][0]["login"]["username"]

class MyStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        userName = get_username()
        # userName = 'dcb'
        myTag = 'cdktf-' + userName

        AwsProvider(self, "AWS", region="us-east-2")

        S3Backend(self,
                bucket = "dcb-remote-states",
                key = ".cdktf/remote-state-" + ns,
                region = "us-east-2"
        )

        azones = datasources.DataAwsAvailabilityZones(self, "zones",
                                                    state = "available")

        myVpc = vpc.Vpc(self, "CustomVpc",
                        tags = {"Name":myTag + "-vpc"},
                        cidr_block = '10.0.0.0/16')

        # n = 0
        # # numazs = int(Fn.length_of(azones.get_list_attribute("names")))
        # for index in range(3):
        #     n = index + 1
        #     azname = Fn.element(azones.names, index)
        #     cidrblk = "10.0."+str(n)+".0/24"
        #     subnet = vpc.Subnet(self, "Subnet"+str(n),
        #                         vpc_id = myVpc.id,
        #                         availability_zone=azname,
        #                         cidr_block=cidrblk,
        #                         tags = {"Name":myTag + "-subnet"})


        subnet = vpc.Subnet(self, "Subnet",
                            vpc_id = myVpc.id,
                            availability_zone="${data." + azones.terraform_resource_type + "." + azones.friendly_unique_id + ".names[count.index]}",
                            cidr_block="${cidrsubnet(\"10.0.0.0/16\", 8, count.index)}",
                            tags = {"Name":myTag + "-subnet"})

        subnet.add_override("count", Fn.length_of(azones.names))

        # subnet1 = vpc.Subnet(self, "Subnet1",
        #                     vpc_id = myVpc.id,
        #                     availability_zone = "us-east-2a",
        #                     cidr_block = '10.0.1.0/24',
        #                     tags = {"Name":myTag + "subnet1"})

        # subnet2 = vpc.Subnet(self, "Subnet2",
        #                     vpc_id = myVpc.id,
        #                     availability_zone = "us-east-2b",
        #                     cidr_block = '10.0.2.0/24',
        #                     tags = {"Name":myTag + "-subnet2"})

        # subnet3 = vpc.Subnet(self, "Subnet3",
        #                     vpc_id = myVpc.id,
        #                     availability_zone = "us-east-2c",
        #                     cidr_block = '10.0.3.0/24',
        #                     tags = {"Name":myTag + "-subnet3"})

        myIp = get_my_ip()
        myCidrBlk = myIp + '/32'

        ingress1 = vpc.SecurityGroupIngress(from_port = 22, to_port = 22, protocol = "tcp", cidr_blocks = [myCidrBlk])
        egress1 = vpc.SecurityGroupEgress(from_port = 0, to_port = 0, protocol = "tcp", cidr_blocks = ['0.0.0.0/0'])

        sg = vpc.SecurityGroup(self, "SecurityGroup",
                            vpc_id = myVpc.id,
                            description = myTag + "-sg",
                            tags = {"Name":myTag + "-sg"},
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
                                subnet_id = "${" + subnet.terraform_resource_type + "." + subnet.friendly_unique_id + ".0.id}",
                                tags = {"Name":myTag + "-instance"})

        TerraformOutput(self, "azs",
                        value=azones.names)
        TerraformOutput(self, "vpc_id",
                        value=myVpc.id)
        TerraformOutput(self, "subnet_ids",
                        value="${" + subnet.terraform_resource_type + "." + subnet.friendly_unique_id + ".*.id}")
        TerraformOutput(self, "sg_id",
                        value=sg.id)
        TerraformOutput(self, "ami_id",
                        value=ami.id)
        TerraformOutput(self, "instance_id",
                        value=instance.id,)

app = App()
MyStack(app, "vpc-ec2-instance")

app.synth()
