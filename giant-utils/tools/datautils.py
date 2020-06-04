"""Utilities for reading, writing and editing data."""
import json
import sqlite3
import typing


client = None    # should be set externally


def discorddata(fun: typing.Callable) -> typing.Callable:
    """Wrap a function to pass it the discord client."""
    def wrapper(*args: typing.Tuple, **kwargs: typing.Dict) -> typing.Any:
        return fun(client, *args, **kwargs)

    return wrapper


def asyncdiscord(fun: typing.Callable) -> typing.Callable:
    """Asynchronously wrap a function to pass it the discord client."""
    async def wrapper(*args: typing.Tuple,
                      **kwargs: typing.Dict) -> typing.Any:
        return await fun(client, *args, **kwargs)

    return wrapper


def jsondata(filepath: str) -> typing.Callable:
    """Return a wrapper for editing JSON files.

    Example usuage:
    ```python
    @jsondata('data.json')
    def addvalue(data, name, value=10):
        data[name] = value

    addvalue('score', 8)
    addvalue('maxscore')
    ```
    """
    def decorator(fun: typing.Callable) -> typing.Callable:
        def wrapper(*args: typing.Tuple, **kwargs: typing.Dict) -> typing.Any:
            try:
                with open(filepath) as file:
                    data = json.load(file)
            except FileNotFoundError:
                data = {}
            result = fun(data, *args, **kwargs)
            with open(filepath, 'w') as file:
                json.dump(data, file)
            return result

        return wrapper

    return decorator


DBS = {}


def _get_db(filepath: str) -> sqlite3.Connection:
    """Connect to a database (with caching)."""
    if filepath in DBS:
        return DBS[filepath]
    DBS[filepath] = sqlite3.connect(filepath)
    return DBS[filepath]


def sqldata(filepath: str = 'data/db.sqlite3') -> typing.Callable:
    """Like jsondata but for SQL.

    Passes wrapped function a function which accepts a parameterised
    query and optional parameters, returning any rows returned by the query.
    """
    def decorator(fun: typing.Callable) -> typing.Callable:
        def wrapper(*args: typing.Tuple, **kwargs: typing.Dict) -> typing.Any:
            db = _get_db(filepath)
            cur = db.cursor()

            def execute(query: str, *params: typing.Tuple
                        ) -> typing.List[typing.List[typing.Any]]:
                cur.execute(query, params)
                return cur.fetchall()

            result = fun(execute, *args, **kwargs)
            db.commit()
            return result

        return wrapper

    return decorator
