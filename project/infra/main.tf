provider "aws" {
  region = var.aws_region
}

resource "aws_key_pair" "deployer" {
  key_name   = var.key_name
  public_key = file("~/.ssh/id_rsa.pub")
}

resource "aws_security_group" "allow_web" {
  name        = "allow_web_traffic"
  description = "Allow ports for Flask API, Adminer, Grafana, Postgres (custom port), and SSH"

  ingress {
    from_port   = 9696
    to_port     = 9696
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow access to the Flask price predictor on port 9696"
  }

  ingress {
    from_port   = 8050
    to_port     = 8050
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow access to Adminer dashboard on port 8050"
  }

  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow access to Grafana web interface on port 3000"
  }

  ingress {
    from_port   = 5431
    to_port     = 5431
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow external access to Postgres running on port 5431"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow SSH access to the EC2 instance"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]

    description = "Allow all outbound traffic"
  }
}

resource "aws_instance" "docker_host" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.allow_web.id]

  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y docker.io docker-compose git
              systemctl enable docker
              usermod -aG docker ubuntu
              EOF

  tags = {
    Name = "docker-compose-host"
  }
}


output "public_ip" {
  value = aws_instance.docker_host.public_ip
}