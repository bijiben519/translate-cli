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

    # Check if already installed
    for lang in argostranslate.translate.get_installed_languages():
        for tr in lang.translations_from:
            if tr.from_lang.code == source and tr.to_lang.code == target:
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

    # Auto-detect source language using CJK character detection
    if source == "auto":
        if _has_cjk(text):
            source = "zh"
        else:
            source = "en"

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


def _has_cjk(text: str) -> bool:
    """Return True if text contains Chinese/Japanese/Korean characters."""
    for ch in text:
        cp = ord(ch)
        if (0x4E00 <= cp <= 0x9FFF
                or 0x3400 <= cp <= 0x4DBF
                or 0xF900 <= cp <= 0xFAFF
                or 0x3040 <= cp <= 0x309F
                or 0x30A0 <= cp <= 0x30FF
                or 0xAC00 <= cp <= 0xD7AF):
            return True
    return False


def list_languages() -> dict[str, str]:
    """List installed language pairs (not all possible pairs)."""
    try:
        import argostranslate.translate
        installed = argostranslate.translate.get_installed_languages()
        result = {}
        for lang in installed:
            for tr in lang.translations_from:
                key = f"{tr.from_lang.code} -> {tr.to_lang.code}"
                result[key] = f"{tr.from_lang.name} → {tr.to_lang.name}"
        return result
    except ImportError:
        return {}
