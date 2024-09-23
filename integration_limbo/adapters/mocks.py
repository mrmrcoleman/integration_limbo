import json
import os
import requests
import unittest.mock as mock

def load_netbox_test_data(data_type):
    """Utility function to load NetBox test data."""
    file_path = f'test_data/netbox/{data_type}.json'
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def mock_requests_get(url, headers=None, params=None):
    """Mock function to replace requests.get in test mode."""
    if 'dcim/manufacturers' in url:
        data = load_netbox_test_data('manufacturers')
        return MockResponse({'results': data})
    elif 'dcim/device-types' in url:
        data = load_netbox_test_data('device_types')
        return MockResponse({'results': data})
    elif 'dcim/device-roles' in url:
        data = load_netbox_test_data('device_roles')
        return MockResponse({'results': data})
    elif 'dcim/sites' in url:
        data = load_netbox_test_data('sites')
        return MockResponse({'results': data})
    elif 'dcim/devices' in url:
        data = load_netbox_test_data('devices')
        return MockResponse({'results': data})
    elif 'droplets' in url:
        data = load_digitalocean_test_data('droplets')
        return MockResponse(data)
    else:
        # Handle other URLs or raise an exception
        return MockResponse({}, status_code=404)

def load_digitalocean_test_data(data_type):
    """Utility function to load DigitalOcean test data."""
    file_path = f'test_data/digitalocean/{data_type}.json'
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

class MockResponse:
    def __init__(self, data, status_code=200):
        self.status_code = status_code
        self._data = data

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f'Status code: {self.status_code}')