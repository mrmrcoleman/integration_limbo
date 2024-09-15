from diffsync import DiffSyncModel

class ManufacturerModel(DiffSyncModel):
    """Model representing a manufacturer."""
    
    _modelname = "manufacturer"
    _identifiers = ("name",)
    _attributes = ("description", "description", "slug")  # Remove id from attributes

    name: str
    description: str = None
    slug: str  # Add slug here as well
    id: int = None  # Store the id but don't use it in diffs

    class Config:
        protected_namespaces = ()  # Set to an empty tuple

class DeviceTypeModel(DiffSyncModel):
    """Model representing a device type."""
    
    _modelname = "device_type"
    _identifiers = ("model",)  # Use 'model' as the identifier
    _attributes = ("manufacturer_name", "slug")  # Remove id from attributes

    model: str  # Use 'model' instead of 'name'
    manufacturer_name: str  # Links to ManufacturerModel
    slug: str
    id: int = None  # Store the id but don't use it in diffs

    class Config:
        protected_namespaces = ()  # Set to an empty tuple

class DeviceRoleModel(DiffSyncModel):
    """Model representing a device role."""
    
    _modelname = "device_role"
    _identifiers = ("name",)
    _attributes = ("slug",)  # Remove id from attributes

    name: str
    slug: str
    id: int = None  # Store the id but don't use it in diffs

    class Config:
        protected_namespaces = ()  # Set to an empty tuple

class SiteModel(DiffSyncModel):
    """Model representing a site."""
    
    _modelname = "site"
    _identifiers = ("name",)
    _attributes = ("slug",)  # Remove id from attributes

    name: str
    slug: str
    id: int = None  # Store the id but don't use it in diffs

    class Config:
        protected_namespaces = ()  # Set to an empty tuple

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
        protected_namespaces = ()  # Set to an empty tuple