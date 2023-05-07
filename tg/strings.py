
import db.filters

default_lang = None

TEXT = {
    'WELCOME': {
        'en': 'Welcome {name}. \n\n{start2} \n\n{start3} \n\n{start4}',
        'he': 'ברוך הבא {name}. \n\n{start2} \n\n{start3} \n\n{start4}',
    },
    'INFO1': {
        'en': 'In this bot you can get the id of any group, channel, user or bot',
        'he': 'בבוט זה תוכלו לקבל id של כל קבוצה, ערוץ, משתמש או בוט'
    },
    'INFO2': {
        'en': 'To use the bot, please click on the buttons below and share the chat whose ID you want to know.'
              ' - In response, the bot will return the ID of the chat you shared',
        'he': 'בשביל להשתמש בבוט אנא לחצו על הכפתורים למטה ושתפו את הצאט שברצונכם לדעת מה ה ID שלו.'
              ' - בתגובה הבוט יחזיר לכם את ה ID של הצאט אותו שיתפתם'
    },
    'INFO3': {
        'en': 'You can also send a message to the bot (with credit) '
              'and the bot will return the ID of the chat from which the message was sent.',
        'he': 'ניתן גם להעביר הודעה לבוט (עם קרדיט)'
              ' והבוט יחזיר לכם את ה ID של הצאט ממנו ההודעה הועברה.'
    },
    'USER': {
        'en': 'User',
        'he': 'משתמש'
    },
    'CHANNEL': {
        'en': 'Channel',
        'he': 'ערוץ'
    },
    'GROUP': {
        'en': 'Group',
        'he': 'קבוצה'
    },
    'ID_USER': {
        'en': 'The ID is: {}',
        'he': 'ה ID הוא: {}'
    },
    'ID_CHANNEL_OR_GROUP': {
        'en': 'The ID is: {}',
        'he': 'ה ID הוא: \u200e{}'
    },
    'ID_HIDDEN': {
        'en': 'The ID is hidden. \n{name}',
        'he': 'ה ID מוסתר \n{name}'
    },
    'GROUP11': {
        'en': 'Group',
        'he': 'קבוצה'
    },
    'GROUP3123': {
        'en': 'Group',
        'he': 'קבוצה'
    }
}


def get_text(text: str, tg_id: int) -> str:
    if default_lang is not None:
        lang = default_lang
    else:
        lang = db.filters.get_lang_by_user(tg_id=tg_id)

    try:
        return TEXT[text][lang]
    except KeyError:
        return 'Error'
