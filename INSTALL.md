# Install

## From GitHub (recommended, needs internet)

```bash
pipx install git+https://github.com/bijiben519/translate-cli.git
```

## From wheel (local network)

Build the wheel on one machine, then copy to others:

```bash
# Build
cd translate-cli
pipx run build

# The wheel is at dist/translate_cli-0.1.0-py3-none-any.whl
# Copy it to the target machine and install:
pipx install translate_cli-0.1.0-py3-none-any.whl
```

## Offline bundle (fully offline, with translation models)

Build the bundle on a machine with internet, then copy:

```bash
# 1. On the internet-connected machine
cd translate-cli
chmod +x build-offline.sh
./build-offline.sh
# Produces: translate-cli-offline.tar.gz (~300MB)

# 2. Copy to the offline machine and install
tar xzf translate-cli-offline.tar.gz
cd translate-cli-offline
./install.sh

# 3. Try it (no internet needed)
translate -o "hello"    # 哈啰
translate -o "你好"      # Hello.
```

## From source

```bash
git clone https://github.com/bijiben519/translate-cli.git
cd translate-cli
pipx install .
```
