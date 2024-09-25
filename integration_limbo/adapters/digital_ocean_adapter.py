import requests
import logging
import json
import os
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

class DigitalOceanAdapter(Adapter):
    """Adapter for syncing DigitalOcean data to NetBox."""

    manufacturer = ManufacturerModel
    device_type = DeviceTypeModel
    device_role = DeviceRoleModel
    site = SiteModel
    device = DeviceModel

    # Top level objects to sync
    top_level = ["site", "manufacturer", "device_role"]

    def __init__(self, api_token, test_mode=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_token = api_token
        self.api_base_url = "https://api.digitalocean.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        self.created_sites = {}  # Cache for created sites (regions)
        self.test_mode = test_mode

    def load(self):
        """Load data from DigitalOcean and populate the models."""
        try:
            logger.info("### Starting data load from DigitalOcean ###")

            # Load manufacturers
            self.load_manufacturers()

            # Load device roles
            self.load_device_roles()

            # Load devices and dynamically create device types and sites
            self.load_devices()

        except Exception as e:
            logger.error(f"Failed to load data from DigitalOcean: {e}")

    def load_manufacturers(self):
        """Load manufacturers. For DigitalOcean, this could be a default like 'DigitalOcean'."""
        logger.debug("Loading manufacturers...")
        try:
            digitalocean_manufacturer = ManufacturerModel(
                name="DigitalOcean",
                description="Cloud provider",
                slug="digitalocean",
            )
            self.add(digitalocean_manufacturer)
            logger.debug(f"Loaded manufacturer: {digitalocean_manufacturer.name}")
            logger.info("Successfully loaded manufacturer: DigitalOcean")
        except Exception as e:
            logger.error(f"Error loading manufacturers: {e}")

    def load_device_roles(self):
        """Load device roles. For now, this can be generic like 'Droplet'."""
        logger.debug("Loading device roles...")
        try:
            droplet_role = DeviceRoleModel(name="Droplet", slug="droplet")
            self.add(droplet_role)

            logger.debug(f"Loaded device role: {droplet_role.name}")
            logger.info("Successfully loaded device role: Droplet")
        except Exception as e:
            logger.error(f"Error loading device roles: {e}")

    def load_devices(self):
        """Load DigitalOcean Droplets as NetBox devices and dynamically create device types and sites."""
        logger.debug("Loading devices (Droplets) from DigitalOcean API...")
        try:
            response = requests.get(f"{self.api_base_url}/droplets", headers=self.headers)
            response.raise_for_status()
            droplets_data = response.json()

            # Ensure the directory exists
            os.makedirs('test_data/digitalocean/', exist_ok=True)

            # Save to disk
            if not self.test_mode:
                with open('test_data/digitalocean/droplets.json', 'w') as f:
                    json.dump(droplets_data, f, indent=4)

            droplets = droplets_data.get("droplets", [])
            if not droplets:
                logger.warning("No droplets returned from the API")

            for droplet in droplets:
                try:
                    logger.debug(f"Processing droplet: {droplet['name']}")

                    # Check if the device type already exists, if not, create it
                    device_type_slug = droplet["size_slug"]
                    try:
                        device_type_model = self.get(DeviceTypeModel, {"model": device_type_slug})
                        logger.debug(f"Reusing existing device type: {device_type_slug}")
                    except ObjectNotFound:
                        # If the device type does not exist, create it
                        logger.debug(f"Creating new device type for {device_type_slug}")
                        device_type_model = DeviceTypeModel(
                            model=device_type_slug,
                            manufacturer_name="DigitalOcean",
                            slug=device_type_slug,
                        )
                        self.add(device_type_model)

                        # Add device type as a child of manufacturer
                        digitalocean_manufacturer = self.get(ManufacturerModel, {"name": "DigitalOcean"})
                        digitalocean_manufacturer.add_child(device_type_model)
                        self.update(digitalocean_manufacturer)  # Update manufacturer

                    # Check if the site (region) already exists, if not, create it
                    region_name = droplet["region"]["name"]
                    if region_name in self.created_sites:
                        site_model = self.created_sites[region_name]
                        logger.debug(f"Reusing existing site (region): {region_name}")
                    else:
                        try:
                            site_model = self.get(SiteModel, {"name": region_name})
                            logger.debug(f"Reusing existing site (region): {region_name}")
                        except ObjectNotFound:
                            logger.debug(f"Creating new site (region) for {region_name}")
                            site_model = SiteModel(
                                name=region_name,
                                slug=droplet["region"]["slug"],
                            )
                            self.add(site_model)
                            # Cache the created site to avoid redundant lookups
                            self.created_sites[region_name] = site_model

                    # Create the device
                    device_model = DeviceModel(
                        name=droplet["name"],
                        device_type_name=device_type_slug,
                        device_role_name="Droplet",
                        site_name=region_name,
                        status="active",
                    )
                    self.add(device_model)
                    logger.debug(f"Successfully added device: {droplet['name']}")

                    # Establish child relationships (add device as a child of device type, site, and role)
                    device_type_model.add_child(device_model)
                    self.update(device_type_model)  # Update device type

                    site_model.add_child(device_model)
                    self.update(site_model)  # Update site

                    droplet_role_model = self.get(DeviceRoleModel, {"name": "Droplet"})
                    droplet_role_model.add_child(device_model)
                    self.update(droplet_role_model)  # Update device role

                except Exception as e:
                    logger.error(f"Error processing droplet {droplet['name']}: {e}")
                    # Continue processing the next droplet even if this one fails
                    continue

            logger.info(f"Successfully processed {len(droplets)} droplets")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error loading droplets from DigitalOcean API: {e}")
        except Exception as e:
            logger.error(f"Failed to load data from DigitalOcean: {e}")