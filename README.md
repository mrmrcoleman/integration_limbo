# integration_limbo
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

pip install -e .
```

## Provide API tokens via `.env` (local development)
**Tip:** You can also specify API token on the command line. See --help for details

```
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
python integration_limbo/integrations/netbox_to_digitalocean/main.py --dry-run --netbox-url "https://your.netbox"
```

## Run a Dry Run against an existing branch

```
python integration_limbo/integrations/netbox_to_digitalocean/main.py --dry-run --branch existingbranch --netbox-url "https://your.netbox"
```

## Run a Dry Run against an non-existant branch
**Tip:** --force will create the branch if it doesn't already exist

```
python integration_limbo/integrations/netbox_to_digitalocean/main.py --dry-run --branch newbranch --force --netbox-url "https://your.netbox"
```

## Run a Sync

```
python integration_limbo/integrations/netbox_to_digitalocean/main.py --sync --branch newbranch --force --netbox-url "https://your.netbox"
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

### Push it to the DockerHub

```
docker tag integration-limbo:latest mrmrcoleman/integration-limbo:latest
docker push mrmrcoleman/integration-limbo:latest
```

## Run through Docker locally
**Tip:** This is just an example. Tailor the command line arguments to your own needs.

```
docker run --rm \
    -e NETBOX_API_TOKEN="YourToken" \
    -e DIGITAL_OCEAN_API_TOKEN="YourToken" \
    -v $(pwd)/integration_limbo/integrations/netbox_to_digitalocean/main.py:/app/integration_limbo/integrations/netbox_to_digitalocean/main.py \
    integration-limbo:latest \
    python /app/integration_limbo/integrations/netbox_to_digitalocean/main.py --dry-run --branch test --netbox-url "https://your.netbox"
```

python setup.py sdist bdist_wheel
pip install dist/kriten_netbox-0.1.1-py3-none-any.whl