"""Custom caching function, like functools.lru_cache."""
import typing


DONT_CACHE = object()
BYPASS_CACHE = object()


def _make_key(args, kwargs) -> typing.Tuple[typing.Any]:
    """Make a unique key for some args and kwargs."""
    key = args + ('__xyz.artemis.cache.sep',)
    for kw_name in kwargs:
        key += (kw_name, kwargs[kw_name])
    return key


def cache(fun: typing.Callable):
    """The caching wrapper."""
    fun_cache = {}

    def wrapper(*args, **kwargs):
        key = _make_key(args, kwargs)
        if args and args[0] == BYPASS_CACHE:
            args = args[1:]
        else:
            if key in fun_cache:
                return fun_cache[key]
        output = fun(*args, **kwargs)
        if isinstance(output, tuple) and output[-1] == DONT_CACHE:
            return output[0]
        else:
            fun_cache[key] = output
            return output

    return wrapper
