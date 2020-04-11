import string
import random


class Model:
    collection = None
    objects = {}

    @classmethod
    def clear_cache(cls):
        cls.objects = {}

    @classmethod
    def all(cls, search=None):
        if not search:
            search = {}
        for user in cls.collection.find(search):
            cls.objects[user['_id']] = cls.load(user['_id'])
        return [*cls.objects.values()]

    @classmethod
    def delete_all(cls, search=None):
        if not search:
            search = {}
        cls.collection.delete_many(search)
        cls.objects = {}

    @classmethod
    def create(cls, data, id=None):
        if id:
            if id in cls.objects:
                raise ValueError('Object already exists with this ID.')
        else:
            while (not id) or (id in cls.objects):
                chars = string.ascii_uppercase + string.digits
                id = ''.join(random.choices(chars, k=5))
        data['_id'] = id
        cls.collection.insert_one(data)
        return cls(id, data)

    @classmethod
    def load(cls, id):
        if id in cls.objects:
            return cls.objects[id]
        data = cls.collection.find_one({'_id': id})
        if data:
            return cls(id, data)

    def __init__(self, id, data):
        self.id = id
        self.data = data
        type(self).objects[id] = self

    def delete(self):
        type(self).collection.delete_one({'_id': self.id})
        del type(self).objects[self.id]

    def __getattr__(self, key):
        if key in ('data',  'id'):
            return super().__getattr__(key)
        return self.data[key]

    def __setattr__(self, key, new):
        if key in ('data', 'id'):
            return super().__setattr__(key, new)
        self.data[key] = new
        type(self).collection.update_one(
            {'_id': self.id}, {'$set': {key: new}}
        )

    def __str__(self):
        ret = f'<{type(self).__name__} id={repr(self.id)}'
        for attr in self.data:
            if not attr.startswith('_'):
                ret += f' {attr}={repr(self.data[attr])}'
        return ret + '>'

    def __repr__(self):
        return str(self)
