#!/bin/bash
set -e

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 [deploy|destroy]"
  exit 1
fi

COMMAND="$1"

# Initialize Terraform
terraform init

if [ "$COMMAND" == "deploy" ]; then
  echo "Planning deployment..."
  terraform plan -out=tfplan
  echo "Applying plan..."
  terraform apply -auto-approve tfplan
elif [ "$COMMAND" == "destroy" ]; then
  echo "Destroying infrastructure..."
  terraform destroy -auto-approve
else
  echo "Unknown command: $COMMAND"
  echo "Usage: $0 [deploy|destroy]"
  exit 1
fi
