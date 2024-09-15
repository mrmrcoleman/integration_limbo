from setuptools import setup, find_packages

setup(
    name='integration-limbo',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,  # Ensure non-code files are included
    install_requires=[
        'requests',
        'pynetbox',
        'diffsync',
        'rich',
        'python-dotenv',
    ],
    package_data={
        'integration_limbo': ['integrations/netbox-to-digitalocean/*.py'],  # Ensure all relevant Python files are included
    }
)