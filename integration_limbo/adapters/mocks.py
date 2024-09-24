import json
import os
import requests

def load_digitalocean_test_data(data_type):
    """Utility function to load DigitalOcean test data."""
    file_path = f'test_data/digitalocean/{data_type}.json'
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def mock_requests_get(url, headers=None, params=None):
    """Mock function to replace requests.get for DigitalOcean API."""
    if 'droplets' in url:
        data = load_digitalocean_test_data('droplets')
        return MockResponse(data)
    else:
        # Allow real requests for other URLs
        return requests.get(url, headers=headers, params=params)

def mock_requests_post(url, headers=None, json=None):
    """Mock function to replace requests.post for DigitalOcean API."""
    # Implement if needed
    return requests.post(url, headers=headers, json=json)

class MockResponse:
    def __init__(self, data, status_code=200):
        self.status_code = status_code
        self._data = data

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f'Status code: {self.status_code}')