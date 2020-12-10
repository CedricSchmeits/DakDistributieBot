from aiogram.utils.callback_data import CallbackData
from .multilinekeyboard import MultilineKeyboard

class NameIdKeyboardMeta(type):
    def __new__(cls, name, bases, dct):
        clsInstance = super().__new__(cls, name, bases, dct)
        if hasattr(clsInstance, 'callbackName'):
            clsInstance._callbackData = CallbackData(clsInstance.callbackName, 'id', 'action')
        return clsInstance

class NameIdKeyboard(MultilineKeyboard, metaclass=NameIdKeyboardMeta):
    def __init__(self):
        self.schema = []
        self.actions = []

    def Append(self, text, textId, action):
        if len(self.schema) == 0 or self.schema[-1] == 3:
            self.schema.append(1)
        else:
            self.schema[-1] += 1

        self.actions.append({'text':          text,
                             'callback_data': self.new(str(textId), action)})

    def Generate(self):
        self.schema.append(1)
        self.actions.append({'text': 'Annuleren', 'callback_data': self.new('-', 'cancel')})

        keyboard = self.generate_keyboard(self.actions, self.schema)

        # disable these actions
        self.action = None
        self.schema = None
        return keyboard

    @classmethod
    def new(cls, *args):
        return cls._callbackData.new(*args)

    @classmethod
    def filter(cls, **config):
        return cls._callbackData.filter(**config)
