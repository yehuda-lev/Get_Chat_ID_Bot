import logging
import inspect
from functools import wraps
from typing import Any, Optional, Tuple, Dict, Hashable, Iterable, Callable, Union

logger = logging.getLogger(__name__)

"""
https://github.com/david-lev (c) 2023
**Cache management in Python in memory efficiently and quickly.**
True, Python has `lru_cache`, but I didn't really find it effective, and in many cases - I don't really care about
objects being flooded in memory. Apart from that, `lru_cache` lacks such basic features:
1. The ability to decide which parameters will be included in the cache key
2. Do not cache on a result of None
3: the flexibility in choosing the name of the cache
4: the ability to delete a specific item from the cache
5: run the function anyway and still store the cache
(In the future, maybe I'll add more features for `lru_cache` and more)
You will find all these, and more, in the realization before you:
"""


class MemoryCache:
    """
    Memory cache
        - This cache is not persistent, it will be lost when the application is restarted or the server is restarted
    """

    def __init__(self):
        logger.debug("memory cache initialized")
        self._cache = {}

    @staticmethod
    def build_cache_id(*args, **kwargs) -> Tuple[Tuple[Any, ...], ...]:
        """Build cache id"""
        return args, tuple(kwargs.items())

    @staticmethod
    def _get_cache_id(
        params: Optional[Union[Iterable[str], str]], *args, **kwargs
    ) -> Tuple[Tuple[Any, ...], ...]:
        """Get cache id"""
        _kwargs = (
            {
                k: kwargs[k]
                for k in (params if not isinstance(params, str) else (params,))
            }
            if params is not None
            else kwargs
        )
        return MemoryCache.build_cache_id(
            *args if params is not None else (), **_kwargs
        )

    def cachable(
        self,
        cache_name: Optional[Hashable] = None,
        params: Optional[Union[Iterable[str], str]] = None,
        always_execute: bool = False,
    ) -> Callable:
        """
        Cache decorator
        Usage:
            >>> cache = MemoryCache()
            >>> @cache.cachable(cache_name='math-plus', params=('a', 'b'))
            >>> def plus(*, a, b):  # The function must have keyword arguments in order to use the params argument
            >>>     return a + b
            >>> plus(a=1, b=2)  # The result will be cached
            3
            >>> plus(a=1, b=2)  # The result will be retrieved from the cache
            3
        :param cache_name: The cache name to use, must be a hashable object. If None, the function name will be used
        :param params: The parameters to use as cache id, if None, all parameters will be used (*args, **kwargs)
        :param always_execute: If True, the function will be executed even if the cache is valid. The result will be cached
        """

        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                nonlocal cache_name, params
                cache_id = self._get_cache_id(params, *args, **kwargs)
                if cache_name is None:
                    cache_name = func.__name__
                if always_execute:
                    cache_data = await func(*args, **kwargs)
                    self.set(
                        cache_name=cache_name, cache_id=cache_id, cache_data=cache_data
                    )
                    return cache_data
                cache_data = self.get(cache_name=cache_name, cache_id=cache_id)
                if cache_data is None:
                    cache_data = await func(*args, **kwargs)
                    self.set(
                        cache_name=cache_name, cache_id=cache_id, cache_data=cache_data
                    )
                return cache_data

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                nonlocal cache_name, params
                cache_id = self._get_cache_id(params, *args, **kwargs)
                if cache_name is None:
                    cache_name = func.__name__
                if always_execute:
                    cache_data = func(*args, **kwargs)
                    self.set(
                        cache_name=cache_name, cache_id=cache_id, cache_data=cache_data
                    )
                    return cache_data
                cache_data = self.get(cache_name=cache_name, cache_id=cache_id)
                if cache_data is None:
                    cache_data = func(*args, **kwargs)
                    self.set(
                        cache_name=cache_name, cache_id=cache_id, cache_data=cache_data
                    )
                return cache_data

            # Check if the function is async
            if inspect.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper

        return decorator

    def invalidate(
        self,
        cache_name: Optional[Hashable] = None,
        params: Optional[Union[Iterable[str], str]] = None,
        before: bool = False,
    ) -> Callable:
        """
        Cache invalidate decorator
        Usage:
            >>> cache = MemoryCache()
            >>> @cache.invalidate(cache_name='math-plus', params=('a', 'b'))
            >>> def plus(*, a, b):  # The function must have keyword arguments in order to use the params argument
            >>>     return a + b
            >>> plus(a=1, b=2)  # The result will deleted from the cache
        :param cache_name: The cache name to use, must be a hashable object. If None, the function name will be used
        :param params: The parameters to use as cache id, if None, all parameters will be used (*args, **kwargs)
        :param before: If True, the cache will be invalidated before the function is executed. Default is after
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                nonlocal cache_name, params
                cache_id = self._get_cache_id(params, *args, **kwargs)
                if cache_name is None:
                    cache_name = func.__name__
                if before:
                    self.delete(cache_name=cache_name, cache_id=cache_id)
                result = func(*args, **kwargs)
                if not before:
                    self.delete(cache_name=cache_name, cache_id=cache_id)
                return result

            return wrapper

        return decorator

    def get(self, cache_name: Hashable, cache_id: Hashable) -> Optional[Any]:
        """
        Get cached data
        :param cache_name: The cache name to get the data from
        :param cache_id: The cache id to get the data from
        :return: The cached data
        """
        return self._cache.get(cache_name, {}).get(cache_id)

    def set(self, cache_name: Hashable, cache_id: Hashable, cache_data: Any):
        """
        Set cached data
        :param cache_name: The cache name to set the data to
        :param cache_id: The cache id to set the data to
        :param cache_data: The data to cache
        """
        self._cache.setdefault(cache_name, {})[cache_id] = cache_data

    def delete(self, cache_name: Hashable, cache_id: Optional[Hashable] = None):
        """
        Delete cached data
        :param cache_name: The cache name to delete the data from
        :param cache_id: The cache id to delete the data from, if None, all data from the cache name will be deleted
        """
        if cache_id:
            self._cache.get(cache_name, {}).pop(cache_id, None)
        else:
            self._cache.pop(cache_name, None)

    def clear(self):
        """Clear all cached data"""
        self._cache = {}

    def get_stats(self) -> Dict[Hashable, int]:
        """Return cache stats, the number of cached data per cache name"""
        return {
            cache_name: len([i for i in cache if cache[i] is not None])
            for cache_name, cache in self._cache.items()
        }


cache_memory = MemoryCache()
