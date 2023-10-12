import yaml
import typing
import httpx
import os
import sys
import asyncio
import watchdog
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

log = logging.getLogger(__name__)

CONFIG_FILE = "config.yaml"

class ConfigSite(typing.TypedDict):
    name: str
    url: str
    endpoint: str
    expected_status: int

class Config(typing.TypedDict):
    sites: typing.List[ConfigSite]
    interval: int
    timeout: int

client = httpx.AsyncClient()

config: Config = {}

class ConfigHandler(FileSystemEventHandler):
    def on_modified(self, event):
        log.info("Config file modified")
        read_config(CONFIG_FILE)

def read_config(name):
    """
    Read the yaml config
    """
    global config

    if not os.path.exists(name):
        log.critical(f"Config '{name}' file does not exist")
        sys.exit(1)

    with open(name, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError:
            log.exception("Error parsing config file")

    config.setdefault("interval", 60)
    config.setdefault("timeout", 10)
    config.setdefault("sites", [])

    assert isinstance(config["sites"], list), "sites must be a list"
    for site in config["sites"]:
        assert isinstance(site, dict), "site must be a mapping"
        assert "name" in site, "site must have a name"
        assert "url" in site, "site must have a url"
        assert "endpoint" in site, "site must have an endpoint"
        assert "expected_status" in site, "site must have an expected_status"

    client.timeout = config["timeout"]

    return config

async def ping(site: ConfigSite):
    """
    Ping a site
    """
    s = True
    try:
        url = site["url"] + site["endpoint"]
        log.info(f"Pinging {url}")
        response = await client.get(url)

        if response.status_code != site["expected_status"]:
            s = False
    except:
        s = False

    if not s:
        log.info(f"Site {site['name']} is down")
    return s

async def ping_forever(site: ConfigSite):
    """
    Ping forever
    """

    _task = None
    while True:
        try:
            _task = asyncio.create_task(ping(site))
            log.info(f"Sleeping for {config['interval']} seconds")
            await asyncio.sleep(config["interval"])
        except KeyboardInterrupt:
            break

async def ping_sites():
    """
    Ping sites forever
    """
    await asyncio.gather(*[ping_forever(site) for site in config["sites"]])


async def run():

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    read_config(CONFIG_FILE)

    event_handler = ConfigHandler()
    observer = Observer()
    observer.schedule(event_handler, path='./', recursive=False)
    observer.start()

    await ping_sites()

    observer.stop()
    observer.join()

def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()