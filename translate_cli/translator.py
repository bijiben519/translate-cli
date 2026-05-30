"""Translation logic wrapping deep-translator (Google Translate)."""

import requests

from deep_translator import GoogleTranslator
from deep_translator.exceptions import (
    LanguageNotSupportedException,
    TranslationNotFound,
    RequestError,
)


SUPPORTED_LANGUAGES = {
    "af": "afrikaans", "sq": "albanian", "am": "amharic", "ar": "arabic",
    "hy": "armenian", "az": "azerbaijani", "eu": "basque", "be": "belarusian",
    "bn": "bengali", "bs": "bosnian", "bg": "bulgarian", "ca": "catalan",
    "ceb": "cebuano", "ny": "chichewa", "zh-CN": "chinese (simplified)",
    "zh-TW": "chinese (traditional)", "co": "corsican", "hr": "croatian",
    "cs": "czech", "da": "danish", "nl": "dutch", "en": "english",
    "eo": "esperanto", "et": "estonian", "tl": "filipino", "fi": "finnish",
    "fr": "french", "fy": "frisian", "gl": "galician", "ka": "georgian",
    "de": "german", "el": "greek", "gu": "gujarati", "ht": "haitian creole",
    "ha": "hausa", "haw": "hawaiian", "iw": "hebrew", "hi": "hindi",
    "hmn": "hmong", "hu": "hungarian", "is": "icelandic", "ig": "igbo",
    "id": "indonesian", "ga": "irish", "it": "italian", "ja": "japanese",
    "jw": "javanese", "kn": "kannada", "kk": "kazakh", "km": "khmer",
    "ko": "korean", "ku": "kurdish (kurmanji)", "ky": "kyrgyz",
    "lo": "lao", "la": "latin", "lv": "latvian", "lt": "lithuanian",
    "lb": "luxembourgish", "mk": "macedonian", "mg": "malagasy",
    "ms": "malay", "ml": "malayalam", "mt": "maltese", "mi": "maori",
    "mr": "marathi", "mn": "mongolian", "my": "myanmar (burmese)",
    "ne": "nepali", "no": "norwegian", "ps": "pashto", "fa": "persian",
    "pl": "polish", "pt": "portuguese", "pa": "punjabi", "ro": "romanian",
    "ru": "russian", "sm": "samoan", "gd": "scots gaelic", "sr": "serbian",
    "st": "sesotho", "sn": "shona", "sd": "sindhi", "si": "sinhala",
    "sk": "slovak", "sl": "slovenian", "so": "somali", "es": "spanish",
    "su": "sundanese", "sw": "swahili", "sv": "swedish", "tg": "tajik",
    "ta": "tamil", "te": "telugu", "th": "thai", "tr": "turkish",
    "uk": "ukrainian", "ur": "urdu", "uz": "uzbek", "vi": "vietnamese",
    "cy": "welsh", "xh": "xhosa", "yi": "yiddish", "yo": "yoruba", "zu": "zulu",
}

# Convenience aliases for common language codes
LANGUAGE_ALIASES = {
    "zh": "zh-CN",
}


def detect_language(text: str) -> str:
    """Detect the language of the given text.

    Returns the language code (e.g., 'fr', 'en').
    """
    try:
        from langdetect import detect
        result = detect(text)
        # Normalize zh-cn to zh-CN etc.
        return result
    except Exception as e:
        raise TranslationError(f"Failed to detect language: {e}") from e


def translate_text(
    text: str,
    source: str = "auto",
    target: str = "en",
) -> str:
    """Translate text from source language to target language.

    Args:
        text: The text to translate.
        source: Source language code (default 'auto' for auto-detection).
        target: Target language code (default 'en').

    Returns the translated text.
    """
    # Resolve convenience aliases
    source = LANGUAGE_ALIASES.get(source, source)
    target = LANGUAGE_ALIASES.get(target, target)
    try:
        translator = GoogleTranslator(source=source, target=target)
        result = translator.translate(text)
        return result
    except LanguageNotSupportedException as e:
        raise TranslationError(f"Language not supported: {e}") from e
    except RequestError as e:
        msg = str(e).lower()
        if "429" in msg or "too many" in msg:
            raise TranslationError(
                "Rate limit exceeded. Please wait a moment and try again."
            ) from e
        raise TranslationError(
            f"Network error — check your internet connection. ({e})"
        ) from e
    except TranslationNotFound as e:
        raise TranslationError(f"Could not translate the given text: {e}") from e
    except requests.exceptions.ConnectionError as e:
        raise TranslationError(
            f"Network error — check your internet connection. ({e})"
        ) from e


def list_languages() -> dict[str, str]:
    """Return a dict of supported language codes to language names."""
    return dict(SUPPORTED_LANGUAGES)


class TranslationError(Exception):
    """Raised when translation or detection fails."""
    pass
