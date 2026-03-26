import os
import json
from enum import Enum

from pyrogram import types

LOCALES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locales")


class TranslationKeys(Enum):
    """
    Enum containing all translation keys.
    """

    WELCOME = "WELCOME"
    USER = "USER"
    BOT = "BOT"
    CHANNEL = "CHANNEL"
    GROUP = "GROUP"
    ID_USER = "ID_USER"
    ID_CHANNEL_OR_GROUP = "ID_CHANNEL_OR_GROUP"
    ID_HIDDEN = "ID_HIDDEN"
    CHOICE_LANG = "CHOICE_LANG"
    DONE = "DONE"
    NOT_HAVE_ID = "NOT_HAVE_ID"
    CAN_NOT_GET_THE_ID = "CAN_NOT_GET_THE_ID"
    CHAT_MANAGER = "CHAT_MANAGER"
    REQUEST_CHAT = "REQUEST_CHAT"
    INFO_REQUEST_CHAT = "INFO_REQUEST_CHAT"
    FORWARD = "FORWARD"
    INFO_FORWARD = "INFO_FORWARD"
    STORY = "STORY"
    INFO_STORY = "INFO_STORY"
    ASK_INLINE_QUERY = "ASK_INLINE_QUERY"
    SEARCH_USERNAME = "SEARCH_USERNAME"
    INFO_SEARCH_USERNAME = "INFO_SEARCH_USERNAME"
    REPLY_TO_ANOTHER_CHAT = "REPLY_TO_ANOTHER_CHAT"
    INFO_REPLY_TO_ANOTHER_CHAT = "INFO_REPLY_TO_ANOTHER_CHAT"
    CONTACT = "CONTACT"
    INFO_CONTACT = "INFO_CONTACT"
    REQUEST_ADMIN = "REQUEST_ADMIN"
    INFO_REQUEST_ADMIN = "INFO_REQUEST_ADMIN"
    ME = "ME"
    INFO_ME = "INFO_ME"
    LANGUAGE = "LANGUAGE"
    INFO_LANGUAGE = "INFO_LANGUAGE"
    INFO_GROUP = "INFO_GROUP"
    SHOW_ALL = "SHOW_ALL"
    NEXT = "NEXT"
    BACK = "BACK"
    MENU = "MENU"
    INFO_MENU = "INFO_MENU"
    ABOUT = "ABOUT"
    INFO_ABOUT = "INFO_ABOUT"
    BUTTON_DEV = "BUTTON_DEV"
    LINK_DEV = "LINK_DEV"
    CHOSE_CHAT_TYPE = "CHOSE_CHAT_TYPE"
    BUTTON_ADD_BOT_TO_GROUP = "BUTTON_ADD_BOT_TO_GROUP"
    ADD_BOT_TO_GROUP = "ADD_BOT_TO_GROUP"
    BOT_ADDED_TO_GROUP = "BOT_ADDED_TO_GROUP"
    BUSINESS = "BUSINESS"
    INFO_BUSINESS = "INFO_BUSINESS"
    BUSINESS_CONNECTION = "BUSINESS_CONNECTION"
    BUSINESS_CONNECTION_DISABLED = "BUSINESS_CONNECTION_DISABLED"
    BUSINESS_CONNECTION_REMOVED = "BUSINESS_CONNECTION_REMOVED"
    ID_BY_MANAGE_BUSINESS = "ID_BY_MANAGE_BUSINESS"
    ASK_AMOUNT_TO_PAY = "ASK_AMOUNT_TO_PAY"
    SUPPORT_ME = "SUPPORT_ME"
    TEXT_SUPPORT_ME = "TEXT_SUPPORT_ME"
    PAYMENT_SUCCESS = "PAYMENT_SUCCESS"
    SOMTHING_WENT_WRONG = "SOMTHING_WENT_WRONG"
    LINK_TO_CHAT = "LINK_TO_CHAT"
    BUTTON_GET_LINK = "BUTTON_GET_LINK"
    FORMAT_LINK = "FORMAT_LINK"

    BOT_NAME = "BOT_NAME"
    BOT_DESCRIPTION = "BOT_DESCRIPTION"
    BOT_ABOUT = "BOT_ABOUT"

    START_COMMAND = "START_COMMAND"
    SETTINGS_COMMAND = "SETTINGS_COMMAND"
    LANG_COMMAND = "LANG_COMMAND"  # needed?
    HELP_COMMAND = "HELP_COMMAND"
    ME_COMMAND = "ME_COMMAND"
    ADD_COMMAND = "ADD_COMMAND"
    ADMIN_COMMAND = "ADMIN_COMMAND"
    ABOUT_COMMAND = "ABOUT_COMMAND"
    LINK_COMMAND = "LINK_COMMAND"
    SEARCH_COMMAND = "SEARCH_COMMAND"
    DONATE_COMMAND = "DONATE_COMMAND"

    SETTINGS = "SETTINGS"
    FEATURE_SETTINGS = "FEATURE_SETTINGS"
    ALERT_CHANGE_SETTINGS = "ALERT_CHANGE_SETTINGS"
    COPY_BUTTON = "COPY_BUTTON"
    MULTIPLE_CHATS = "MULTIPLE_CHATS"
    DISABLE_ALL_FEATURES = "DISABLE_ALL_FEATURES"
    ENABLE_ALL_FEATURES = "ENABLE_ALL_FEATURES"
    SAVE_CHANGES = "SAVE_CHANGES"
    SETTINGS_SAVED = "SETTINGS_SAVED"


class TranslationManager:
    """
    Manages translations for different languages.
    """

    def __init__(self, locales_dir):
        self._locales_dir = locales_dir
        self._translations = self._load_all_languages()

    def _load_language(self, lang_code) -> dict[str, str]:
        """Loads translations from a specific language file."""

        file_path = os.path.join(self._locales_dir, f"{lang_code}.json")
        if not os.path.exists(file_path):
            return {}
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def _load_all_languages(self) -> dict[str, dict[str, str]]:
        """Loads translations for all available languages."""
        translations = {}
        for file_name in os.listdir(self._locales_dir):
            if file_name.endswith(".json"):
                lang_code = file_name.split(".")[0]
                translations[lang_code] = self._load_language(lang_code)
        return translations

    def get_translation(
        self, key: TranslationKeys | str, lang: str, is_button: bool = False
    ) -> str | tuple[str, int | None]:
        """
        Get a translation for a specific key and language.
        If the key is not found in the specified language, fallback to English.

        :param key: The translation key.
        :param lang: The language code.
        :param is_button: Whether the translation is for a button (to handle emojis differently).
        :return: The translated string
        """
        key = key.value if isinstance(key, TranslationKeys) else key
        # Check if the key exists in this language, otherwise fallback to English
        if lang in self._translations and key in self._translations[lang]:
            text, emoji_id = replace_emojis_with_premium_emojis(
                self._translations[lang][key], is_button=is_button
            )
        elif key in self._translations["en"]:
            text, emoji_id = replace_emojis_with_premium_emojis(
                self._translations["en"][key], is_button=is_button
            )
        else:
            text, emoji_id = replace_emojis_with_premium_emojis(
                key, is_button=is_button
            )  # Fallback to the key itself if not found

        if is_button:
            return text, emoji_id
        return text

    def _validate_language(self, lang_code: str) -> list[str]:
        """
        Validates if a specific language contains all keys defined in TranslationKeys.
        """
        missing_keys = []
        lang_translations = self._translations.get(lang_code, {})
        for key in TranslationKeys:
            if key.value not in lang_translations:
                missing_keys.append(key.value)
        return missing_keys


def get_button_with_emoji(
    key: TranslationKeys | str,
    lang: str | None = None,
    callback_data: str | None = None,
    url: str | None = None,
    request_users: types.KeyboardButtonRequestUsers | None = None,
    request_chat: types.KeyboardButtonRequestChat | None = None,
) -> types.InlineKeyboardButton | types.KeyboardButton:
    """
    Get a button with emoji by translation key and language.
    """
    text, emoji_id = manager.get_translation(key, lang, is_button=True)

    if callback_data:
        return types.InlineKeyboardButton(
            text=text,
            icon_custom_emoji_id=emoji_id,
            callback_data=callback_data,
        )
    elif url:
        return types.InlineKeyboardButton(
            text=text,
            icon_custom_emoji_id=emoji_id,
            url=url,
        )
    elif request_users:
        return types.KeyboardButton(
            text=text,
            icon_custom_emoji_id=emoji_id,
            request_users=request_users,
        )
    elif request_chat:
        return types.KeyboardButton(
            text=text,
            icon_custom_emoji_id=emoji_id,
            request_chat=request_chat,
        )

    raise ValueError(
        "At least one of callback_data, url, request_users or request_chat must be provided."
    )


emojis = {
    "🌟": 4963511421280192936,
    "🤠": 5373308531757817004,
    "🪪": 5422683699130933153,
    "🚀": 5445284980978621387,
    "1️⃣": 6035214020577859654,
    "2️⃣": 6032932813123098123,
    "💡": 5472146462362048818,
    "🌐": 5776233299424843260,
    "🤳": 5879585266426973039,
    "🇺🇸": 5202021044105257611,
    "🇮🇱": 5332299462461107995,
    "🇸🇦": 5202079966761590204,
    "🇷🇺": 5449408995691341691,
    "🇨🇳": 5431782733376399004,
    "🇮🇳": 5447419223242449630,
    "🇪🇸": 5201957744877248121,
    "🇦🇿": 5224254431939275524,
    "🇫🇷": 5202132623060640759,
    "💖": 5465540480538254161,
    "📢": 5771695636411847302,
    #
    "🔗": 5877465816030515018,
    "📱": 5819078828017849357,
    "🍏": 5818920837645867167,
    #
    "👤": 5879770735999717115,
    "🤖": 5931415565955503486,
    "👥": 5942877472163892475,
    #
    "📤": 5877396173135811032,
    "⏩": 5832251986635920010,
    "📚": 5877437284417698827,
    "ℹ️": 5879785854284599288,
    "🆘": 5879785854284599288,
    "📝": 5764747792371160364,
    "🔍": 5771887475421090729,
    "↩️": 5888484185261216745,
    "📕": 5883997877172179131,
    "🏠": 6023896773162967617,
    "🏘": 5873121512445187130,
    "➡️": 5807453545548487345,
    "⬅️": 5805509901048356965,
    "👮‍♂️": 5778423822940114949,
    #
    "🖤": 6318902906900711458,
    "👨‍💻": 5217797330861826981,
}

emoji_template = "![{emoji}](tg://emoji?id={emoji_id})"


def replace_emojis_with_premium_emojis(
    text: str, is_button: bool = False
) -> tuple[str, int | None]:
    """
    Replace emojis in the text with their corresponding premium emoji format.
    """

    icon_emoji_id = None
    for emoji, emoji_id in emojis.items():
        if emoji in text:
            if is_button:
                icon_emoji_id = emoji_id
                text = text.replace(emoji, "").strip()
                break
            else:
                # check if is format ![emoji](tg://emoji?id=emoji_id) and if so, don't replace it
                if f"![{emoji}](tg://emoji?id=" in text:
                    continue
                text = text.replace(
                    emoji, emoji_template.format(emoji=emoji, emoji_id=emoji_id)
                )

    return text.strip(), icon_emoji_id


manager = TranslationManager(LOCALES_DIR)
