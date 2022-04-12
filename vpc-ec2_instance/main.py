#!/usr/bin/env python
from re import sub
import requests
from typing import Protocol
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput, Fn, Token
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

        AwsProvider(self, "AWS", region="us-east-2")

        zones = datasources.DataAwsAvailabilityZones(self, "zones",
                                                    state = "available")

        # userName = get_username()
        userName = 'dcb'
        myTag = 'cdktf-' + userName

        myVpc = vpc.Vpc(self, "CustomVpc",
                        tags = {"Name":myTag + "-vpc"},
                        cidr_block = '10.0.0.0/16')

        n = 0
        for azname in zones.names:
            n += 1
            cidrblk = "10.0."+str(n)+".0/24"
            subnet = vpc.Subnet(self, "Subnet",
                                vpc_id = myVpc.id,
                                availability_zone=azname,
                                cidr_block=cidrblk,
                                tags = {"Name":myTag + "-subnet"})


        # subnet = vpc.Subnet(self, "Subnet",
        #                     vpc_id = myVpc.id,
        #                     availability_zone="${Fn.element(zones.get_list_attribute(\"names\"), count.index)}",
        #                     cidr_block="${cidrsubnet(\"10.0.0.0/16\", 8, count.index)}",
        #                     # availability_zone = "${Fn.element(zones.names, count.index)}",
        #                     # cidr_block = '10.0.' + "${(each.key + 1)}" + '.0/24',
        #                     tags = {"Name":myTag + "-subnet"})

        # subnet.add_override("count", Fn.length_of(zones.names))
        # subnet.add_override("availability_zone", f"\\${Fn.element(Token().as_list(zones.names), count.index)}")
        # subnet.add_override("availability_zone", Fn.element(Token().as_list(zones.names), count.index))
        # subnet.add_override("availability_zone", Fn.element(zones.names, count.index))

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

        # instance = ec2.Instance(self, "Instance",
        #                         instance_type = "t2.micro",
        #                         ami = ami.id,
        #                         vpc_security_group_ids = [sg.id],
        #                         subnet_id = subnet.get(0).id,
        #                         tags = {"Name":myTag + "-instance"})

        TerraformOutput(self, "azs",
                        value=zones.names)
        TerraformOutput(self, "vpc_id",
                        value=myVpc.id)
        # TerraformOutput(self, "subnet1_id",
        #                 value=subnet[].id)
        # TerraformOutput(self, "subnet1_id",
        #                 value=subnet1.id)
        # TerraformOutput(self, "subnet2_id",
        #                 value=subnet2.id)
        # TerraformOutput(self, "subnet3_id",
        #                 value=subnet3.id)
        TerraformOutput(self, "sg_id",
                        value=sg.id)
        TerraformOutput(self, "ami_id",
                        value=ami.id)
        # TerraformOutput(self, "instance_id",
        #                 value=instance.id,)

app = App()
MyStack(app, "learn-cdktf-vpc")

app.synth()
