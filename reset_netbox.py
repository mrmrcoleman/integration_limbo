import pynetbox
import logging

# Setup basic logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# NetBox API configuration
NETBOX_API_URL = "YOUR NETBOX URL"
NETBOX_API_TOKEN = "YOUR API TOKEN"

# Initialize the NetBox API client
netbox = pynetbox.api(url=NETBOX_API_URL, token=NETBOX_API_TOKEN)


def delete_devices():
    """Delete all devices from NetBox."""
    try:
        logger.debug("Fetching all devices from NetBox...")
        devices = netbox.dcim.devices.all()

        if devices:
            for device in devices:
                logger.debug(f"Deleting device: {device.name}")
                device.delete()

            logger.info(f"Successfully deleted {len(devices)} devices")
        else:
            logger.info("No devices to delete.")
    except Exception as e:
        logger.error(f"Error deleting devices: {e}")


def delete_sites():
    """Delete all sites from NetBox."""
    try:
        logger.debug("Fetching all sites from NetBox...")
        sites = netbox.dcim.sites.all()

        if sites:
            for site in sites:
                logger.debug(f"Deleting site: {site.name}")
                site.delete()

            logger.info(f"Successfully deleted {len(sites)} sites")
        else:
            logger.info("No sites to delete.")
    except Exception as e:
        logger.error(f"Error deleting sites: {e}")


def delete_device_roles():
    """Delete all device roles from NetBox."""
    try:
        logger.debug("Fetching all device roles from NetBox...")
        device_roles = netbox.dcim.device_roles.all()

        if device_roles:
            for device_role in device_roles:
                logger.debug(f"Deleting device role: {device_role.name}")
                device_role.delete()

            logger.info(f"Successfully deleted {len(device_roles)} device roles")
        else:
            logger.info("No device roles to delete.")
    except Exception as e:
        logger.error(f"Error deleting device roles: {e}")


def delete_device_types():
    """Delete all device types from NetBox."""
    try:
        logger.debug("Fetching all device types from NetBox...")
        device_types = netbox.dcim.device_types.all()

        if device_types:
            for device_type in device_types:
                logger.debug(f"Deleting device type: {device_type.model}")
                device_type.delete()

            logger.info(f"Successfully deleted {len(device_types)} device types")
        else:
            logger.info("No device types to delete.")
    except Exception as e:
        logger.error(f"Error deleting device types: {e}")


def delete_manufacturers():
    """Delete all manufacturers from NetBox."""
    try:
        logger.debug("Fetching all manufacturers from NetBox...")
        manufacturers = netbox.dcim.manufacturers.all()

        if manufacturers:
            for manufacturer in manufacturers:
                logger.debug(f"Deleting manufacturer: {manufacturer.name}")
                manufacturer.delete()

            logger.info(f"Successfully deleted {len(manufacturers)} manufacturers")
        else:
            logger.info("No manufacturers to delete.")
    except Exception as e:
        logger.error(f"Error deleting manufacturers: {e}")


def delete_all_objects():
    """Delete all objects in the correct order to avoid referential integrity issues."""
    logger.info("Starting deletion of all objects in NetBox...")
    delete_devices()
    delete_sites()
    delete_device_roles()
    delete_device_types()
    delete_manufacturers()
    logger.info("Deletion of all objects complete.")


if __name__ == "__main__":
    delete_all_objects()
