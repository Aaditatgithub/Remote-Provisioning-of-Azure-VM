param vmName string
param adminUsername string
param adminPassword string
param sqlServerName string
param sqlAdminUsername string
param sqlAdminPassword string
param sqlDatabaseName string

var nicName = '${vmName}-nic'
var nsgName = '${vmName}-nsg'
var vnetName = '${vmName}-vnet'
var subnetName = 'default'
var addressPrefix = '10.0.0.0/16'
var subnetPrefix = '10.0.0.0/24'
var publicIPAddressName = '${vmName}-pip'
var vmSize = 'Standard_DS1_v2'

resource vnet 'Microsoft.Network/virtualNetworks@2020-06-01' = {
  name: vnetName
  location: resourceGroup().location
  properties: {
    addressSpace: {
      addressPrefixes: [
        addressPrefix
      ]
    }
    subnets: [
      {
        name: subnetName
        properties: {
          addressPrefix: subnetPrefix
        }
      }
    ]
  }
}

resource nsg 'Microsoft.Network/networkSecurityGroups@2020-06-01' = {
  name: nsgName
  location: resourceGroup().location
  properties: {
    securityRules: [
      {
        name: 'default-allow-rdp'
        properties: {
          priority: 1000
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '3389'
          description: 'Allow RDP'
        }
      }
    ]
  }
}

resource publicIPAddress 'Microsoft.Network/publicIPAddresses@2020-06-01' = {
  name: publicIPAddressName
  location: resourceGroup().location
  properties: {
    publicIPAllocationMethod: 'Dynamic'
  }
}

resource nic 'Microsoft.Network/networkInterfaces@2020-06-01' = {
  name: nicName
  location: resourceGroup().location
  dependsOn: [
    vnet
    nsg
  ]
  properties: {
    ipConfigurations: [
      {
        name: 'ipconfig1'
        properties: {
          subnet: {
            id: vnet.properties.subnets[0].id
          }
          networkSecurityGroup: {
            id: nsg.id
          }
          publicIPAddress: {
            id: publicIPAddress.id
          }
        }
      }
    ]
  }
}

resource vm 'Microsoft.Compute/virtualMachines@2020-06-01' = {
  name: vmName
  location: resourceGroup().location
  dependsOn: [
    nic
  ]
  properties: {
    hardwareProfile: {
      vmSize: vmSize
    }
    osProfile: {
      computerName: vmName
      adminUsername: adminUsername
      adminPassword: adminPassword
    }
    storageProfile: {
      imageReference: {
        publisher: 'MicrosoftWindowsServer'
        offer: 'WindowsServer'
        sku: '2019-Datacenter'
        version: 'latest'
      }
      osDisk: {
        createOption: 'FromImage'
      }
    }
    networkProfile: {
      networkInterfaces: [
        {
          id: nic.id
        }
      ]
    }
  }
}

resource sqlServer 'Microsoft.Sql/servers@2020-11-01-preview' = {
  name: sqlServerName
  location: resourceGroup().location
  properties: {
    administratorLogin: sqlAdminUsername
    administratorLoginPassword: sqlAdminPassword
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2020-11-01-preview' = {
  name: sqlDatabaseName
  dependsOn: [
    sqlServer
  ]
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
    maxSizeBytes: '2147483648'
    sampleName: 'AdventureWorksLT'
  }
}

resource firewallRule 'Microsoft.Sql/servers/firewallRules@2020-11-01-preview' = {
  name: 'AllowAllWindowsAzureIps'
  dependsOn: [
    sqlServer
  ]
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

output vmName string = vmName
output publicIPAddress string = publicIPAddress.properties.dnsSettings.fqdn
output sqlServerName string = sqlServerName
output sqlDatabaseName string = sqlDatabaseName