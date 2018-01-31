
from random import SystemRandom
import pytest

from cacheout import LRUCache


parametrize = pytest.mark.parametrize
random = SystemRandom()


def next_keys(cache):
    for n in range(cache.maxsize, cache.maxsize * 2):
        cache.set(n, n)
        assert cache.full()
        yield n


@pytest.fixture
def cache():
    _cache = LRUCache(maxsize=10)
    for n in range(_cache.maxsize):
        _cache.set(n, n)
    assert _cache.full()
    return _cache


def assert_keys_are_evicted_in_order(cache, keys):
    """Assert that cache keys are evicted in the same order as `keys`."""
    for n in range(cache.maxsize, cache.maxsize * 2):
        cache.set(n, n)
        assert cache.full()
        assert keys.pop(0) not in cache

        for key in keys:
            assert key in cache


def test_lru_set_eviction(cache):
    """Test that LRUCache evicts least recently set entries first."""
    keys = random.sample(cache.keys(), len(cache))

    for key in keys:
        cache.set(key, key)

    assert_keys_are_evicted_in_order(cache, keys)


def test_lru_get_eviction(cache):
    """Test that LRUCache evicts least recently accessed entries first."""
    keys = random.sample(cache.keys(), len(cache))

    for key in keys:
        cache.get(key)

    assert_keys_are_evicted_in_order(cache, keys)


def test_lru_get_set_eviction(cache):
    """Test that LRUCache evicts least recently set/accessed entries first."""
    all_keys = list(cache.keys())
    get_keys = random.sample(all_keys, len(cache) // 2)
    set_keys = random.sample(set(all_keys).difference(get_keys),
                             len(cache) // 2)

    assert not set(get_keys).intersection(set_keys)
    assert set(get_keys + set_keys) == set(all_keys)

    for key in get_keys:
        cache.get(key)

    for key in set_keys:
        cache.set(key, key)

    keys = get_keys + set_keys

    assert_keys_are_evicted_in_order(cache, keys)


def test_lru_get(cache):
    """Test that LRUCache.get() returns cached value."""
    for key, value in cache.items():
        assert cache.get(key) == value
