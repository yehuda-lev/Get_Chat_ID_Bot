from pyrogram import types, Client

from data import cashe_memory

cache = cashe_memory.cache_memory

list_of_help: list[list[str]] = [
    ['Request_peer', 'Forward', 'Story'],
    ['Search_username', 'Reply_to_another_chat', 'Contact'],
    ['Request_admin', 'Language'],
]


def get_keyboard(keyboard_from: str) -> list[list[types.InlineKeyboardButton]]:
    """
    Get keyboard for help
    :param keyboard_from: str
    :return: list[list[types.InlineKeyboardButton]]
    """
    list_of_keyboard = []

    for lst in list_of_help:
        x = []
        for item in lst:
            x.append(
                types.InlineKeyboardButton(
                    text=item,  # TODO text need to be a language of user
                    # callback_data=f'help:info:{list_of_help.index(lst)}-{lst.index(item)}:{list_of_help.index(lst)}:{lst.index(item)}')
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


def get_index(index_item: str) -> tuple[int, int]:
    """
    Get index of item in list list_of_help
    :param index_item: str
    :return: tuple[int, int]
    """
    for i in list_of_help:
        if index_item in i:
            return list_of_help.index(i), i.index(index_item)


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


def get_keyboard_menu(keyboard_from: str) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        [
            [
                types.InlineKeyboardButton(
                    text='help',  # TODO text need to be a language of user
                    callback_data=f'help:next:{keyboard_from}:0:0')
            ],
            *get_keyboard(keyboard_from),
            [
                types.InlineKeyboardButton(
                    text='about',  # TODO text need to be a language of user
                    callback_data=f'help:info:{keyboard_from}:about')
            ]
        ]
    )


# handle callback data
def handle_callback_data_help(_: Client, cbd: types.CallbackQuery | types.Message):
    if isinstance(cbd, types.Message):
        cbd.reply(
            text="choose help",
            reply_markup=get_keyboard_menu(keyboard_from="menu")
        )

    else:
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

            cbd.edit_message_text(
                text=get_item_from_callback_data(index_lst, index_item),
                reply_markup=types.InlineKeyboardMarkup(
                    [
                        [
                            types.InlineKeyboardButton(
                                text='back',  # TODO text need to be a language of user
                                callback_data=get_back_callback_data(index_lst, index_item)
                            ),
                            types.InlineKeyboardButton(
                                text='next',  # TODO text need to be a language of user
                                callback_data=get_next_callback_data(index_lst, index_item)
                            ),
                        ],
                        # back to menu:
                        [
                            types.InlineKeyboardButton(
                                text="back to menu",  # TODO text need to be a language of user
                                callback_data=f"help:menu:{keyboad_from}:menu"
                            )
                        ],

                        [
                            types.InlineKeyboardButton(
                                text='about',  # TODO text need to be a language of user
                                callback_data=f'help:info:{keyboad_from}:about')
                        ]
                    ]
                )
            )

        elif data[1] == "menu":
            cbd.edit_message_text(
                text="choose help",
                reply_markup=get_keyboard_menu(keyboad_from)
            )

        elif data[1] == "info":
            if data[3] == "about":
                cbd.edit_message_text(
                    text="text about",
                    reply_markup=types.InlineKeyboardMarkup(
                        [
                            [
                                types.InlineKeyboardButton(
                                    text="back to menu",  # TODO text need to be a language of user
                                    callback_data=f"help:menu:{keyboad_from}:menu"
                                )
                            ]
                        ]
                    )
                )

            # get item
            else:
                index_lst, index_item = int(data[-2]), int(data[-1])
                cbd.edit_message_text(
                    text=get_item_from_callback_data(index_lst, index_item),
                    reply_markup=get_keyboard_menu(keyboad_from),
                )
