import json
import sys
import asyncio
import os
import logging
from pathlib import Path
from argparse import ArgumentParser

try:
    from trengine import AsyncEngine
except ImportError:
    print(
        "Module 'trengine' not found. Please install it using 'pip install trengine' and try again."
    )
    sys.exit(1)

logging.basicConfig(level=logging.INFO)


def parse_args():
    parser = ArgumentParser(
        description="Generate translations for a given language code."
    )
    parser.add_argument("iso_code", help="ISO code of the language (e.g., 'es')")
    return parser.parse_args()


def load_languages():
    with open(Path(__file__).parent / "languages.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_language_data(lang_code, langs):
    filtered = [lang for lang in langs if lang["Code"].lower() == lang_code]
    if not filtered:
        raise ValueError(f"Language code: {lang_code} not found.")
    return filtered[0]


async def translate(translator: AsyncEngine, string: str, lang_code: str):
    engines = [translator.google, translator.hozory, translator.tdict, translator.tr]
    text, source_lang, to_lang = string, "en", lang_code

    for engine in engines:
        try:
            args = {
                "text": text,
                "to_language": to_lang,
                "source_language": source_lang,
            }
            if engine == translator.hozory:
                args = {"text": text, "target": to_lang}
            result = await engine.translate(**args)
            return result if isinstance(result, str) else result.translated_text
        except Exception as e:
            logging.warning(f"{e.__class__.__name__}: Retrying with other translator.")
    raise RuntimeError("All translation engines failed.")


async def main():
    args = parse_args()
    lang_code = args.iso_code.lower()
    langs = load_languages()
    lang_data = get_language_data(lang_code, langs)

    translator = AsyncEngine()

    with open(Path(__file__).parent / "en.json", "r", encoding="utf-8") as f:
        original = json.load(f)

    to_write = {}

    async def process_translation(k, v):
        if k == "LANGUAGE":
            return "{} {}".format(lang_data["NativeName"], lang_data["Flag"])
        elif k == "LINK_DEV":
            return v
        elif k == "LANG_COMMAND":
            return v.replace("🇮🇱", lang_data["Flag"])
        return (
            "\n".join(
                [
                    await translate(translator, line, lang_code) if line else line
                    for line in v.splitlines()
                ]
            )
            if "\n" in v
            else await translate(translator, v, lang_code)
        )

    tasks = [process_translation(k, v) for k, v in original.items()]
    results = await asyncio.gather(*tasks)

    logging.info(results)

    for (k, _), result in zip(original.items(), results):
        to_write[k] = result
        logging.info(f"[{k}] Translated Successfully to [{lang_data['EnglishName']}].")

    with open(Path(__file__).parent / f"{lang_code}.json", "w", encoding="utf-8") as f:
        json.dump(to_write, f, indent=4, ensure_ascii=False)

    logging.info(f"Generated successfully to [./{lang_code}.json]")

    utils_path = Path(__file__).parent.parent / "tg" / "utils.py"
    with open(utils_path, "r") as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.strip().startswith("list_langs = ["):
            start = line.index("[")
            end = line.index("]")
            existing_list = line[start + 1 : end].strip()
            langs = [lang.strip().strip('"') for lang in existing_list.split(",")]
            if lang_code not in langs:
                langs.append(lang_code)
            updated_list = ", ".join(f'"{lang}"' for lang in langs)
            lines[i] = f"list_langs = [{updated_list}]\n"
            break

    with open(utils_path, "w") as file:
        file.writelines(lines)

    logging.info(f"Added '{lang_code}' to the list and updated tg/utils.py.")
    os.system("ruff format")


if __name__ == "__main__":
    asyncio.run(main())
