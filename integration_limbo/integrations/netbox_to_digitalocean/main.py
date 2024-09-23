import argparse
import sys
import time
import logging
import os
from dotenv import load_dotenv
from rich import print
from rich.pretty import Pretty
import pynetbox
import requests
import unittest.mock as mock
from integration_limbo.adapters.netbox_adapter import NetBoxAdapter
from integration_limbo.adapters.digital_ocean_adapter import DigitalOceanAdapter
from integration_limbo.adapters.mocks import mock_requests_get

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Sync DigitalOcean with NetBox, with optional dry-run or sync modes.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--dry-run', action='store_true', help='Show the diff between DigitalOcean and NetBox without making any changes.')
    group.add_argument('--sync', action='store_true', help='Sync the changes from DigitalOcean to NetBox.')

    parser.add_argument('--branch', '-b', required=True, help='Specify the branch to write to. Use "main" for main branch.')
    parser.add_argument('--force', '-f', action='store_true', help='Create the branch if it does not exist.')
    parser.add_argument('--netbox-url', required=True, help='Specify the NetBox URL.')
    parser.add_argument('--netbox-token', help='Specify the NetBox API token. This will override the environment variable.')
    parser.add_argument('--digital-ocean-token', help='Specify the DigitalOcean API token. This will override the environment variable.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging.')
    parser.add_argument('--test-mode', action='store_true', help='Run in test mode using mocked API responses.')

    args = parser.parse_args()

    # Set logging level to DEBUG if --verbose is provided
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Fetch API tokens from environment variables if not provided on command line
    netbox_token = args.netbox_token or os.getenv('NETBOX_API_TOKEN')
    digital_ocean_token = args.digital_ocean_token or os.getenv('DIGITAL_OCEAN_API_TOKEN')

    if not netbox_token or not digital_ocean_token:
        logger.error("Both NETBOX_API_TOKEN and DIGITAL_OCEAN_API_TOKEN must be set either via command-line arguments or environment variables.")
        sys.exit(1)

    # Initialize the adapters and run the sync
    if args.test_mode:
        logger.info("Running in test mode with mocked API responses.")

        # Apply mocks for requests.get, excluding branch management
        with mock.patch('requests.get', side_effect=conditional_mock_requests_get(args.netbox_url)):
            run_sync(args, netbox_token, digital_ocean_token, test_mode=True)
    else:
        run_sync(args, netbox_token, digital_ocean_token, test_mode=False)

def conditional_mock_requests_get(netbox_url):
    """Return a side_effect function for mock.patch to conditionally mock requests.get."""
    def side_effect(url, *args, **kwargs):
        if netbox_url in url and 'plugins/branching/branches' in url:
            # Allow real requests for branch management
            return requests.get(url, *args, **kwargs)
        else:
            # Use the mock for other requests
            return mock_requests_get(url, *args, **kwargs)
    return side_effect

def run_sync(args, netbox_token, digital_ocean_token, test_mode=False):
    # Create a separate NetBox API instance for branch management
    netbox_api = pynetbox.api(url=args.netbox_url, token=netbox_token)

    # Check if we are writing to a branch
    if args.branch != "main":
        logger.info(f"Branch mode: {args.branch}")
        # Get or create the branch in NetBox
        branch = get_or_create_branch(netbox_api, args.branch, args.force)
        netbox_api.http_session.headers["X-NetBox-Branch"] = branch.schema_id
        branch_schema_id = branch.schema_id  # Store the branch schema ID
    else:
        logger.info("Operating on the main branch.")
        branch_schema_id = None  # No branch schema ID for the main branch

    # Initialize the local NetBox adapter (destination)
    local_netbox = NetBoxAdapter(
        url=args.netbox_url,
        token=netbox_token,
        branch_schema_id=branch_schema_id,  # Pass the branch schema ID
        test_mode=test_mode
    )

    # Initialize the DigitalOcean adapter (source)
    digital_ocean = DigitalOceanAdapter(
        api_token=digital_ocean_token,
        test_mode=test_mode
    )

    # Load data from both DigitalOcean (source) and NetBox (destination)
    logger.info("Loading data from NetBox and DigitalOcean...")
    local_netbox.load()
    digital_ocean.load()

    # Calculate the diff between DigitalOcean and the local NetBox instance
    logger.info("Calculating diff between DigitalOcean and NetBox...")
    diff = local_netbox.diff_from(digital_ocean)

    if args.dry_run:
        # If --dry-run is specified, just show the diff and exit
        print("### DRY-RUN MODE: Displaying diff ###")
        print(diff.summary())
        print(Pretty(diff.dict()))
        sys.exit(0)

    if args.sync:
        # If --sync is specified, perform the sync operation
        print("### SYNC MODE: Synchronizing changes ###")
        local_netbox.sync_from(digital_ocean)
        print("### Sync complete! ###")
        sys.exit(0)

# Function to get or create branch in NetBox
def get_or_create_branch(netbox_api, branch_name, force_create=False):
    """Retrieve or create a branch in NetBox."""
    try:
        # Try to get the branch
        branch = netbox_api.plugins.branching.branches.get(name=branch_name)
        if branch:
            logger.info(f"Branch '{branch_name}' already exists.")
        else:
            if not force_create:
                logger.error(f"Branch '{branch_name}' does not exist and --force was not specified.")
                sys.exit(1)
            # Create the branch if --force is specified
            branch = netbox_api.plugins.branching.branches.create(
                name=branch_name,
                status="ready",  # Adjust according to the API requirements
                description="Created by: NetBox Labs - Digital Ocean to NetBox Sync"
            )
            logger.info(f"Branch '{branch_name}' created successfully.")

        # Wait until the branch is ready
        wait_for_branch_ready(branch, netbox_api)
        return branch

    except pynetbox.RequestError as e:
        logger.error(f"Failed to retrieve or create branch '{branch_name}': {e}")
        sys.exit(1)

def wait_for_branch_ready(branch, netbox_api, timeout=10):
    """Wait for the branch to have status 'ready'."""
    logger.info(f"Waiting for branch '{branch.name}' to be ready...")
    elapsed_time = 0
    while branch.status != "ready":
        time.sleep(1)
        elapsed_time += 1
        if elapsed_time > timeout:
            logger.error(f"Timeout waiting for branch '{branch.name}' to be ready.")
            sys.exit(1)
        branch = netbox_api.plugins.branching.branches.get(name=branch.name)
    logger.info(f"Branch '{branch.name}' is now ready.")

if __name__ == "__main__":
    main()