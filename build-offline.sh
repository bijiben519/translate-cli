#!/bin/bash
# Build an offline bundle for translate-cli.
# Run this on a machine with internet access, then copy the bundle to the offline machine.
#
# Usage:
#   chmod +x build-offline.sh
#   ./build-offline.sh
#   # Produces translate-cli-offline.tar.gz (~300MB)
#
# On the target (offline) machine:
#   tar xzf translate-cli-offline.tar.gz
#   cd translate-cli-offline
#   ./install.sh

set -e

BUNDLE="translate-cli-offline"
rm -rf "$BUNDLE" "$BUNDLE.tar.gz"

echo "==> Building translate-cli wheel..."
pipx run build --wheel --outdir dist/ .
cp dist/translate_cli-*.whl /tmp/translate_cli.whl

echo "==> Downloading dependency wheels..."
pip3 download \
    --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    -d /tmp/translate-deps \
    /tmp/translate_cli.whl \
    argostranslate 2>&1 | tail -3

echo "==> Downloading en<->zh translation models..."
python3 -c "
import argostranslate.package
argostranslate.package.update_package_index()
pkgs = argostranslate.package.get_available_packages()
for code in ('en', 'zh'):
    target = 'zh' if code == 'en' else 'en'
    for p in pkgs:
        if p.from_code == code and p.to_code == target:
            print(f'Installing {p.from_code} -> {p.to_code}')
            p.install()
            break
"

echo "==> Bundling..."
mkdir -p "$BUNDLE/wheels"
cp /tmp/translate_cli.whl "$BUNDLE/wheels/"
cp /tmp/translate-deps/*.whl "$BUNDLE/wheels/"
cp -r ~/.local/share/argos-translate "$BUNDLE/models"

cat > "$BUNDLE/install.sh" << 'INSTALL'
#!/bin/bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> Installing translate-cli and dependencies..."
pipx install --no-deps "$DIR"/wheels/translate_cli-*.whl
pipx runpip translate-cli install --no-index --find-links "$DIR/wheels" argostranslate

echo "==> Installing translation models..."
mkdir -p ~/.local/share
cp -r "$DIR/models/argos-translate" ~/.local/share/

echo "==> Done! Try: translate -o 'hello'"
INSTALL
chmod +x "$BUNDLE/install.sh"

echo "==> Creating tarball..."
tar czf "$BUNDLE.tar.gz" "$BUNDLE"

echo "==> Done: $BUNDLE.tar.gz ($(du -sh $BUNDLE.tar.gz | cut -f1))"
