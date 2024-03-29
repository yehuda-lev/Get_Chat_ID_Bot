from db import repository

default_lang = None

TEXT = {
    "WELCOME": {
        "en": "Welcome {name} 🤠\n\n"
              "🪪 In this bot you can get the id of any group, channel, user or bot\n\n"
              "📤 To use the bot, click on the buttons below and share the chat whose ID you want to know."
              " - In response, the bot will return the ID of the chat you shared\n\n"
              "🇺🇸 To change the language please send the /lang command\n\n"
              "📝 For the list of available commands send the command /help\n\n"
              "📢 For updates on the bot subscribe to @GetChatID_Updates",
        "he": "ברוך הבא {name} 🤠\n\n"
              "\u200f🪪 בבוט זה תוכל לקבל מזהה של כל קבוצה, ערוץ, משתמש או בוט\n\n"
              "📤 בשביל להשתמש בבוט לחץ על הכפתורים למטה ושתף את הצאט שברצונך לדעת מה המזהה שלו. "
              "- בתגובה הבוט יחזיר לך את המזהה של הצאט אותו שיתפת\n\n"
              "\u200f🇺🇸 לשינוי השפה אנא שלחו את הפקודה /lang\n\n"
              "📝 לרשימת הפקודות הזמינות שלחו את הפקודה /help\n\n"
              "📢 לעדכונים על הבוט הירשמו ל-@GetChatID_Updates",
    },
    "USER": {"en": "👤 User", "he": "👤 משתמש"},
    "BOT": {"en": "🤖 Bot", "he": "🤖 בוט"},
    "CHANNEL": {"en": "📢 Channel", "he": "📢 ערוץ"},
    "GROUP": {"en": "👥 Group", "he": "👥 קבוצה"},
    "ID_USER": {"en": "🪪 The ID is: {}", "he": "‏🪪 ה ID הוא: {}"},
    "ID_CHANNEL_OR_GROUP": {"en": "🪪 The ID is: {}", "he": "‏🪪 ה ID הוא: \u200e{}"},
    "ID_HIDDEN": {"en": "🪪 The ID is hidden. \n{name}", "he": "‏🪪 ה ID מוסתר \n{name}"},
    "CHOICE_LANG": {"en": "🤳 Select your language.", "he": "🤳 בחר את השפה שלך."},
    "DONE": {"en": "The selected language is {}", "he": "השפה שנבחרה היא {}"},
    "NOT_HAVE_ID": {
        "en": "❌ The contact you sent has no ID",
        "he": "❌ לאיש הקשר ששלחת אין ID",
    },
    "CAN_NOT_GET_THE_ID": {
        "en": "❌ It is not possible to get the ID of this chat",
        "he": "❌ אי אפשר לקבל את הID של הצאט הזה",
    },
    "CHAT_MANAGER": {
        "en": "👮 By clicking the buttons below you can see all the groups and channels you manage and get their ID",
        "he": "👮 בלחיצה על הכפתורים למטה תוכל לראות את כל הקבוצות והערוצים שאתה מנהל בהם ולקבל את המזהה שלהם",
    },
    'REQUEST_CHAT': {
        'en': '📤 request chat',
        'he': "📤 שיתוף צ'אט"
    },
    'INFO_REQUEST_CHAT': {
        'en': '**📤 request chat**\n\n'
              'Click on the buttons below and share the chat whose ID you want to know.'
              '\n- In response, the bot will return the ID of the chat you shared',
        'he': "**📤 שיתוף צ'אט**\n\n"
              "לחץ על הכפתורים למטה ושתף את הצ'אט שברצונך לדעת מה המזהה שלו."
              "\n- בתגובה הבוט יחזיר לך את המזהה של הצ'אט אותו שיתפת"
    },
    'FORWARD': {
        'en': '⏩ forward',
        'he': '⏩ העברה'
    },
    'INFO_FORWARD': {
        'en': '**⏩ forward message**\n\n'
              'Forward any message to the bot (forward with quotes) '
              'and the bot will return the ID of the chat from which the message was sent.',
        'he': '**⏩ העברת הודעה**\n\n'
              "העבירו כל הודעה לבוט (עם קרדיט) והבוט יחזיר לכם את המזהה של הצ'אט ממנו ההודעה הועברה"
    },
    'STORY': {
        'en': '📝 story',
        'he': '📝 סטורי'
    },
    'INFO_STORY': {
        'en': '**📝 Story**\n\n'
              'Transfer a story and get their ID.',
        'he': "**📝 סטורי**\n\n"
              "העבירו סטורי לבוט וקבלו את המזהה של הצא'ט",
    },
    'SEARCH_USERNAME': {
        'en': '🔍 username',
        'he': '🔍 שם משתמש'
    },
    'INFO_SEARCH_USERNAME': {
        'en': '**🔍 Search by Username**\n\n'
              'Send the username to the bot and the bot will return the ID of the chat with that username.',
        'he': "**🔍 חיפוש באמצעות שם משתמש**\n\n"
              "שלח שם משתמש לבוט והבוט יחזיר לך את המזהה של הצ'אט הזה",
    },
    'REPLY_TO_ANOTHER_CHAT': {
        'en': '↩️ reply to',
        'he': "↩️ הגב ל"
    },
    'INFO_REPLY_TO_ANOTHER_CHAT': {
        'en': '**↩️ Reply to Another Chat**\n\n'
              'Reply to any message in another chat, '
              'and the bot will return the ID of the chat from which the message was replied.',
        'he': "**↩️ הגב לצ'אט אחר**\n\n"
              "הגב לכל הודעה מצ'אט אחר, "
              "והבוט יחזיר לך את המזהה של הצ'אט ממנו נשלחה ההודעה.",
    },
    'CONTACT': {
        'en': '🪪 contact',
        'he': '\u200f🪪 איש קשר'
    },
    'INFO_CONTACT': {
        'en': "**🪪 Contact**\n\n"
              "Share a contact to the bot and the bot will return the contact's ID to you",
        'he': "**\u200f🪪 איש קשר**\n\n"""
              "שתף איש קשר לבוט והבוט יחזיר לך את המזהה של האיש קשר",
    },
    'REQUEST_ADMIN': {
        'en': '👮‍♂️ admin',
        'he': '👮‍♂️ ניהולים'
    },
    'INFO_REQUEST_ADMIN': {
        'en': '**👮‍ Request Admin**\n\n'
              'Send the command /admin to get all the chats you have name management.',
        'he': "**👮 צאט'ים בניהולך**\n\n"
              'שלחו את הפקודה /admin לקבלת כל הצאטים שיש לכם ניהול שם',
    },
    'ME': {
        'en': '👤 me',
        'he': '👤 אני'
    },
    'INFO_ME': {
        'en': "**👤 Get your ID**\n\n"
              "Send the command /me to get your ID",
        'he': "**👤 קבל את המזהה שלך**\n\n"
              "שלח את הפקודה /me בכדי לקבל את המזהה שלך"
    },
    'LANGUAGE': {
        'en': '🇺🇸 language',
        'he': '\u200f🇺🇸 שפה'
    },
    'INFO_LANGUAGE': {
        'en': '**🇺🇸 Language**\n\n'
              'To change the language send the /lang command.',
        'he': "**\u200f🇺🇸 שפה**\n\n"
              "לשינוי השפה שלחו את הפקודה /lang",
    },
    'SHOW_ALL': {
        'en': '📕 show all',
        'he': '📕 הצג הכל'
    },
    'NEXT': {
        'en': 'next ➡️',
        'he': '➡️ הבא'
    },
    'BACK': {
        'en': '⬅️ back',
        'he': 'חזור ⬅️'
    },
    'MENU': {
        'en': '🏘 menu',
        'he': '🏘 תפריט ראשי'
    },
    'INFO_MENU': {
        'en': '🏘 menu help',
        'he': '🏘 תפריט עזרה'
    },
    'ABOUT': {
        'en': 'ℹ️ about',
        'he': 'ℹ️ אודות'
    },
    'INFO_ABOUT': {
        'en':
            "ℹ️ **Details about the bot**\n\n"
            "Language: Python \n"
            "Library: Pyrogram \n"
            "Bot creator: @yehudalev 👨‍💻\n\n"
            "The bot is open source on GitHub 🖤\n"
            "https://github.com/yehuda-lev/Get_Chat_ID_Bot\n\n"
            "📢 For updates on the bot, subscribe to @GetChatID_Updates,",
        'he':
            "\u200fℹ️ **פרטים על הבוט**\n\n"
            "שפה: Python \n"
            "ספרייה: Pyrogram \n"
            "יוצר הבוט: @yehudalev  👨‍💻\n\n"
            "הבוט בקוד פתוח בגיטהאב 🖤\n"
            "https://github.com/yehuda-lev/Get_Chat_ID_Bot\n\n"
            "📢 לעדכונים על הבוט הירשמו ל-@GetChatID_Updates",
    },
    "BUTTON_DEV": {
        "en": "Send message👨‍💻",
        "he": "לשליחת הודעה למתכנת 👨‍💻"
    },
    "LINK_DEV": {
        "en": "https://t.me/yehudalev",
        "he": "https://t.me/yehudalev"
    },
}


def get_text(text: str, tg_id: int) -> str:
    if default_lang is not None:
        lang = default_lang
    else:
        lang = repository.get_lang_by_user(tg_id=tg_id)

    try:
        return TEXT[text][lang]
    except KeyError:
        return "Error"
