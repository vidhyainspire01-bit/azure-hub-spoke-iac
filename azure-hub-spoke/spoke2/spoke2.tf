resource "azurerm_resource_group" "spoke2" {
  name     = "rg-spoke2"
  location = "eastus"

  tags = {
    environment = "dev"
    owner       = "vidhya"
  }
}

resource "azurerm_virtual_network" "spoke2_vnet" {
  name                = "vnet-spoke2"
  location            = azurerm_resource_group.spoke2.location
  resource_group_name = azurerm_resource_group.spoke2.name
  address_space       = ["10.2.0.0/16"]

  tags = {
    environment = "dev"
    owner       = "vidhya"
  }
}
resource "azurerm_subnet" "spoke2_dev" {
  name                 = "dev"
  resource_group_name  = azurerm_resource_group.spoke2.name
  virtual_network_name = azurerm_virtual_network.spoke2_vnet.name
  address_prefixes     = ["10.2.1.0/24"]

  tags = {
    environment = "dev"
    owner       = "vidhya"
  }
}
resource "azurerm_subnet" "spoke2_prod" {
  name                 = "prod"
  resource_group_name  = azurerm_resource_group.spoke2.name
  virtual_network_name = azurerm_virtual_network.spoke2_vnet.name
  address_prefixes     = ["10.2.2.0/24"]

  tags = {
    environment = "prod"
    owner       = "vidhya"
  }
}
resource "azurerm_virtual_network_peering" "hub_to_spoke2" {
  name                      = "hub-to-spoke2"
  resource_group_name       = azurerm_resource_group.hub.name
  virtual_network_name      = azurerm_virtual_network.hub_vnet.name
  remote_virtual_network_id = azurerm_virtual_network.spoke2_vnet.id
  allow_forwarded_traffic   = true
  allow_gateway_transit     = true

}
resource "azurerm_virtual_network_peering" "spoke2_to_hub" {
  name                      = "spoke2-to-hub"
  resource_group_name       = azurerm_resource_group.spoke2.name
  virtual_network_name      = azurerm_virtual_network.spoke2_vnet.name
  remote_virtual_network_id = azurerm_virtual_network.hub_vnet.id
  allow_forwarded_traffic   = true
  use_remote_gateways       = true

}
