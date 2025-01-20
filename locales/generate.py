import json
import sys
import asyncio
import os

try:
    from trengine import AsyncEngine
except ImportError:
    print(
        "Module 'trengine' not found. Please install it using 'pip install trengine' and try again."
    )

if len(sys.argv) < 2:
    raise ValueError(
        "Usage: python generator.py <iso_code> | e.g: python generator.py es"
    )

lang_code = sys.argv[1].lower()

with open("./languages.json", "r", encoding="utf-8") as f:
    langs = json.load(f)
    filtered = [lang for lang in langs if lang["Code"].lower() == lang_code]

    if not filtered:
        raise ValueError(f"Language code: {lang_code} not found.")

    lang_data = filtered[0]

translator = AsyncEngine()


async def translate(string: str) -> str:
    engines = [translator.google, translator.hozory, translator.tdict, translator.tr]

    text, source_lang, to_lang = string, "en", lang_code

    for engine in engines:
        try:
            if engine == translator.google:
                args = {
                    "text": text,
                    "to_language": to_lang,
                    "source_language": source_lang,
                }
            elif engine == translator.hozory:
                args = {"text": text, "target": to_lang}
            elif engine == translator.tdict:
                args = {"text": text, "to_language": to_lang}
            else:
                args = {
                    "text": text,
                    "translated_lang": to_lang,
                    "source_lang": source_lang,
                }

            result = await engine.translate(**args)

            if isinstance(result, str):
                return result
            else:
                return result.translated_text
        except Exception as e:
            print(f"{e.__class__.__name__}: Retrying with other translator.")

    raise RuntimeError("All translation engines failed.")


async def main():
    with open("./en.json", "r", encoding="utf-8") as f:
        original: dict = json.loads(f.read())

    to_write = {}

    for k, v in original.items():
        if k == "LANGUAGE":
            v = "{} {}".format(lang_data["NativeName"], lang_data["Flag"])

            to_write[k] = v
        elif k == "LINK_DEV":
            to_write[k] = v
        elif k == "LANG_COMMAND":
            v = v.replace("🇮🇱", lang_data["Flag"])

        if k not in to_write:
            to_write[k] = await translate(v)
        print(f"[{k}] Translated Successfully to [{lang_data['EnglishName']}].")

    with open(f"./{lang_code}.json", "w+", encoding="utf-8") as f:
        f.write(json.dumps(to_write, indent=4, ensure_ascii=False))

    print(f"Generated successfully to [./{lang_code}.json]")

    with open("../tg/utils.py", "r") as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.strip().startswith("list_langs = ["):
            # Extract the existing list
            start = line.index("[")
            end = line.index("]")
            existing_list = line[start + 1 : end].strip()

            # Split the elements and add the new language if not present
            langs = [lang.strip().strip('"') for lang in existing_list.split(",")]
            langs.append(lang_code)

            # Rebuild the line
            updated_list = ", ".join(f'"{lang}"' for lang in langs)
            lines[i] = f"list_langs = [{updated_list}]\n"
            break

    # Write the updated content back to the file
    with open("../tg/utils.py", "w") as file:
        file.writelines(lines)

    print(f"Added '{lang_code}' to the list and updated tg/utils.py.")
    os.system("ruff format")


asyncio.run(main())
