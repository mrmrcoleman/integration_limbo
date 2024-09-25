from diffsync import DiffSyncModel
from typing import List

class ManufacturerModel(DiffSyncModel):
    """Model representing a manufacturer."""
    
    _modelname = "manufacturer"
    _identifiers = ("name",)
    _attributes = ("description", "slug")
    _children = {"device_type": "device_types"}

    name: str
    description: str = None
    slug: str
    id: int = None  # Store the id but don't use it in diffs
    device_types: List = []

    class Config:
        protected_namespaces = ()


class DeviceTypeModel(DiffSyncModel):
    """Model representing a device type."""
    
    _modelname = "device_type"
    _identifiers = ("model",)
    _attributes = ("manufacturer_name", "slug")
    _children = {"device": "devices"}

    model: str
    manufacturer_name: str  # Links to ManufacturerModel
    slug: str
    id: int = None  # Store the id but don't use it in diffs
    devices: List = []

    class Config:
        protected_namespaces = ()


class DeviceRoleModel(DiffSyncModel):
    """Model representing a device role."""
    
    _modelname = "device_role"
    _identifiers = ("name",)
    _attributes = ("slug",)
    _children = {"device": "devices"}

    name: str
    slug: str
    id: int = None  # Store the id but don't use it in diffs
    devices: List = []

    class Config:
        protected_namespaces = ()


class SiteModel(DiffSyncModel):
    """Model representing a site."""
    
    _modelname = "site"
    _identifiers = ("name",)
    _attributes = ("slug",)
    _children = {"device": "devices"}

    name: str
    slug: str
    id: int = None  # Store the id but don't use it in diffs
    devices: List = []

    class Config:
        protected_namespaces = ()


class DeviceModel(DiffSyncModel):
    """Model representing a device."""
    
    _modelname = "device"
    _identifiers = ("name",)
    _attributes = ("device_type_name", "device_role_name", "site_name", "status")  # Remove id from attributes

    name: str
    device_type_name: str  # Links to DeviceTypeModel
    device_role_name: str  # Links to DeviceRoleModel
    site_name: str  # Links to SiteModel
    status: str
    id: int = None  # Store the id but don't use it in diffs

    class Config:
        protected_namespaces = ()