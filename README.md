# integration_limbo
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

pip install -e .
```

## Reset NetBox
```
python reset_netbox.py
```

## Provide API tokens via `.env` (local development)
**Tip:** You can also specify API token on the command line. See --help for details

```
cd integration_limbo
cp .env.example .env

# Put your API token values in .env
```

## Show help

```
python integration_limbo/integrations/netbox_to_digitalocean/main.py --help
```

## Run a Dry Run (shows the diff but doesn't apply the sync)

In this example we just diff against NetBox main

```
python integration_limbo/integrations/netbox_to_digitalocean/main.py --dry-run --branch test --netbox-url "https://high-jump.netboxlabs.tech"
```

## Run a Dry Run against an existing branch

```
python integration_limbo/integrations/netbox_to_digitalocean/main.py --dry-run --branch existingbranch --netbox-url "https://high-jump.netboxlabs.tech"
```

## Run a Dry Run against an non-existant branch
**Tip:** --force will create the branch if it doesn't already exist

```
python integration_limbo/integrations/netbox_to_digitalocean/main.py --dry-run --branch newbranch --force --netbox-url "https://high-jump.netboxlabs.tech"
```

## Run a Sync

```
python integration_limbo/integrations/netbox_to_digitalocean/main.py --sync --branch newbranch --force --netbox-url "https://high-jump.netboxlabs.tech"
```

## Creating the base image for Kriten.io

### Install Docker

```
snap install docker
```

### Clean up old image

```
docker rmi integration-limbo --force
```

### Create the image
```
docker build -t integration-limbo:latest .
```

## Run through Docker locally
**Tip:** This is just an example. Tailor the command line arguments to your own needs.

```
docker run --rm \
    -e NETBOX_API_TOKEN="YourToken" \
    -e DIGITAL_OCEAN_API_TOKEN="YourToken" \
    -v $(pwd)/integration_limbo/integrations/netbox_to_digitalocean/main.py:/app/integration_limbo/integrations/netbox_to_digitalocean/main.py \
    integration-limbo:latest \
    python /app/integration_limbo/integrations/netbox_to_digitalocean/main.py --dry-run --branch test --netbox-url "https://high-jump.netboxlabs.tech"
```
