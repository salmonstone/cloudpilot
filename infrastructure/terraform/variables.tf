variable "aws_region"          { default = "ap-south-1" }
variable "project_name"        { default = "cloudpilot" }
variable "environment"         { default = "production" }
variable "cluster_name"        { default = "cloudpilot-cluster" }
variable "vpc_cidr"            { default = "10.0.0.0/16" }
variable "availability_zones"  { default = ["ap-south-1a", "ap-south-1b"] }
variable "public_subnet_cidrs" { default = ["10.0.1.0/24", "10.0.2.0/24"] }
variable "private_subnet_cidrs"{ default = ["10.0.10.0/24", "10.0.11.0/24"] }
