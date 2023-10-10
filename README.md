# Pinger
> A simple tool to ping a list of sites' health status.

### Config

The list of sites is read from a YAML file. The file should be named `config.yaml` and placed in the same directory as the executable.

```yaml
# config.yaml
interval: 5 # seconds
timeout: 2 # seconds
sites:
    - name: Google
      url: https://google.com
      endpoint: /api/health
      expected_status: 200
    - name: Facebook
      url: https://facebook.com
      endpoint: /api/health
      expected_status: 200
```

### Installation

Install with pipx:

`pipx install git+https://github.com/aarhusstadsarkiv/pinger.git`