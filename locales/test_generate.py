import pytest
import json
import sys
import io

# Add lang_code to sys.argv before importing generate
lang_code = "es"
sys.argv = ["generate.py", lang_code]

from .generate import translate, main  # noqa: E402


@pytest.mark.asyncio
async def test_translate():
    # Example test for the translate function
    text = "Hello"
    translated_text = await translate(text)
    assert translated_text is not None
    assert isinstance(translated_text, str)


@pytest.mark.asyncio
async def test_main(monkeypatch):
    # Mock the translate function to return the same text
    async def mock_translate(text):
        return text

    monkeypatch.setattr("locales.generate.translate", mock_translate)

    # Run the main function
    await main()

    # Verify the output file
    with open(f"./{lang_code}.json", "r", encoding="utf-8") as f:
        generated_data = json.load(f)
        assert generated_data["LANGUAGE"] == "Español 🇪🇸"
        assert generated_data["LANG_COMMAND"] == "Change the language 🇺🇸/🇪🇸"
