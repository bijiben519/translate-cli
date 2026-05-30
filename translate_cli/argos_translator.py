"""Offline translation backend using Argos Translate."""

from translate_cli.translator import TranslationError

# Map our language codes to Argos Translate codes
_CODE_MAP = {
    "zh-CN": "zh",
    "zh-TW": "zt",
    "zh": "zh",
}


def _to_argos(code: str) -> str:
    return _CODE_MAP.get(code, code)


def _ensure_model(source: str, target: str):
    """Ensure the language model for source->target is installed.

    Downloads from the internet on first use; works offline thereafter.
    """
    import argostranslate.package
    import argostranslate.translate

    source = _to_argos(source)
    target = _to_argos(target)

    installed = argostranslate.translate.get_installed_languages()
    for pair in installed:
        if pair.from_code == source and pair.to_code == target:
            return  # already installed

    # Download the package
    argostranslate.package.update_package_index()
    available = argostranslate.package.get_available_packages()
    pkg = next(
        (p for p in available if p.from_code == source and p.to_code == target),
        None,
    )
    if pkg is None:
        raise TranslationError(
            f"No offline model for {source} -> {target}. "
            f"Try a different language pair."
        )
    pkg.install()


def translate_text(text: str, source: str = "auto", target: str = "en") -> str:
    """Translate text offline using Argos Translate."""
    try:
        import argostranslate.translate
    except ImportError:
        raise TranslationError(
            "Argos Translate is not installed. Run: pip install argostranslate"
        )

    # Auto-detect source language (langdetect works offline)
    if source == "auto":
        from langdetect import detect
        detected = detect(text)
        source = detected

    source = _to_argos(source)
    target = _to_argos(target)

    try:
        _ensure_model(source, target)
    except TranslationError:
        raise
    except Exception as e:
        raise TranslationError(
            f"Failed to download language model: {e}\n"
            f"Make sure you have internet for the first download."
        )

    try:
        result = argostranslate.translate.translate(text, source, target)
        return result
    except Exception as e:
        raise TranslationError(f"Translation failed: {e}")


def detect_language(text: str) -> str:
    """Detect the language of the given text (offline)."""
    try:
        from langdetect import detect
        return detect(text)
    except Exception as e:
        raise TranslationError(f"Failed to detect language: {e}")


def list_languages() -> dict[str, str]:
    """List installed language pairs (not all possible pairs)."""
    try:
        import argostranslate.translate
        installed = argostranslate.translate.get_installed_languages()
        result = {}
        for pair in installed:
            key = f"{pair.from_code} -> {pair.to_code}"
            result[key] = f"{pair.from_name} → {pair.to_name}"
        return result
    except ImportError:
        return {}
