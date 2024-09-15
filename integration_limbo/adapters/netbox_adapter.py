import pynetbox
import logging
from diffsync import Adapter
from integration_limbo.integrations.netbox_to_digitalocean.models import ManufacturerModel, DeviceTypeModel, DeviceRoleModel, SiteModel, DeviceModel

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ManufacturerNetBoxModel(ManufacturerModel):
    """NetBox-specific implementation of Manufacturer CRUD methods."""
    
    @classmethod
    def create(cls, adapter, ids, attrs):
        """Create a new manufacturer in NetBox."""
        new_manufacturer = adapter.netbox_api.dcim.manufacturers.create(
            name=ids["name"],
            description=attrs["description"],
            slug=attrs["slug"]
        )
        logger.info(f"Created manufacturer: {new_manufacturer.name}")
        
        # Capture and store the NetBox ID after creation
        ids["id"] = new_manufacturer.id
        return super().create(adapter, ids=ids, attrs=attrs)

    def delete(self):
        """Delete a manufacturer in NetBox."""
        manufacturer = self.adapter.netbox_api.dcim.manufacturers.get(name=self.name)
        if manufacturer:
            manufacturer.delete()
            logger.info(f"Deleted manufacturer: {self.name}")
        return super().delete()


class DeviceTypeNetBoxModel(DeviceTypeModel):
    """NetBox-specific implementation of DeviceType CRUD methods."""
    
    @classmethod
    def create(cls, adapter, ids, attrs):
        """Create a new device type in NetBox."""
        manufacturer = adapter.get(ManufacturerNetBoxModel, {"name": attrs["manufacturer_name"]})
        
        if not manufacturer:
            logger.error(f"Manufacturer {attrs['manufacturer_name']} not found in NetBox.")
            raise ValueError(f"Manufacturer {attrs['manufacturer_name']} not found in NetBox.")
        
        new_device_type = adapter.netbox_api.dcim.device_types.create(
            model=ids["model"],
            manufacturer=manufacturer.id,
            slug=attrs["slug"]
        )
        logger.info(f"Created device type: {new_device_type.model}")
        
        # Capture and store the NetBox ID after creation
        ids["id"] = new_device_type.id
        return super().create(adapter, ids=ids, attrs=attrs)

    def delete(self):
        """Delete a device type in NetBox."""
        device_type = self.adapter.netbox_api.dcim.device_types.get(model=self.model)
        if device_type:
            device_type.delete()
            logger.info(f"Deleted device type: {self.model}")
        return super().delete()


class DeviceRoleNetBoxModel(DeviceRoleModel):
    """NetBox-specific implementation of DeviceRole CRUD methods."""
    
    @classmethod
    def create(cls, adapter, ids, attrs):
        """Create a new device role in NetBox."""
        new_device_role = adapter.netbox_api.dcim.device_roles.create(
            name=ids["name"],
            slug=attrs["slug"]
        )
        logger.info(f"Created device role: {new_device_role.name}")
        
        # Capture and store the NetBox ID after creation
        ids["id"] = new_device_role.id
        return super().create(adapter, ids=ids, attrs=attrs)

    def delete(self):
        """Delete a device role in NetBox."""
        device_role = self.adapter.netbox_api.dcim.device_roles.get(name=self.name)
        if device_role:
            device_role.delete()
            logger.info(f"Deleted device role: {self.name}")
        return super().delete()


class SiteNetBoxModel(SiteModel):
    """NetBox-specific implementation of Site CRUD methods."""
    
    @classmethod
    def create(cls, adapter, ids, attrs):
        """Create a new site in NetBox."""
        new_site = adapter.netbox_api.dcim.sites.create(
            name=ids["name"],
            slug=attrs["slug"]
        )
        logger.info(f"Created site: {new_site.name}")
        
        # Capture and store the NetBox ID after creation
        ids["id"] = new_site.id
        return super().create(adapter, ids=ids, attrs=attrs)

    def delete(self):
        """Delete a site in NetBox."""
        site = self.adapter.netbox_api.dcim.sites.get(name=self.name)
        if site:
            site.delete()
            logger.info(f"Deleted site: {self.name}")
        return super().delete()


class DeviceNetBoxModel(DeviceModel):
    """NetBox-specific implementation of Device CRUD methods."""
    
    @classmethod
    def create(cls, adapter, ids, attrs):
        """Create a new device in NetBox."""
        device_type = adapter.get(DeviceTypeNetBoxModel, {"model": attrs["device_type_name"]})
        device_role = adapter.get(DeviceRoleNetBoxModel, {"name": attrs["device_role_name"]})
        site = adapter.get(SiteNetBoxModel, {"name": attrs["site_name"]})

        new_device = adapter.netbox_api.dcim.devices.create(
            name=ids["name"],
            device_type=device_type.id,
            role=device_role.id,
            site=site.id,
            status=attrs.get("status", "active")
        )
        logger.info(f"Created device: {new_device.name}")
        
        # Capture and store the NetBox ID after creation
        ids["id"] = new_device.id
        return super().create(adapter, ids=ids, attrs=attrs)

    def delete(self):
        """Delete a device in NetBox."""
        device = self.adapter.netbox_api.dcim.devices.get(name=self.name)
        if device:
            device.delete()
            logger.info(f"Deleted device: {self.name}")
        return super().delete()


class NetBoxAdapter(Adapter):
    """NetBox adapter that loads models and interacts with the NetBox API."""
    
    manufacturer = ManufacturerNetBoxModel
    device_type = DeviceTypeNetBoxModel
    device_role = DeviceRoleNetBoxModel
    site = SiteNetBoxModel
    device = DeviceNetBoxModel

    top_level = ["manufacturer", "device_type", "device_role", "site", "device"]

    def __init__(self, url, token, *args, **kwargs):
        """Initialize the adapter with NetBox API connection."""
        super().__init__(*args, **kwargs)
        self.netbox_api = pynetbox.api(url=url, token=token)

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
        manufacturers = self.netbox_api.dcim.manufacturers.all()
        for manufacturer in manufacturers:
            logger.debug(f"Loaded manufacturer: {manufacturer.name}")
            manufacturer_model = self.manufacturer(
                name=manufacturer.name,
                description=manufacturer.description,
                slug=manufacturer.slug,
                id=manufacturer.id
            )
            self.add(manufacturer_model)
        logger.info(f"Successfully loaded {len(manufacturers)} manufacturers")

    def load_device_types(self):
        """Load DeviceType data from NetBox."""
        device_types = self.netbox_api.dcim.device_types.all()
        for device_type in device_types:
            logger.debug(f"Loaded device type: {device_type.model}")
            device_type_model = self.device_type(
                model=device_type.model,
                manufacturer_name=device_type.manufacturer.name,
                slug=device_type.slug,
                id=device_type.id
            )
            self.add(device_type_model)
        logger.info(f"Successfully loaded {len(device_types)} device types")

    def load_device_roles(self):
        """Load DeviceRole data from NetBox."""
        device_roles = self.netbox_api.dcim.device_roles.all()
        for device_role in device_roles:
            logger.debug(f"Loaded device role: {device_role.name}")
            device_role_model = self.device_role(
                name=device_role.name,
                slug=device_role.slug,
                id=device_role.id
            )
            self.add(device_role_model)
        logger.info(f"Successfully loaded {len(device_roles)} device roles")

    def load_sites(self):
        """Load Site data from NetBox."""
        sites = self.netbox_api.dcim.sites.all()
        for site in sites:
            logger.debug(f"Loaded site: {site.name}")
            site_model = self.site(
                name=site.name,
                slug=site.slug,
                id=site.id
            )
            self.add(site_model)
        logger.info(f"Successfully loaded {len(sites)} sites")

    def load_devices(self):
        """Load Device data from NetBox."""
        devices = self.netbox_api.dcim.devices.all()
        for device in devices:
            logger.debug(f"Loaded device: {device.name}")
            device_model = self.device(
                name=device.name,
                device_type_name=device.device_type.model,
                device_role_name=device.role.name,
                site_name=device.site.name,
                status=device.status.value,
                id=device.id
            )
            self.add(device_model)
        logger.info(f"Successfully loaded {len(devices)} devices")