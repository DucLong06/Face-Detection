## Gen SSH key for jenkins
```shell
ssh-keygen -t rsa -b 2048 -f jenkins_key -C "longhd"  
```
## Provision a new cluster
```shell
cd terraform
terraform init
terraform plan
terraform apply
```
## setup jenkins with ansible
```shell
ansible-playbook -i ansible/inventory/inventory.ini ansible/deploy_jenkins.yaml
```