# Install

## From GitHub (recommended)

```bash
pipx install git+https://github.com/bijiben519/translate-cli.git
```

## From wheel (offline / local network)

Build the wheel on one machine, then copy to others:

```bash
# Build
cd translate-cli
pipx run build

# The wheel is at dist/translate_cli-0.1.0-py3-none-any.whl
# Copy it to the target machine and install:
pipx install translate_cli-0.1.0-py3-none-any.whl
```

## From source

```bash
git clone https://github.com/bijiben519/translate-cli.git
cd translate-cli
pipx install .
```
