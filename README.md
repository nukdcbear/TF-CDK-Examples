# Getting Started With CDK for Terraform - CDKTF Python Examples

The Terraform CDK is a relatively new project, presently in community preview, that provides a nice extension to "programatically" create infrastructure with Terraform.

Some developers prefer to use a familiar programming language to define their infrastructure. This allows them to use the same language constructs and tools they are familiar with for other development tasks. They can also use all of the features and libraries available to fully featured programming languages to develop complex infrastructure projects. Additionally the CDK provides us with a harness to integrate external services and data with Terraform. Also by using your programming language of choice, you can take advantage of the features and development workflows you are familiar with. For example, when working with Python, you can use IDE features such as IntelliSense in Visual Studio Code.

This repository contains a few example use cases on how to leverage the CDK.

## AWS Credentials

All of these examples utilize AWS, so you'll need to generate and set your credentials accordingly.

## Prerequisites

In order to use CDKTF, you will need Terraform and Node.js. These examples are based upon Python.

- [Terraform](https://www.terraform.io/downloads) >= v1.0+
- [Node.js](https://nodejs.org/en/) >= v14+
- [Python](https://www.python.org/downloads/) >= 3.7+
- [pipenv](https://pipenv.pypa.io/en/latest/install/#installing-pipenv/) >= v2021.5.29

## Initialization of CDKTF Project

Use existing code example:
1. Clone git respo
2. cd into project and example folder
3. `pipenv install`
4. `cdktf synth`
5. `cdktf deploy`
6. `cdktf destroy`

Start a blank project from scratch:

1. mkdir <your directory name>
2. cd into directory
3. Execute `cdktf init --template="python" --local`
   Note: the `-local` option is for locally managed state file, otherwise you will be prompted for TF Cloud state management.
4. For Python based projects install the CDKTF provider; i.e. `pipenv install cdktf-cdktf-provider-aws`
5. Edit the `main.py` file with the desired coding and CDK resources.
6. Generate TF plan and valid code: `cdktf synth`
7. Provision infrastructure `cdktf deploy`
8. Destroy infrastructure `cdktf destroy`