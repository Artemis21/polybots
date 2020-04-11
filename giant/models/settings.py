from .generic import ModelList
import json


class SettingsType(type):
    def __getattr__(cls, name):
        if name in ('FIELDS', 'data'):
            return super().__getattribute__(name)
        if name in cls.FIELDS:
            if name in cls.data:
                return cls.data[name]
            else:
                obj = cls.FIELDS[name]
                try:
                    obj = obj.copy()
                except AttributeError:
                    pass
                cls.data[name] = obj
                return obj
        raise AttributeError(f'No attribute named {name}.')

    def __setattr__(cls, name, value):
        if name in ('FIELDS', 'data'):
            return super().__setattr__(name, value)
        if name not in cls.FIELDS:
            raise AttributeError(f'{name} is not a defined field.')
        if not isinstance(value, type(cls.FIELDS[name])):
            raise ValueError('Field {} must be of type {}.'.format(
                name, type(cls.FIELDS[name]).__name__
            ))
        cls.data[name] = value
        cls.save()


class Settings(metaclass=SettingsType):
    @classmethod
    def load(cls):
        cls.FIELDS = {
            'admin_users': ModelList(Settings, [496381034628251688]),
            'admin_roles': ModelList(Settings),
            'banned_users': ModelList(Settings),
            'banned_roles': ModelList(Settings),
            'season': 2,
            'leagues': 3,
        }
        try:
            with open('data/settings.json') as f:
                cls.data = json.load(f)
        except FileNotFoundError:
            cls.data = {}

    @classmethod
    def save(cls):
        with open('data/settings.json', 'w') as f:
            json.dump(cls.data, f)

    @classmethod
    def reset(cls):
        cls.data = {}
        cls.save()
