resource "azurerm_resource_group" "hub" {
  name     = "rg-hub"
  location = "eastus"

  tags = {
    environment = "prod"
    owner       = "vidhya"
  }
}

resource "azurerm_virtual_network" "hub_vnet" {
  name                = "vnet-hub"
  location            = azurerm_resource_group.hub.location
  resource_group_name = azurerm_resource_group.hub.name
  address_space       = ["10.0.0.0/16"]

  tags = {
    environment = "prod"
    owner       = "vidhya"
  }
}


resource "azurerm_subnet" "AzureFirewallSubnet" {
  name                 = "AzureFirewallSubnet"
  resource_group_name  = azurerm_resource_group.hub.name
  virtual_network_name = azurerm_virtual_network.hub_vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}
