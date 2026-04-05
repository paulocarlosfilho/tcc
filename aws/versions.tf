terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  # Configuration for LocalStack
  endpoints {
    ec2            = "http://localhost:4510"
    iam            = "http://localhost:4511"
    cloudformation = "http://localhost:4512"
    s3             = "http://localhost:4566"
    # Add other services as needed for your project
    # For a full list of service endpoints, refer to LocalStack documentation:
    # https://docs.localstack.cloud/references/configuration/"
  }
}
