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

# Import statements adjusted for diffsync 2.0.0
from diffsync import DiffSyncFlags
from diffsync.diff import Diff
from diffsync.enum import DiffSyncActions

from integration_limbo.adapters.netbox_adapter import NetBoxAdapter
from integration_limbo.adapters.digital_ocean_adapter import DigitalOceanAdapter
from integration_limbo.adapters.mocks import mock_requests_get, mock_requests_post

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
        logger.info("Running in test mode with mocked DigitalOcean API responses.")

        # Apply mocks for DigitalOcean API
        with mock.patch('requests.get', side_effect=mock_requests_get), \
             mock.patch('requests.post', side_effect=mock_requests_post):
            run_sync(args, netbox_token, digital_ocean_token, test_mode=True)
    else:
        run_sync(args, netbox_token, digital_ocean_token, test_mode=False)

def run_sync(args, netbox_token, digital_ocean_token, test_mode=False):
    # Create a NetBox API instance
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
        branch_schema_id=branch_schema_id,
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

    if args.dry_run:
        # If --dry-run is specified, just show the diff and exit
        diff = local_netbox.diff_from(digital_ocean)
        print("### DRY-RUN MODE: Displaying diff ###")
        print(diff.str())
        sys.exit(0)

    if args.sync:
        # If --sync is specified, perform the sync operation
        print("### SYNC MODE: Synchronizing changes ###")

        # First, process creations and updates (skip deletions)
        logger.info("Synchronizing creations and updates...")
        local_netbox.sync_from(digital_ocean, flags=DiffSyncFlags.SKIP_UNMATCHED_DST)

        # Then, re-calculate the diff and process deletions
        logger.info("Re-calculating diff and processing deletions...")
        diff = local_netbox.diff_from(digital_ocean)

        # Process deletions
        logger.info("Processing deletions...")
        for obj_type in diff.groups():
            for diff_element in diff.children[obj_type].values():
                if diff_element.action == DiffSyncActions.DELETE:
                    obj = local_netbox.get(diff_element.type, diff_element.keys)
                    if obj:
                        success = obj.delete()
                        if success:
                            logger.info(f"Deleted {obj_type} {diff_element.name}")
                        else:
                            logger.error(f"Failed to delete {obj_type} {diff_element.name}")
                    else:
                        logger.warning(f"Object {obj_type} {diff_element.name} not found in destination for deletion")

        print("### Sync complete! ###")
        sys.exit(0)

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
                status="ready",
                description="Created by: NetBox Labs - Digital Ocean to NetBox Sync"
            )
            logger.info(f"Branch '{branch_name}' created successfully.")

        # Wait until the branch is ready
        wait_for_branch_ready(branch, netbox_api)
        return branch

    except pynetbox.RequestError as e:
        logger.error(f"Failed to retrieve or create branch '{branch_name}': {e}")
        sys.exit(1)

def wait_for_branch_ready(branch, netbox_api, timeout=30):
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