variable "aws_region" {
  default = "ap-southeast-2"
}

variable "key_name" {
  description = "Name of the EC2 key pair"
  type        = string
}

variable "instance_type" {
  default = "t3.micro"
}

variable "ami_id" {
  description = "Ubuntu 22.04 AMI ID for the selected region"
  default     = ""
}