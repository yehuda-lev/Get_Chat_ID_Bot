import os
import json
from enum import Enum

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
    ID_USERS = "ID_USERS"
    ID_CHANNEL_OR_GROUP = "ID_CHANNEL_OR_GROUP"
    ID_CHANNELS_OR_GROUPS = "ID_CHANNELS_OR_GROUPS"
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
    LANG_COMMAND = "LANG_COMMAND"
    HELP_COMMAND = "HELP_COMMAND"
    ME_COMMAND = "ME_COMMAND"
    ADD_COMMAND = "ADD_COMMAND"
    ADMIN_COMMAND = "ADMIN_COMMAND"
    ABOUT_COMMAND = "ABOUT_COMMAND"
    LINK_COMMAND = "LINK_COMMAND"
    SEARCH_COMMAND = "SEARCH_COMMAND"
    DONATE_COMMAND = "DONATE_COMMAND"


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

    def get_translation(self, key: TranslationKeys | str, lang: str) -> str:
        """
        Get a translation for a specific key and language.
        If the key is not found in the specified language, fallback to English.

        :param key: The translation key.
        :param lang: The language code.
        :return: The translated string
        """
        key = key.value if isinstance(key, TranslationKeys) else key
        # Check if the key exists in this language, otherwise fallback to English
        if lang in self._translations and key in self._translations[lang]:
            return self._translations[lang][key]
        elif key in self._translations["en"]:
            return self._translations["en"][key]
        else:
            return "Something went wrong."

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


manager = TranslationManager(LOCALES_DIR)
