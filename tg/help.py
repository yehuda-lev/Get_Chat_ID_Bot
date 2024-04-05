from pyrogram import types, Client, errors

from data import cashe_memory
from db import repository
from tg import strings

cache = cashe_memory.cache_memory

list_of_help: list[list[str]] = [
    ['Request_chat', 'Forward', 'Story'],
    ['Search_username', 'Reply_to_another_chat', 'Contact'],
    ['Me', 'Request_admin', 'Language'],
]


@cache.cachable(cache_name="get_keyboard", params=('keyboard_from', 'tg_id'))
def get_keyboard(*, keyboard_from: str | list, tg_id: int) -> list[list[types.InlineKeyboardButton]]:
    """
    Get keyboard for help
    :param keyboard_from: str
    :param tg_id: int
    :return: list[list[types.InlineKeyboardButton]]
    """
    lang = repository.get_lang_by_user(tg_id=tg_id)
    list_of_keyboard = []

    for lst in list_of_help:
        x = []

        for item in lst:
            x.append(
                types.InlineKeyboardButton(
                    text=strings.get_text(key=item.upper(), lang=lang),
                    callback_data=f'help:info:{keyboard_from}:{list_of_help.index(lst)}:{lst.index(item)}')
            )
        list_of_keyboard.append(x)

    return list_of_keyboard


def get_item_from_callback_data(index_lst: int, index_item: int) -> str:
    """
    Get item from list list_of_help
    :param index_lst: int
    :param index_item: int
    :return: str
    """
    return list_of_help[index_lst][index_item]


def get_next_callback_data(data_index_lst: int, data_index_item: int) -> str:
    """
    Get next item in list list_of_help
    :param data_index_lst: int
    :param data_index_item: int
    :return: str
    """
    try:
        index_item, index_lst = data_index_item, data_index_lst
        if data_index_item + 1 >= len(list_of_help[data_index_lst]):
            index_item = 0
            if data_index_lst + 1 >= len(list_of_help):
                index_lst = 0
            else:
                index_lst += 1
        else:
            index_item += 1
    except IndexError:
        index_lst, index_item = 0, 0

    return f'help:next:{data_index_lst}-{data_index_item}:{index_lst}:{index_item}'


def get_back_callback_data(data_index_lst: int, data_index_item: int) -> str:
    """
    Get back item in list list_of_help
    :param data_index_lst: int
    :param data_index_item: int
    :return: str
    """
    try:
        index_item, index_lst = data_index_item, data_index_lst
        if data_index_item - 1 < 0:
            if data_index_lst - 1 < 0:
                index_lst = len(list_of_help) - 1
                index_item = len(list_of_help[index_lst]) - 1
            else:
                index_lst -= 1
                index_item = len(list_of_help[index_lst]) - 1
        else:
            # check if is in the list
            if data_index_lst >= len(list_of_help):
                index_lst = len(list_of_help) - 1
                index_item = len(list_of_help[index_lst]) - 1
            else:
                index_item -= 1
    except IndexError:
        index_lst, index_item = 0, 0

    return f'help:back:{data_index_lst}-{data_index_item}:{index_lst}:{index_item}'


def get_keyboard_menu(keyboard_from: str | list, tg_id: int) -> types.InlineKeyboardMarkup:
    lang = repository.get_lang_by_user(tg_id=tg_id)
    return types.InlineKeyboardMarkup(
        [
            [
                types.InlineKeyboardButton(
                    text=strings.get_text(key="SHOW_ALL", lang=lang),
                    callback_data=f'help:next:{keyboard_from}:0:0')
            ],
            *get_keyboard(keyboard_from=keyboard_from, tg_id=tg_id),
            [
                types.InlineKeyboardButton(
                    text=strings.get_text(key="ABOUT", lang=lang),
                    callback_data=f'help:info:{keyboard_from}:about')
            ]
        ]
    )


# handle callback data
async def handle_callback_data_help(_: Client, cbd: types.CallbackQuery | types.Message):
    tg_id = cbd.from_user.id
    lang = repository.get_lang_by_user(tg_id=tg_id)

    if isinstance(cbd, types.Message):
        await cbd.reply(
            text=strings.get_text(key="INFO_MENU", lang=lang),
            reply_markup=get_keyboard_menu(keyboard_from="menu", tg_id=tg_id)
        )

    else:
        try:
            data = cbd.data.split(':')

            if data[2].replace("-", ":").split(":")[0] == str(data[3:]):
                return

            if len(data) < 5:
                keyboad_from = data[3]
            else:
                keyboad_from = [data[3], data[4]]

            # callback next and back:
            if data[1] == "next" or data[1] == "back":
                index_lst, index_item = int(data[-2]), int(data[-1])

                await cbd.edit_message_text(
                    text=strings.get_text(key=f"INFO_{get_item_from_callback_data(index_lst, index_item).upper()}", lang=lang),
                    reply_markup=types.InlineKeyboardMarkup(
                        [
                            [
                                types.InlineKeyboardButton(
                                    text=strings.get_text(key="BACK", lang=lang),
                                    callback_data=get_back_callback_data(index_lst, index_item)
                                ),
                                types.InlineKeyboardButton(
                                    text=strings.get_text(key="NEXT", lang=lang),
                                    callback_data=get_next_callback_data(index_lst, index_item)
                                ),
                            ],
                            # back to menu:
                            [
                                types.InlineKeyboardButton(
                                    text=strings.get_text(key="MENU", lang=lang),
                                    callback_data=f"help:menu:{keyboad_from}:menu"
                                )
                            ],

                            [
                                types.InlineKeyboardButton(
                                    text=strings.get_text(key="ABOUT", lang=lang),
                                    callback_data=f'help:info:{keyboad_from}:about')
                            ]
                        ]
                    )
                )

            elif data[1] == "menu":
                await cbd.edit_message_text(
                    text=strings.get_text(key="INFO_MENU", lang=lang),
                    reply_markup=get_keyboard_menu(keyboad_from, tg_id)
                )

            elif data[1] == "info":
                if data[3] == "about":
                    await cbd.edit_message_text(
                        text=strings.get_text(key="INFO_ABOUT", lang=lang),
                        link_preview_options=types.LinkPreviewOptions(is_disabled=True),
                        reply_markup=types.InlineKeyboardMarkup(
                            [
                                [
                                    types.InlineKeyboardButton(
                                        text=strings.get_text(key="BUTTON_DEV", lang=lang),
                                        url=strings.get_text(key="LINK_DEV", lang=lang)
                                    )
                                ],
                                [
                                    types.InlineKeyboardButton(
                                        text=strings.get_text(key="MENU", lang=lang),
                                        callback_data=f"help:menu:{keyboad_from}:menu"
                                    )
                                ]
                            ]
                        )
                    )

                # get item
                else:
                    index_lst, index_item = int(data[-2]), int(data[-1])
                    await cbd.edit_message_text(
                        text=strings.get_text(
                            key=f"INFO_{get_item_from_callback_data(index_lst, index_item).upper()}", lang=lang),
                        reply_markup=get_keyboard_menu(keyboard_from=str(keyboad_from), tg_id=tg_id),
                    )
        except errors.MessageNotModified:
            pass
