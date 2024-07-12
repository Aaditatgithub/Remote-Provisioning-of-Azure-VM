# Azure VM Provisioning Script

This script demonstrates how to provision a virtual machine (VM) in Azure using Python and the Azure SDK. The script performs the following tasks:
1. Sets up credential management.
2. Provisions a resource group.
3. Creates a network security group.
4. Provisions a virtual network (VNet).
5. Provisions a subnet.
6. Provisions a public IP address.
7. Provisions a network interface.
8. Provisions the VM.

## System Requirements
- Python 3.x
- Azure SDK for Python
- Visual Studio Code or any Python IDE

## Steps to Run the Script 
0. **Prerequisites: Ensure you have Azure subscription with admin priviliges**

1. **Install Azure SDK for Python**
   ```sh
   pip install azure-identity azure-mgmt-resource azure-mgmt-compute azure-mgmt-network

2. Set Up Environment Variables
   - Make sure to replace the placeholder values with your actual Azure AD tenant ID, client ID, secret key, and subscription ID
   ```python
   tenantid = '<your-tenant-id>'
   subscription_id = '<your-subscription-id>'
   clientid = '<your-client-id>'
   secretkey = '<your-secret-key>'

4. Run the Script
   ```sh
   python vm-provision.py 
   
## Future plans
   1. Maybe work on a project to provide parameterized fullstack provisioning in azure
