resource "azurerm_resource_group" "spoke1" {
  name     = "rg-spoke1"
  location = "eastus"
}

resource "azurerm_virtual_network" "spoke1_vnet" {
  name                = "vnet-spoke1"
  location            = azurerm_resource_group.spoke1.location
  resource_group_name = azurerm_resource_group.spoke1.name
  address_space       = ["10.1.0.0/16"]

  tags = {
    environment = "dev"
    owner       = "vidhya"
  }
}

resource "azurerm_subnet" "dev" {
  name                 = "dev"
  resource_group_name  = azurerm_resource_group.spoke1.name
  virtual_network_name = azurerm_virtual_network.spoke1_vnet.name
  address_prefixes     = ["10.1.1.0/24"]

  tags = {
    environment = "dev"
    owner       = "vidhya"
  }
}

resource "azurerm_network_security_group" "spoke1_dev_nsg" {
  name                = "spoke1-dev-nsg"
  location            = azurerm_resource_group.spoke1.location
  resource_group_name = azurerm_resource_group.spoke1.name

  tags = {
    environment = "dev"
    owner       = "vidhya"
  }
}
resource "azurerm_subnet_network_security_group_association" "spoke1_dev_assoc" {
  subnet_id                 = azurerm_subnet.dev.id
  network_security_group_id = azurerm_network_security_group.spoke1_dev_nsg.id
}



resource "azurerm_subnet" "prod" {
  name                 = "prod"
  resource_group_name  = azurerm_resource_group.spoke1.name
  virtual_network_name = azurerm_virtual_network.spoke1_vnet.name
  address_prefixes     = ["10.1.2.0/24"]
}
resource "azurerm_network_security_group" "spoke1_prod_nsg" {
  name                = "spoke1-prod-nsg"
  location            = azurerm_resource_group.spoke1.location
  resource_group_name = azurerm_resource_group.spoke1.name

  tags = {
    environment = "prod"
    owner       = "vidhya"
  }
}
resource "azurerm_subnet_network_security_group_association" "spoke1_prod_assoc" {
  subnet_id                 = azurerm_subnet.prod.id
  network_security_group_id = azurerm_network_security_group.spoke1_prod_nsg.id
}
