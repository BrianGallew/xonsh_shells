"""A shared cache for environment variables.  In theory, new values are
updated whenver changes are detected in the cache file.

"""
import builtins  # This is the *xonsh* builtins!
import os
import pickle
import time
from typing import Sequence

import simpleflock

_env = builtins.__xonsh__.env

__all__ = ()  # Nothing here is really shared for export.


class SharedCache:
    """Stick environment variables in a shared file"""

    def __init__(self, filename=f'{_env["TMPDIR"]}/cachefile'):
        self.cache_file = filename
        self.lock_file = f"{filename}.lock"
        self.timestamp = 0
        self.shared = dict()
        self._load_shared_values()

    def share_value(self, names: Sequence[str]):
        """Identify an environment variable to share

        :param names: an iterable of names to add to the shared_vlue list
        """
        for name in names:
            self.shared[name] = _env.get(name, None)
        self.save_shared_values()

    def save_shared_values(self):
        "Write shared variables out to the cache file"
        for key in self.shared:
            self.shared[key] = _env.get(key, None)

        with simpleflock.SimpleFlock(self.lock_file):
            with open(self.cache_file, "wb") as filehandle:
                pickle.dump(self.shared, filehandle)
        self.timestamp = time.time()

    def _load_shared_values(self):
        "Load shared variables from the cache file"
        with simpleflock.SimpleFlock(self.lock_file):
            try:
                self.shared = pickle.load(open(self.cache_file, "rb"))
            except IOError:
                return
            except Exception as the_exception:
                print("Failed to reload shared values.", the_exception)
                return
        for key, value in self.shared.items():
            if value is None and key in _env:
                del _env[key]
            else:
                _env[key] = value
        self.timestamp = time.time()

    def __call__(self):
        "Check if saving or loading need to happen"
        try:
            if os.stat(self.cache_file).st_mtime > self.timestamp:
                self._load_shared_values()
        except FileNotFoundError:
            # Don't care if we can't read/write the file
            pass
        except Exception as e:
            print(e)


shared_cache = SharedCache()


@events.on_envvar_change  # noqa: F821 # pylint: disable=undefined-variable
def shared_cache_save(**_):
    "Func to be decorated for environment changes"
    shared_cache.save_shared_values()


@events.on_precommand  # noqa: F821 # pylint: disable=undefined-variable
def shared_cache_load(**_):
    "Func to be decorated for to keep the environment up to date"
    shared_cache()


aliases[  # noqa: F821 # pylint: disable=undefined-variable
    "share"
] = shared_cache.share_value
