"""Click CLI for the translation tool."""

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
    default="en",
    help="Target language code (default: en).",
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
def main(text, source, target, detect_mode, list_mode):
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
        return

    # Translate
    try:
        result = translate_text(input_text, source=source, target=target)
        click.echo(result)
    except TranslationError as e:
        raise click.ClickException(str(e))
