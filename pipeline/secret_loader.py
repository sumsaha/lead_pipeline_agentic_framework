import os
def load_secret(name):
    # Priority: Vault -> ENV
    try:
        import hvac
        addr = os.environ.get('VAULT_ADDR')
        token = os.environ.get('VAULT_TOKEN')
        if addr and token:
            client = hvac.Client(url=addr, token=token)
            secret = client.secrets.kv.v2.read_secret_version(path=name)
            return secret['data']['data']
    except Exception:
        pass
    return os.environ.get(name.upper())
