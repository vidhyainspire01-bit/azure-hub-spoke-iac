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
  network_security_group_id = azurerm_network_security_group.default.id
  network_security_group_id = azurerm_network_security_group.default.id
  network_security_group_id = azurerm_network_security_group.default.id
  address_prefixes     = ["10.2.1.0/24"]

}

resource "azurerm_network_interface" "vm1_nic" {
  name                = "vm1-nic"
  location            = azurerm_resource_group.spoke2.location
  resource_group_name = azurerm_resource_group.spoke2.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.spoke2_dev.id
    private_ip_address_allocation = "Dynamic"
  }
}

resource "azurerm_windows_virtual_machine" "vm1" {
  name                = "myvm"
  location            = azurerm_resource_group.spoke2.location
  resource_group_name = azurerm_resource_group.spoke2.name
  size                = "Standard_B2s"
  admin_username      = "adminuser"
  admin_password      = "P@ssw0rd1234!"

  network_interface_ids = [azurerm_network_interface.vm1_nic.id]

  os_disk {
    name                 = "myvm_os_disk"
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
    disk_size_gb         = 64
  }

  source_image_reference {
    publisher = "MicrosoftWindowsServer"
    offer     = "WindowsServer"
    sku       = "2019-Datacenter"
    version   = "latest"
  }
  tags = {
    environment = "dev"
    owner       = "vidhya"
  }
}

resource "azurerm_network_security_group" "spoke2_dev_nsg" {
  name                = "spoke2-dev-nsg"
  location            = azurerm_resource_group.spoke2.location
  resource_group_name = azurerm_resource_group.spoke2.name

  tags = {
    environment = "dev"
    owner       = "vidhya"
  }
}

resource "azurerm_subnet_network_security_group_association" "spoke2_dev_assoc" {
  subnet_id                 = azurerm_subnet.spoke2_dev.id
  network_security_group_id = azurerm_network_security_group.spoke2_dev_nsg.id
}

resource "azurerm_subnet" "spoke2_prod" {
  name                 = "prod"
  resource_group_name  = azurerm_resource_group.spoke2.name
  virtual_network_name = azurerm_virtual_network.spoke2_vnet.name
  network_security_group_id = azurerm_network_security_group.default.id
  network_security_group_id = azurerm_network_security_group.default.id
  network_security_group_id = azurerm_network_security_group.default.id
  address_prefixes     = ["10.2.2.0/24"]

}


resource "azurerm_network_security_group" "spoke2_prod_nsg" {
  name                = "spoke2-prod-nsg"
  location            = azurerm_resource_group.spoke2.location
  resource_group_name = azurerm_resource_group.spoke2.name

  tags = {
    environment = "prod"
    owner       = "vidhya"
  }
}

resource "azurerm_subnet_network_security_group_association" "spoke2_prod_assoc" {
  subnet_id                 = azurerm_subnet.spoke2_prod.id
  network_security_group_id = azurerm_network_security_group.spoke2_prod_nsg.id
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
