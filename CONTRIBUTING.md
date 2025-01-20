# Contributing

We welcome contributions to this project! Here are some ways you can contribute:

## Generating New Languages

If you would like to add support for a new language, follow these steps:

1. **Ensure you have the necessary library installed**:
    Make sure you have Python and the required library installed. You can install it using:

    ```sh
    pip install trengine
    ```

2. **Prepare the language data**:
    If the language you want to add isn't listed in `languages.json`, you need to add it manually. This includes specifying    the `Code`, `NativeName`, `Flag`, and `EnglishName` for the new language.

3. **Run the script**:
    Execute the script using the following command:

    ```sh
    python generate.py {lang_code}
    ```

4. **Check the output**:
    The script will read the `en.json` file, translate the contents, and generate a new language file named `{lang_code}.json` in the same directory. The `{lang_code}` should be replaced with the appropriate language code.

5. **Verify the generated file**:
    Open the generated `{lang_code}.json` file and verify that the translations are correct.

> **Note:**
> The language code must follow the **[ISO 639](https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes)** format.

## Other Contributions

- **Bug Reports & Feature Requests**: If you encounter any bugs or have feature requests, please open an issue on GitHub.
- **Code Contributions**: Feel free to fork the repository and submit pull requests. Make sure to follow the project's coding guidelines and include tests for any new features or bug fixes.

