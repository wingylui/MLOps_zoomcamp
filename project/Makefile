Terraform:
	@echo "Initializing Terraform..."
	cd $(TERRAFORM_DIR) && terraform init

	@echo "Planning Terraform deployment..."
	cd $(TERRAFORM_DIR) && terraform plan

	@echo "Applying Terraform deployment..."
	cd $(TERRAFORM_DIR) && terraform apply

	@echo "Destroying Terraform-managed infrastructure..."
	cd $(TERRAFORM_DIR) && terraform destroy 

# ssh:
# 	@echo "Connecting to EC2 instance via SSH..."
# 	@IP=$$(cd $(TERRAFORM_DIR) && terraform output -raw public_ip) && \
# 	echo "Connecting to $$IP..." && \
# 	ssh -i ~/.ssh/YOUR_KEY.pem ubuntu@$$IP
