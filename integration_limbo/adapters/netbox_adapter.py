import requests
import logging
import json
import os
import sys  # Import sys for sys.exit
from diffsync import Adapter
from diffsync.exceptions import ObjectNotFound
from integration_limbo.integrations.netbox_to_digitalocean.models import (
    ManufacturerModel,
    DeviceTypeModel,
    DeviceRoleModel,
    SiteModel,
    DeviceModel,
)

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ManufacturerNetBoxModel(ManufacturerModel):
    """NetBox-specific implementation of Manufacturer CRUD methods."""

    @classmethod
    def create(cls, adapter, ids, attrs):
        """Create a new manufacturer in NetBox."""
        data = {
            "name": ids["name"],
            "slug": attrs["slug"],
            "description": attrs.get("description", ""),
        }
        endpoint = f"{adapter.url}/api/dcim/manufacturers/"
        response = requests.post(endpoint, headers=adapter.headers, json=data)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to create manufacturer '{ids['name']}' in NetBox.")
            logger.error(f"HTTP Error: {e}")
            logger.error(f"Response status code: {response.status_code}")
            logger.error(f"Response content: {response.text}")
            logger.error(f"Request data: {data}")
            sys.exit(1)  # Exit the process
        manufacturer = response.json()
        logger.info(f"Created manufacturer: {manufacturer['name']}")

        # Capture and store the NetBox ID after creation
        ids["id"] = manufacturer["id"]
        return super().create(adapter, ids=ids, attrs=attrs)

    def delete(self):
        """Delete a manufacturer in NetBox."""
        endpoint = f"{self.adapter.url}/api/dcim/manufacturers/{self.id}/"
        response = requests.delete(endpoint, headers=self.adapter.headers)
        if response.status_code == 204:
            logger.info(f"Deleted manufacturer: {self.name}")
        else:
            logger.error(f"Failed to delete manufacturer {self.name}: {response.text}")
        return super().delete()


class DeviceTypeNetBoxModel(DeviceTypeModel):
    """NetBox-specific implementation of DeviceType CRUD methods."""

    @classmethod
    def create(cls, adapter, ids, attrs):
        """Create a new device type in NetBox."""
        # Get the manufacturer ID
        manufacturer = adapter.get(ManufacturerNetBoxModel, {"name": attrs["manufacturer_name"]})
        if not manufacturer:
            logger.error(f"Manufacturer {attrs['manufacturer_name']} not found.")
            sys.exit(1)  # Exit the process

        data = {
            "model": ids["model"],
            "manufacturer": manufacturer.id,
            "slug": attrs["slug"],
        }
        endpoint = f"{adapter.url}/api/dcim/device-types/"
        response = requests.post(endpoint, headers=adapter.headers, json=data)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to create device type '{ids['model']}' in NetBox.")
            logger.error(f"HTTP Error: {e}")
            logger.error(f"Response status code: {response.status_code}")
            logger.error(f"Response content: {response.text}")
            logger.error(f"Request data: {data}")
            sys.exit(1)  # Exit the process
        device_type = response.json()
        logger.info(f"Created device type: {device_type['model']}")

        ids["id"] = device_type["id"]
        return super().create(adapter, ids=ids, attrs=attrs)

    def delete(self):
        """Delete a device type in NetBox."""
        endpoint = f"{self.adapter.url}/api/dcim/device-types/{self.id}/"
        response = requests.delete(endpoint, headers=self.adapter.headers)
        if response.status_code == 204:
            logger.info(f"Deleted device type: {self.model}")
        else:
            logger.error(f"Failed to delete device type {self.model}: {response.text}")
        return super().delete()


class DeviceRoleNetBoxModel(DeviceRoleModel):
    """NetBox-specific implementation of DeviceRole CRUD methods."""

    @classmethod
    def create(cls, adapter, ids, attrs):
        """Create a new device role in NetBox."""
        data = {
            "name": ids["name"],
            "slug": attrs["slug"],
            "color": attrs.get("color", "ffffff"),
        }
        endpoint = f"{adapter.url}/api/dcim/device-roles/"
        response = requests.post(endpoint, headers=adapter.headers, json=data)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to create device role '{ids['name']}' in NetBox.")
            logger.error(f"HTTP Error: {e}")
            logger.error(f"Response status code: {response.status_code}")
            logger.error(f"Response content: {response.text}")
            logger.error(f"Request data: {data}")
            sys.exit(1)  # Exit the process
        device_role = response.json()
        logger.info(f"Created device role: {device_role['name']}")

        ids["id"] = device_role["id"]
        return super().create(adapter, ids=ids, attrs=attrs)

    def delete(self):
        """Delete a device role in NetBox."""
        endpoint = f"{self.adapter.url}/api/dcim/device-roles/{self.id}/"
        response = requests.delete(endpoint, headers=self.adapter.headers)
        if response.status_code == 204:
            logger.info(f"Deleted device role: {self.name}")
        else:
            logger.error(f"Failed to delete device role {self.name}: {response.text}")
        return super().delete()


class SiteNetBoxModel(SiteModel):
    """NetBox-specific implementation of Site CRUD methods."""

    @classmethod
    def create(cls, adapter, ids, attrs):
        """Create a new site in NetBox."""
        data = {
            "name": ids["name"],
            "slug": attrs["slug"],
        }
        endpoint = f"{adapter.url}/api/dcim/sites/"
        response = requests.post(endpoint, headers=adapter.headers, json=data)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to create site '{ids['name']}' in NetBox.")
            logger.error(f"HTTP Error: {e}")
            logger.error(f"Response status code: {response.status_code}")
            logger.error(f"Response content: {response.text}")
            logger.error(f"Request data: {data}")
            sys.exit(1)  # Exit the process
        site = response.json()
        logger.info(f"Created site: {site['name']}")

        ids["id"] = site["id"]
        return super().create(adapter, ids=ids, attrs=attrs)

    def delete(self):
        """Delete a site in NetBox."""
        endpoint = f"{self.adapter.url}/api/dcim/sites/{self.id}/"
        response = requests.delete(endpoint, headers=self.adapter.headers)
        if response.status_code == 204:
            logger.info(f"Deleted site: {self.name}")
        else:
            logger.error(f"Failed to delete site {self.name}: {response.text}")
        return super().delete()


class DeviceNetBoxModel(DeviceModel):
    """NetBox-specific implementation of Device CRUD methods."""

    @classmethod
    def create(cls, adapter, ids, attrs):
        """Create a new device in NetBox."""
        # Get device type, device role, and site IDs
        device_type = adapter.get(DeviceTypeNetBoxModel, {"model": attrs["device_type_name"]})
        if not device_type:
            logger.error(f"Device type '{attrs['device_type_name']}' not found.")
            sys.exit(1)  # Exit the process

        device_role = adapter.get(DeviceRoleNetBoxModel, {"name": attrs["device_role_name"]})
        if not device_role:
            logger.error(f"Device role '{attrs['device_role_name']}' not found.")
            sys.exit(1)  # Exit the process

        site = adapter.get(SiteNetBoxModel, {"name": attrs["site_name"]})
        if not site:
            logger.error(f"Site '{attrs['site_name']}' not found.")
            sys.exit(1)  # Exit the process

        data = {
            "name": ids["name"],
            "device_type": device_type.id,
            "role": device_role.id,  # Changed from 'device_role' to 'role'
            "site": site.id,
            "status": attrs.get("status", "active"),
        }
        endpoint = f"{adapter.url}/api/dcim/devices/"
        response = requests.post(endpoint, headers=adapter.headers, json=data)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to create device '{ids['name']}' in NetBox.")
            logger.error(f"HTTP Error: {e}")
            logger.error(f"Response status code: {response.status_code}")
            logger.error(f"Response content: {response.text}")
            logger.error(f"Request data: {data}")
            sys.exit(1)  # Exit the process

        device = response.json()
        logger.info(f"Created device: {device['name']}")

        ids["id"] = device["id"]
        return super().create(adapter, ids=ids, attrs=attrs)

    def delete(self):
        """Delete a device in NetBox."""
        endpoint = f"{self.adapter.url}/api/dcim/devices/{self.id}/"
        response = requests.delete(endpoint, headers=self.adapter.headers)
        if response.status_code == 204:
            logger.info(f"Deleted device: {self.name}")
        else:
            logger.error(f"Failed to delete device {self.name}: {response.text}")
        return super().delete()


class NetBoxAdapter(Adapter):
    """NetBox adapter that loads models and interacts with the NetBox API using requests."""

    manufacturer = ManufacturerNetBoxModel
    device_type = DeviceTypeNetBoxModel
    device_role = DeviceRoleNetBoxModel
    site = SiteNetBoxModel
    device = DeviceNetBoxModel

    top_level = ["manufacturer", "device_type", "device_role", "site", "device"]

    def __init__(self, url, token, branch_schema_id=None, test_mode=False, *args, **kwargs):
        """Initialize the adapter with NetBox API connection."""
        super().__init__(*args, **kwargs)
        self.url = url.rstrip('/')
        self.token = token
        self.headers = {
            "Authorization": f"Token {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if branch_schema_id:
            self.headers["X-NetBox-Branch"] = branch_schema_id
        self.test_mode = test_mode

    def load(self):
        """Load data from NetBox into the DiffSync system."""
        logger.info("### Starting data load from NetBox ###")
        self.load_manufacturers()
        self.load_device_types()
        self.load_device_roles()
        self.load_sites()
        self.load_devices()

    def load_manufacturers(self):
        """Load Manufacturer data from NetBox."""
        endpoint = f"{self.url}/api/dcim/manufacturers/"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        manufacturers_data = response.json()["results"]

        # Ensure the directory exists
        os.makedirs('test_data/netbox/', exist_ok=True)

        # Save data to disk
        if not self.test_mode:
            with open('test_data/netbox/manufacturers.json', 'w') as f:
                json.dump(manufacturers_data, f, indent=4)

        for data in manufacturers_data:
            manufacturer_model = self.manufacturer(
                name=data['name'],
                description=data.get('description', ''),
                slug=data['slug'],
                id=data['id'],
            )
            self.add(manufacturer_model)
        logger.info(f"Successfully loaded {len(manufacturers_data)} manufacturers")

    def load_device_types(self):
        """Load DeviceType data from NetBox."""
        endpoint = f"{self.url}/api/dcim/device-types/"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        device_types_data = response.json()["results"]

        # Ensure the directory exists
        os.makedirs('test_data/netbox/', exist_ok=True)

        # Save data to disk
        if not self.test_mode:
            with open('test_data/netbox/device_types.json', 'w') as f:
                json.dump(device_types_data, f, indent=4)

        for data in device_types_data:
            manufacturer_name = data['manufacturer']['name']
            device_type_model = self.device_type(
                model=data['model'],
                manufacturer_name=manufacturer_name,
                slug=data['slug'],
                id=data['id'],
            )
            self.add(device_type_model)
        logger.info(f"Successfully loaded {len(device_types_data)} device types")

    def load_device_roles(self):
        """Load DeviceRole data from NetBox."""
        endpoint = f"{self.url}/api/dcim/device-roles/"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        device_roles_data = response.json()["results"]

        # Ensure the directory exists
        os.makedirs('test_data/netbox/', exist_ok=True)

        # Save data to disk
        if not self.test_mode:
            with open('test_data/netbox/device_roles.json', 'w') as f:
                json.dump(device_roles_data, f, indent=4)

        for data in device_roles_data:
            device_role_model = self.device_role(
                name=data['name'],
                slug=data['slug'],
                id=data['id'],
            )
            self.add(device_role_model)
        logger.info(f"Successfully loaded {len(device_roles_data)} device roles")

    def load_sites(self):
        """Load Site data from NetBox."""
        endpoint = f"{self.url}/api/dcim/sites/"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        sites_data = response.json()["results"]

        # Ensure the directory exists
        os.makedirs('test_data/netbox/', exist_ok=True)

        # Save data to disk
        if not self.test_mode:
            with open('test_data/netbox/sites.json', 'w') as f:
                json.dump(sites_data, f, indent=4)

        for data in sites_data:
            site_model = self.site(
                name=data['name'],
                slug=data['slug'],
                id=data['id'],
            )
            self.add(site_model)
        logger.info(f"Successfully loaded {len(sites_data)} sites")

    def load_devices(self):
        """Load Device data from NetBox."""
        endpoint = f"{self.url}/api/dcim/devices/"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        devices_data = response.json()["results"]

        # Ensure the directory exists
        os.makedirs('test_data/netbox/', exist_ok=True)

        # Save data to disk
        if not self.test_mode:
            with open('test_data/netbox/devices.json', 'w') as f:
                json.dump(devices_data, f, indent=4)

        for data in devices_data:
            device_model = self.device(
                name=data['name'],
                device_type_name=data['device_type']['model'],
                device_role_name=data['role']['name'],  # Changed from 'device_role' to 'role'
                site_name=data['site']['name'],
                status=data['status']['value'],
                id=data['id'],
            )
            self.add(device_model)
        logger.info(f"Successfully loaded {len(devices_data)} devices")