<p align="center">
  <img src="https://telegra.ph/file/014d967eab622032e2b46.jpg" width="100" height="100">
</p>

# Get_Chat_ID_Bot

## Description

A bot to receive the ID of every Telegram chat.

_Check out our bot [here](https://t.me/GetChatID_IL_BOT)._


## Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/yehuda-lev/Get_Chat_ID_Bot.git
    ```

2. Set up the environment variables:

    1. **Copy the `.env.example` file:**

        ```bash
        cp .env.example .env
        ```

    2. **Edit the `.env` file:**
        - Open the `.env` file in a text editor of your choice.
        - Replace the placeholder values with your actual credentials. You can obtain these credentials from the following sources:

        - **Telegram Credentials:**
            - `TELEGRAM_API_ID` and `TELEGRAM_API_HASH`: Obtain from [my.telegram.org](https://my.telegram.org).
            - `TELEGRAM_BOT_TOKEN`: Create a new bot on [BotFather](https://t.me/BotFather).
            - `TG_GROUP_TOPIC_ID`: ID of the Telegram group where the bot will operate.
            - `ADMINS`: A comma-separated list of Telegram user IDs that will be granted admin privileges.
            - `LIMIT_SPAM`: The number of messages that can be sent in a minute.

    3. **Save the `.env` file:**
        - After editing, save the changes to the `.env` file.

By completing these steps, your environment variables will be properly configured for the project.

## Installation

Clone the repository to your local machine. Then, build the Docker image using the following command:

> If you want to rebuild the image, you can use the `--build` flag to force a rebuild:
> If you want to run the bot in the background, you can use the `-d` flag:

```bash
docker compose up
```

## Contributing

We welcome contributions to this project! Here are some ways you can contribute:

### Generating New Languages

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

### Other Contributions

- **Bug Reports & Feature Requests**: If you encounter any bugs or have feature requests, please open an issue on GitHub.
- **Code Contributions**: Feel free to fork the repository and submit pull requests. Make sure to follow the project's coding guidelines and include tests for any new features or bug fixes.


## Credits

This project was created by [@yehudalev](https://t.me/yehudalev).

---