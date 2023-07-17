# Import the needed credential and management objects from the libraries.
import os
from datetime import datetime
from azure.identity import ClientSecretCredential
#from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient      
from azure.identity import DefaultAzureCredential
from azure.mgmt.network.v2017_03_01.models import NetworkSecurityGroup
from azure.mgmt.network.v2017_03_01.models import SecurityRule

print("Provisioning a virtual machine...some operations might take a \
minute or two.")
dttime = f'{datetime.now():%d-%H-%M-%S%z}'

# Step 1: Credential Management
#----------------------------------------------

tenantid ''
subscription_id = ''
clientid = ''
secretkey = ''


credential = ClientSecretCredential(
    tenant_id=tenantid, client_id=clientid,
    client_secret=secretkey)


# Step 2: Provision a resource group
#-----------------------------------------------------------------------------
# Obtain the management object for resources, using the credentials
# from the CLI login.
resource_client = ResourceManagementClient(credential, subscription_id)

# Constants we need in multiple places: the resource group name and
# the region in which we provision resources. You can change these
# values however you want.

RESOURCE_GROUP_NAME = "RG"
SECURITY_RULE_NAME = "SecurityRuleAllowRDP"
LOCATION = "eastus"
NETWORK_SECUIRITY_GROUP = RESOURCE_GROUP_NAME + "-" + "NSG"


rg_result = resource_client.resource_groups.create_or_update(
    RESOURCE_GROUP_NAME, {"location": LOCATION}
)
print(f"Provisioned Resource Group {RESOURCE_GROUP_NAME}")


#Step-3 - Create Network security group
network_client = NetworkManagementClient(credential,subscription_id)

poller = network_client.network_security_groups.begin_create_or_update(
        resource_group_name=RESOURCE_GROUP_NAME,
        network_security_group_name=NETWORK_SECUIRITY_GROUP,
        parameters={"location": LOCATION,
                "properties": {
                "securityRules": [
                    {
                        "name": "rule1",
                        "properties": {
                            "access": "Allow",
                            "destinationAddressPrefix": "*",
                            "destinationPortRange": "3389",
                            "direction": "Inbound",
                            "priority": 100,
                            "protocol": "TCP",
                            "sourceAddressPrefix": "*",
                            "sourcePortRange": "*",
                        },
                    }
                ]
            },



                    },
    )
nsg_result = poller.result();   
print(f"Provisioned Network Security Group {NETWORK_SECUIRITY_GROUP}")

# Step-4 Provision the VNET
#----------------------------
# Obtain the management object for networks

IP_NAME = "ip" +  "-" + dttime
IP_CONFIG_NAME = "ip-config" + "-" + dttime
NIC_NAME = "nic" + "-" + dttime
VNET_NAME = "VNET" + "-" + dttime
SUBNET_NAME = "SUBNET" + "-" + dttime

## Provision the virtual network and wait for completion
poller = network_client.virtual_networks.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    VNET_NAME,
    {
        "location": LOCATION,
        "address_space": {"address_prefixes": ["10.0.0.0/16"]},
    }
)
vnet_result = poller.result()
#
print(
    f"Provisioned virtual network {vnet_result.name} with address \
#prefixes {vnet_result.address_space.address_prefixes}"
)
#
## Step 5: Provision the subnet and wait for completion
#-------------------------------------------------------
poller = network_client.subnets.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    VNET_NAME,
    SUBNET_NAME,
    {
        "address_prefix": "10.0.0.0/21",
    },
)
subnet_result = poller.result()

print(
    f"Provisioned virtual subnet {subnet_result.name} with address \
prefix {subnet_result.address_prefix}"
)

# Step 6: Provision an IP address and wait for completion
#--------------------------------------------------------
poller = network_client.public_ip_addresses.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    IP_NAME,
    {
        "location": LOCATION,
        "sku": {"name": "Standard"},
        "public_ip_allocation_method": "Static",
        "public_ip_address_version": "IPV4",
    },
)

ip_address_result = poller.result()

print(
    f"Provisioned public IP address {ip_address_result.name} \
with address {ip_address_result.ip_address}"
)

# Step 7: Provision the network interface client
#-------------------------------------------------
poller = network_client.network_interfaces.begin_create_or_update(
    RESOURCE_GROUP_NAME,
NIC_NAME,
    {
        "location": LOCATION,
        "ip_configurations": [
            {
                "name": IP_CONFIG_NAME,
                "subnet": {"id": subnet_result.id},
                "public_ip_address": {"id": ip_address_result.id},
                "networkSecurityGroup": nsg_result.id,
            }
        ],
    },
)

nic_result = poller.result()

# Step 8: Provision the VM
#-------------------------------------------------
# Provision the VM specifying only minimal arguments, which defaults
# to an Ubuntu 18.04 VM on a Standard DS1 v2 plan with a public IP address
# and a default virtual network/subnet.
VM_NAME = "A" + "-" + dttime
USERNAME = "azureuser"
PASSWORD = "Admin123456#"

print( f"Provisioning virtual machine {VM_NAME}; this operation might \
take a few minutes."
)
# Obtain the management object for virtual machines
compute_client = ComputeManagementClient(credential, subscription_id)
poller = compute_client.virtual_machines.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    VM_NAME,
    {   "location": LOCATION,
        "storage_profile": {
            "imageReference": {
                "publisher": "MicrosoftWindowsServer",
                "offer": "WindowsServer",
                "sku": "2022-datacenter-azure-edition",
                "version": "latest",
                "exactVersion": "20348.1547.230207",
                #"publisher": "Canonical",
                #"offer": "UbuntuServer",
                #"sku": "16.04.0-LTS",
                #"version": "latest",
            }
        },
        "hardware_profile": {"vm_size": "Standard_DS1_v2"},
        "os_profile": {
            "computer_name": VM_NAME,
            "admin_username": USERNAME,
            "admin_password": PASSWORD,
        },
        "network_profile": {
            "network_interfaces": [
                {
                    "id": nic_result.id,
                    "networkSecurityGroup": nsg_result.id,
                },
            ]
        },
    },
)
vm_result = poller.result()
print(f"Provisioned virtual machine {vm_result.name}")
