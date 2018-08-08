
import os
import json
import time
import builtins
import simpleflock

_env = builtins.__xonsh_env__


class SharedCache():
    '''Stick environment variables in a shared file'''

    def __init__(self, filename=f'{_env["TMPDIR"]}/cachefile'):
        self.cache_file = filename
        self.lock_file = f'{filename}.lock'
        self.timestamp = 0
        self.shared = dict()
        self._load_shared_values()

    def share_value(self, names):
        'Identify an environment variable to share'
        for name in names:
            if name not in self.shared:
                self.shared[name] = _env.get(name, None)
        self._save_shared_values()

    def _save_shared_values(self):
        'Write shared variables out to the cache file'
        for key in self.shared:
            self.shared[key] = _env.get(key, None)

        with simpleflock.SimpleFlock(self.lock_file):
            with open(self.cache_file, 'w') as filehandle:
                json.dump(self.shared, filehandle)
                filehandle.flush()
        self.timestamp = time.time()

    def _load_shared_values(self):
        'Load shared variables from the cache file'
        with simpleflock.SimpleFlock(self.lock_file):
            try:
                for key, value in json.load(open(self.cache_file)).items():
                    self.shared[key] = value
                    if value is None and key in _env:
                        del _env[key]
                    else:
                        _env[key] = value
            except IOError:
                return
            except Exception as the_exception:
                print("Failed to reload shared values.", the_exception)
                return
        self.timestamp = time.time()

    def __call__(self):
        'Check if saving or loading need to happen'
        try:
            if os.stat(self.cache_file).st_mtime > self.timestamp:
                self._load_shared_values()
        except FileNotFoundError:
            # Don't care if we can't read/write the file
            pass
        except Exception as e:
            print(e)

        for key in self.shared:
            if self.shared.get(key) != _env.get(key):
                return
        return


shared_cache = SharedCache()


@events.on_pre_prompt
def shared_cache_update():
    'Func to be decorated for prompt updates'
    shared_cache()


aliases['share'] = shared_cache.share_value
