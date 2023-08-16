import yaml
import typing
import httpx
import asyncio

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

def read_config(name):
    """
    Read the yaml config
    """

    with open(name, 'r') as stream:
        try:
            config: Config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

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

    try:
        url = site["url"] + site["endpoint"]
        print("Pinging", url)
        response = await client.get(url)
    except:
        return False

    if response.status_code != site["expected_status"]:
        return False

    return True

async def ping_forever(cfg: Config):
    """
    Ping forever
    """

    while True:
        try:
            for site in cfg["sites"]:
                if not await ping(site):
                    print("Site", site["name"], "is down")
            print("Sleeping for", cfg["interval"], "seconds")
            await asyncio.sleep(cfg["interval"])
        except KeyboardInterrupt:
            break


async def main():

    config = read_config(CONFIG_FILE)

    await ping_forever(config)

if __name__ == "__main__":
    asyncio.run(main())