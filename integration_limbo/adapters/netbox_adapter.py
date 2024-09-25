import pynetbox
import logging
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
        try:
            manufacturer = adapter.netbox_api.dcim.manufacturers.create([data])
            if manufacturer:
                manufacturer = manufacturer[0]
                logger.info(f"Created manufacturer: {manufacturer.name}")
                ids["id"] = manufacturer.id
                return super().create(adapter, ids=ids, attrs=attrs)
        except Exception as e:
            logger.error(f"Failed to create manufacturer '{ids['name']}']: {e}")
        return None

    def update(self, attrs):
        """Update an existing manufacturer in NetBox."""
        try:
            manufacturer = self.adapter.netbox_api.dcim.manufacturers.get(self.id)
            if manufacturer:
                data = {
                    "name": self.name,
                    "slug": attrs.get("slug", self.slug),
                    "description": attrs.get("description", self.description),
                }
                manufacturer.update(data)
                logger.info(f"Updated manufacturer: {self.name}")
                return super().update(attrs)
            else:
                logger.error(f"Manufacturer {self.name} not found in NetBox.")
        except Exception as e:
            logger.error(f"Failed to update manufacturer {self.name}: {e}")
        return None

    def delete(self):
        """Delete a manufacturer in NetBox."""
        try:
            manufacturer = self.adapter.netbox_api.dcim.manufacturers.get(self.id)
            if manufacturer:
                response = manufacturer.delete()
                if response:
                    logger.info(f"Deleted manufacturer: {self.name}")
                    return super().delete()
                else:
                    logger.error(f"Failed to delete manufacturer {self.name}: {response}")
            else:
                logger.error(f"Manufacturer {self.name} not found in NetBox.")
        except Exception as e:
            logger.error(f"Failed to delete manufacturer {self.name}: {e}")
        return None


class DeviceTypeNetBoxModel(DeviceTypeModel):
    """NetBox-specific implementation of DeviceType CRUD methods."""

    @classmethod
    def create(cls, adapter, ids, attrs):
        """Create a new device type in NetBox."""
        manufacturer = adapter.get(ManufacturerNetBoxModel, {"name": attrs["manufacturer_name"]})
        if not manufacturer:
            logger.error(f"Manufacturer '{attrs['manufacturer_name']}' not found.")
            return None

        data = {
            "model": ids["model"],
            "manufacturer": manufacturer.id,
            "slug": attrs["slug"],
        }
        try:
            device_type = adapter.netbox_api.dcim.device_types.create([data])
            if device_type:
                device_type = device_type[0]
                logger.info(f"Created device type: {device_type.model}")
                ids["id"] = device_type.id
                return super().create(adapter, ids=ids, attrs=attrs)
        except Exception as e:
            logger.error(f"Failed to create device type '{ids['model']}']: {e}")
        return None

    def update(self, attrs):
        """Update an existing device type in NetBox."""
        try:
            device_type = self.adapter.netbox_api.dcim.device_types.get(self.id)
            if device_type:
                manufacturer_name = attrs.get("manufacturer_name", self.manufacturer_name)
                manufacturer = self.adapter.get(ManufacturerNetBoxModel, {"name": manufacturer_name})
                if not manufacturer:
                    logger.error(f"Manufacturer '{manufacturer_name}' not found.")
                    return None

                data = {
                    "model": self.model,
                    "manufacturer": manufacturer.id,
                    "slug": attrs.get("slug", self.slug),
                }
                device_type.update(data)
                logger.info(f"Updated device type: {self.model}")
                return super().update(attrs)
            else:
                logger.error(f"Device type {self.model} not found in NetBox.")
        except Exception as e:
            logger.error(f"Failed to update device type {self.model}: {e}")
        return None

    def delete(self):
        """Delete a device type in NetBox, only if it has no devices."""
        try:
            device_type = self.adapter.netbox_api.dcim.device_types.get(self.id)
            if device_type:
                response = device_type.delete()
                if response:
                    logger.info(f"Deleted device type: {self.model}")
                    return super().delete()
                else:
                    logger.error(f"Failed to delete device type {self.model}: {response}")
            else:
                logger.error(f"Device type {self.model} not found in NetBox.")
        except Exception as e:
            logger.error(f"Failed to delete device type {self.model}: {e}")
        return None


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
        try:
            device_role = adapter.netbox_api.dcim.device_roles.create([data])
            if device_role:
                device_role = device_role[0]
                logger.info(f"Created device role: {device_role.name}")
                ids["id"] = device_role.id
                return super().create(adapter, ids=ids, attrs=attrs)
        except Exception as e:
            logger.error(f"Failed to create device role '{ids['name']}']: {e}")
        return None

    def update(self, attrs):
        """Update an existing device role in NetBox."""
        try:
            device_role = self.adapter.netbox_api.dcim.device_roles.get(self.id)
            if device_role:
                data = {
                    "name": self.name,
                    "slug": attrs.get("slug", self.slug),
                    "color": attrs.get("color", "ffffff"),
                }
                device_role.update(data)
                logger.info(f"Updated device role: {self.name}")
                return super().update(attrs)
            else:
                logger.error(f"Device role {self.name} not found in NetBox.")
        except Exception as e:
            logger.error(f"Failed to update device role {self.name}: {e}")
        return None

    def delete(self):
        """Delete a device role in NetBox."""
        try:
            device_role = self.adapter.netbox_api.dcim.device_roles.get(self.id)
            if device_role:
                response = device_role.delete()
                if response:
                    logger.info(f"Deleted device role: {self.name}")
                    return super().delete()
                else:
                    logger.error(f"Failed to delete device role {self.name}: {response}")
            else:
                logger.error(f"Device role {self.name} not found in NetBox.")
        except Exception as e:
            logger.error(f"Failed to delete device role {self.name}: {e}")
        return None


class SiteNetBoxModel(SiteModel):
    """NetBox-specific implementation of Site CRUD methods."""

    @classmethod
    def create(cls, adapter, ids, attrs):
        """Create a new site in NetBox."""
        data = {
            "name": ids["name"],
            "slug": attrs["slug"],
        }
        try:
            site = adapter.netbox_api.dcim.sites.create([data])
            if site:
                site = site[0]
                logger.info(f"Created site: {site.name}")
                ids["id"] = site.id
                return super().create(adapter, ids=ids, attrs=attrs)
        except Exception as e:
            logger.error(f"Failed to create site '{ids['name']}']: {e}")
        return None

    def update(self, attrs):
        """Update an existing site in NetBox."""
        try:
            site = self.adapter.netbox_api.dcim.sites.get(self.id)
            if site:
                data = {
                    "name": self.name,
                    "slug": attrs.get("slug", self.slug),
                }
                site.update(data)
                logger.info(f"Updated site: {self.name}")
                return super().update(attrs)
            else:
                logger.error(f"Site {self.name} not found in NetBox.")
        except Exception as e:
            logger.error(f"Failed to update site {self.name}: {e}")
        return None

    def delete(self):
        """Delete a site in NetBox, but only if it has no devices."""
        try:
            site = self.adapter.netbox_api.dcim.sites.get(self.id)
            if site:
                response = site.delete()
                if response:
                    logger.info(f"Deleted site: {self.name}")
                    return super().delete()
                else:
                    logger.error(f"Failed to delete site {self.name}: {response}")
            else:
                logger.error(f"Site {self.name} not found in NetBox.")
        except Exception as e:
            logger.error(f"Failed to delete site {self.name}: {e}")
        return None


class DeviceNetBoxModel(DeviceModel):
    """NetBox-specific implementation of Device CRUD methods."""

    @classmethod
    def create(cls, adapter, ids, attrs):
        """Create a new device in NetBox."""
        try:
            device_type = adapter.get(DeviceTypeNetBoxModel, {"model": attrs["device_type_name"]})
            if not device_type:
                logger.error(f"Device type '{attrs['device_type_name']}' not found.")
                return None

            device_role = adapter.get(DeviceRoleNetBoxModel, {"name": attrs["device_role_name"]})
            if not device_role:
                logger.error(f"Device role '{attrs['device_role_name']}' not found.")
                return None

            site = adapter.get(SiteNetBoxModel, {"name": attrs["site_name"]})
            if not site:
                logger.error(f"Site '{attrs['site_name']}' not found.")
                return None

            data = {
                "name": ids["name"],
                "device_type": device_type.id,
                "role": device_role.id,
                "site": site.id,
                "status": attrs.get("status", "active"),
            }
            device = adapter.netbox_api.dcim.devices.create([data])
            if device:
                device = device[0]
                logger.info(f"Created device: {device.name}")
                ids["id"] = device.id
                return super().create(adapter, ids=ids, attrs=attrs)
        except Exception as e:
            logger.error(f"Failed to create device '{ids['name']}']: {e}")
        return None

    def update(self, attrs):
        """Update an existing device in NetBox."""
        try:
            device = self.adapter.netbox_api.dcim.devices.get(self.id)
            if device:
                device_type_name = attrs.get("device_type_name", self.device_type_name)
                device_type = self.adapter.get(DeviceTypeNetBoxModel, {"model": device_type_name})
                if not device_type:
                    logger.error(f"Device type '{device_type_name}' not found.")
                    return None

                device_role_name = attrs.get("device_role_name", self.device_role_name)
                device_role = self.adapter.get(DeviceRoleNetBoxModel, {"name": device_role_name})
                if not device_role:
                    logger.error(f"Device role '{device_role_name}' not found.")
                    return None

                site_name = attrs.get("site_name", self.site_name)
                site = self.adapter.get(SiteNetBoxModel, {"name": site_name})
                if not site:
                    logger.error(f"Site '{site_name}' not found.")
                    return None

                data = {
                    "name": self.name,
                    "device_type": device_type.id,
                    "role": device_role.id,
                    "site": site.id,
                    "status": attrs.get("status", self.status),
                }
                device.update(data)
                logger.info(f"Updated device: {self.name}")
                return super().update(attrs)
            else:
                logger.error(f"Device {self.name} not found in NetBox.")
        except Exception as e:
            logger.error(f"Failed to update device {self.name}: {e}")
        return None

    def delete(self):
        """Delete a device in NetBox."""
        try:
            device = self.adapter.netbox_api.dcim.devices.get(self.id)
            if device:
                response = device.delete()
                if response:
                    logger.info(f"Deleted device: {self.name}")
                    return super().delete()
                else:
                    logger.error(f"Failed to delete device {self.name}: {response}")
            else:
                logger.error(f"Device {self.name} not found in NetBox.")
        except Exception as e:
            logger.error(f"Failed to delete device {self.name}: {e}")
        return None


class NetBoxAdapter(Adapter):
    """NetBox adapter that loads models and interacts with NetBox using pynetbox."""

    manufacturer = ManufacturerNetBoxModel
    device_type = DeviceTypeNetBoxModel
    device_role = DeviceRoleNetBoxModel
    site = SiteNetBoxModel
    device = DeviceNetBoxModel

    top_level = ["site", "manufacturer", "device_role"]

    def __init__(self, url, token, branch_schema_id=None, test_mode=False, *args, **kwargs):
        """Initialize the adapter with NetBox API connection."""
        super().__init__(*args, **kwargs)
        self.url = url.rstrip('/')
        self.token = token
        self.netbox_api = pynetbox.api(self.url, self.token)

        if branch_schema_id:
            self.netbox_api.http_session.headers["X-NetBox-Branch"] = branch_schema_id

        self.test_mode = test_mode

    def load(self):
        """Load data from NetBox into the DiffSync system."""
        logger.info("### Starting data load from NetBox ###")
        self.load_sites()              
        self.load_manufacturers()      
        self.load_device_roles()       
        self.load_device_types()       
        self.load_devices()            

    def load_manufacturers(self):
        """Load Manufacturer data from NetBox."""
        manufacturers = self.netbox_api.dcim.manufacturers.all()

        for manufacturer in manufacturers:
            manufacturer_model = self.manufacturer(
                name=manufacturer.name,
                description=manufacturer.description or '',
                slug=manufacturer.slug,
                id=manufacturer.id,
            )
            self.add(manufacturer_model)
        logger.info(f"Successfully loaded {len(manufacturers)} manufacturers")

    def load_device_types(self):
        """Load DeviceType data from NetBox."""
        device_types = self.netbox_api.dcim.device_types.all()

        for device_type in device_types:
            manufacturer_name = device_type.manufacturer.name
            device_type_model = self.device_type(
                model=device_type.model,
                manufacturer_name=manufacturer_name,
                slug=device_type.slug,
                id=device_type.id,
            )
            self.add(device_type_model)

            # Add device_type as a child of the corresponding manufacturer
            manufacturer = self.get(ManufacturerNetBoxModel, {"name": manufacturer_name})
            manufacturer.add_child(device_type_model)
            self.update(manufacturer)  # Update manufacturer
            
        logger.info(f"Successfully loaded {len(device_types)} device types")

    def load_device_roles(self):
        """Load DeviceRole data from NetBox."""
        device_roles = self.netbox_api.dcim.device_roles.all()

        for device_role in device_roles:
            device_role_model = self.device_role(
                name=device_role.name,
                slug=device_role.slug,
                id=device_role.id,
            )
            self.add(device_role_model)
        logger.info(f"Successfully loaded {len(device_roles)} device roles")

    def load_sites(self):
        """Load Site data from NetBox."""
        sites = self.netbox_api.dcim.sites.all()

        for site in sites:
            site_model = self.site(
                name=site.name,
                slug=site.slug,
                id=site.id,
            )
            self.add(site_model)
        logger.info(f"Successfully loaded {len(sites)} sites")

    def load_devices(self):
        """Load Device data from NetBox."""
        devices = self.netbox_api.dcim.devices.all()

        for device in devices:
            device_model = self.device(
                name=device.name,
                device_type_name=device.device_type.model,
                device_role_name=device.role.name,
                site_name=device.site.name,
                status=device.status.value,
                id=device.id,
            )
            self.add(device_model)

            # Add device as a child of its device_type, site, and device_role
            device_type = self.get(DeviceTypeNetBoxModel, {"model": device.device_type.model})
            device_type.add_child(device_model)
            self.update(device_type)  # Update device_type

            device_role = self.get(DeviceRoleNetBoxModel, {"name": device.role.name})
            device_role.add_child(device_model)
            self.update(device_role)  # Update device_role

            site = self.get(SiteNetBoxModel, {"name": device.site.name})
            site.add_child(device_model)
            self.update(site)  # Update site

        logger.info(f"Successfully loaded {len(devices)} devices")