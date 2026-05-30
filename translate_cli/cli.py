"""Click CLI for the translation tool."""

import subprocess
import sys

import click

from translate_cli.translator import (
    detect_language,
    list_languages,
    translate_text,
    TranslationError,
)


@click.command()
@click.argument("text", required=False)
@click.option(
    "-s", "--source",
    default="auto",
    help="Source language code (default: auto-detect).",
)
@click.option(
    "-t", "--target",
    default=None,
    help="Target language code (default: smart en/zh-CN based on detected language).",
)
@click.option(
    "--detect", "detect_mode",
    is_flag=True,
    help="Detect the language of the given text.",
)
@click.option(
    "--languages", "list_mode",
    is_flag=True,
    help="List all supported language codes.",
)
@click.option(
    "-c", "--copy",
    is_flag=True,
    help="Copy the result to clipboard.",
)
def main(text, source, target, detect_mode, list_mode, copy):
    """Translate text from the command line.

    TEXT is read from the first argument or from stdin (pipe-friendly).

    \b
    Examples:
      translate "hello" -t zh
      echo "hola" | translate -t en
      translate --detect "bonjour"
      translate --languages
    """
    # --languages flag
    if list_mode:
        langs = list_languages()
        for code, name in langs.items():
            click.echo(f"{code:<8} {name}")
        return

    # Gather input text: argument first, then stdin
    if text:
        input_text = text
    else:
        # Read from stdin if piped
        if not sys.stdin.isatty():
            input_text = sys.stdin.read().strip()
        else:
            raise click.UsageError(
                "No text provided. Pass text as an argument or pipe it via stdin."
            )

    if not input_text:
        raise click.UsageError("Empty input. Please provide text to translate or detect.")

    # --detect flag
    if detect_mode:
        try:
            result = detect_language(input_text)
            click.echo(result)
        except TranslationError as e:
            raise click.ClickException(str(e))
        if copy:
            _copy_to_clipboard(result)
        return

    # Translate
    try:
        if target is None:
            if _has_cjk(input_text):
                target = "en"
            else:
                target = "zh-CN"
        result = translate_text(input_text, source=source, target=target)
        click.echo(result)
        if copy:
            _copy_to_clipboard(result)
    except TranslationError as e:
        raise click.ClickException(str(e))


def _copy_to_clipboard(text: str) -> None:
    """Copy text to the system clipboard (macOS)."""
    try:
        subprocess.run(["pbcopy"], input=text.encode(), check=True)
    except Exception as e:
        raise click.ClickException(f"Failed to copy to clipboard: {e}")


def _has_cjk(text: str) -> bool:
    """Return True if text contains Chinese/Japanese/Korean characters."""
    for ch in text:
        cp = ord(ch)
        if (0x4E00 <= cp <= 0x9FFF     # CJK Unified Ideographs
                or 0x3400 <= cp <= 0x4DBF  # CJK Extension A
                or 0xF900 <= cp <= 0xFAFF  # CJK Compatibility Ideographs
                or 0x3040 <= cp <= 0x309F  # Hiragana
                or 0x30A0 <= cp <= 0x30FF  # Katakana
                or 0xAC00 <= cp <= 0xD7AF):  # Hangul
            return True
    return False
