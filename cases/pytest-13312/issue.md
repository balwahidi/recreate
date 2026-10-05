# [regression,8.2.2] `KeyError` sometimes crashes test collection on PyPy while reordering fixtures

Reported by @webknjaz on 2025-03-19

So @bdraco was adding new tests in https://github.com/aio-libs/multidict/pull/1072. And it worked at first. But they had readability problems, and I added a few refactoring commits on top. And that's when things went south.

The first version of the tests made use of `@pytest.mark.parametrize` which I later converted into a parametrized fixture. That specific fixture depends on `request: pytest.FixtureRequest`, but doesn't depend on anything else we have declared in `conftest.py`.

The params set uses a trick that @The-Compiler has shown in his EuroPython 2023 workshop — wrapping them in dataclasses featuring `__str__()` interface. Not sure if that's relevant, though.


So the traceback I'm talking about is only happening on PyPy and looks like this:
```console
Run python -Im pytest tests -v --cov-report xml --junitxml=.test-results/pytest/test.xml --no-c-extensions
============================= test session starts ==============================
platform linux -- Python 3.9.19[pypy-7.3.16-final], pytest-8.3.5, pluggy-1.5.0 -- /opt/hostedtoolcache/PyPy/3.9.19/x64/bin/python
codspeed: 3.2.0 (disabled, mode: walltime, timer_resolution: 1.0ns)
cachedir: .pytest_cache
rootdir: /home/runner/work/multidict/multidict
configfile: pytest.ini
plugins: cov-6.0.0, codspeed-3.2.0
collecting ... collected 1161 items
INTERNALERROR> Traceback (most recent call last):
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/_pytest/main.py", line 283, in wrap_session
INTERNALERROR>     session.exitstatus = doit(config, session) or 0
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/_pytest/main.py", line 336, in _main
INTERNALERROR>     config.hook.pytest_collection(session=session)
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/pluggy/_hooks.py", line 513, in __call__
INTERNALERROR>     return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/pluggy/_manager.py", line 120, in _hookexec
INTERNALERROR>     return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/pluggy/_callers.py", line 139, in _multicall
INTERNALERROR>     raise exception.with_traceback(exception.__traceback__)
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/pluggy/_callers.py", line 122, in _multicall
INTERNALERROR>     teardown.throw(exception)  # type: ignore[union-attr]
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/_pytest/logging.py", line 790, in pytest_collection
INTERNALERROR>     return (yield)
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/pluggy/_callers.py", line 122, in _multicall
INTERNALERROR>     teardown.throw(exception)  # type: ignore[union-attr]
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/_pytest/warnings.py", line 121, in pytest_collection
INTERNALERROR>     return (yield)
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/pluggy/_callers.py", line 122, in _multicall
INTERNALERROR>     teardown.throw(exception)  # type: ignore[union-attr]
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/_pytest/config/__init__.py", line 1417, in pytest_collection
INTERNALERROR>     return (yield)
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/pluggy/_callers.py", line 103, in _multicall
INTERNALERROR>     res = hook_impl.function(*args)
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/_pytest/main.py", line 347, in pytest_collection
INTERNALERROR>     session.perform_collect()
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/_pytest/main.py", line 812, in perform_collect
INTERNALERROR>     hook.pytest_collection_modifyitems(
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/pluggy/_hooks.py", line 513, in __call__
INTERNALERROR>     return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/pluggy/_manager.py", line 120, in _hookexec
INTERNALERROR>     return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/pluggy/_callers.py", line 139, in _multicall
INTERNALERROR>     raise exception.with_traceback(exception.__traceback__)
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/pluggy/_callers.py", line 122, in _multicall
INTERNALERROR>     teardown.throw(exception)  # type: ignore[union-attr]
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/_pytest/cacheprovider.py", line 443, in pytest_collection_modifyitems
INTERNALERROR>     res = yield
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/pluggy/_callers.py", line 122, in _multicall
INTERNALERROR>     teardown.throw(exception)  # type: ignore[union-attr]
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/_pytest/cacheprovider.py", line 373, in pytest_collection_modifyitems
INTERNALERROR>     res = yield
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/pluggy/_callers.py", line 103, in _multicall
INTERNALERROR>     res = hook_impl.function(*args)
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/_pytest/fixtures.py", line 1627, in pytest_collection_modifyitems
INTERNALERROR>     items[:] = reorder_items(items)
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/_pytest/fixtures.py", line 233, in reorder_items
INTERNALERROR>     reorder_items_atscope(
INTERNALERROR>   File "/opt/hostedtoolcache/PyPy/3.9.19/x64/lib/pypy3.9/site-packages/_pytest/fixtures.py", line 282, in reorder_items_atscope
INTERNALERROR>     other_scoped_items_by_argkey[argkey].move_to_end(
INTERNALERROR> KeyError: <Function test_setdefault[case-insensitive-pure-python-module]>

============================ no tests ran in 5.81s =============================
Error: Process completed with exit code 3.
```

I was able to reproduce it locally on my Gentoo Linux laptop using pypy3.9-7.3.16. But I wasn't really able to make the repro smaller. I learned that this traceback is first seen in `pytest == 8.2.2`. And `pytest == 8.2.1` does not have this problem.

So the current STR is something like:
1. `pyenv install pypy3.9-7.3.16`
2. `pyenv virtualenv pypy3.9-7.3.16 multidict-pyenv-pypy3.9-7.3.16`
3. `pyenv shell multidict-pyenv-pypy3.9-7.3.16`
4. Get a copy of https://github.com/aio-libs/multidict/pull/1072
5. `pip install -r requirements/pytest.txt`
6. `pip install -e .`
7. `SETUPTOOLS_SCM_PRETEND_VERSION_FOR_PYTEST='8.2.2.dev0+first-broken-due-to-pr12414-regression' pip install 'pytest @ https://github.com/pytest-dev/pytest/archive/214d098fcce88940f5ce9353786b3cc8f0bd3938.tar.gz'`
8. And finally run `pytest --collect-only --no-cov tests/test_abc.py tests/test_copy.py tests/test_incorrect_args.py tests/test_multidict.py tests/test_mypy.py tests/test_pickle.py tests/test_types.py tests/test_update.py tests/test_version.py`

These aren't all the test modules of the project. Removing them from CLI args or removing some of the tests inside makes it so that it doesn't traceback anymore. That's why I wasn't able to come up with a single-snippet reproducer. It feels like it only happens when a certain amount of tests is hit or something.

I also ran it with `--pdb` which allowed me to see the value of `item` at that point when `OrderedDict.move_to_end()` is called: https://github.com/pytest-dev/pytest/blame/2b40981/src/_pytest/fixtures.py#L278C29-L280C30.
It kinda suggests that the PyPy implementation of `OrderedDict` is weird:
```pycon
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PDB post_mortem (IO-capturing turned off) >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
> ~/.pyenv/versions/pypy3.9-7.3.16/envs/multidict-pyenv-pypy3.9-7.3.16/lib/pypy3.9/site-packages/_pytest/fixtures.py(236)fix_cache_order()
-> scoped_items_by_argkey[key].move_to_end(item, last=False)
(Pdb) pp item
<Function test_popitem[case-insensitive-pure-python-module]>
(Pdb) pp [(k, v) for k, v in scoped_items_by_argkey[key].items() if str(k) == '<Function test_popitem[case-insensitive-pure-python-module]>']
[(<Function test_popitem[case-insensitive-pure-python-module]>, None),
 (<Function test_popitem[case-insensitive-pure-python-module]>, None)]
(Pdb) pp scoped_items_by_argkey[key,item]
*** KeyError: <Function test_popitem[case-insensitive-pure-python-module]>
(Pdb) pp [(k, v, id(k), hash(k)) for k, v in scoped_items_by_argkey[key].items() if str(k) == '<Function test_popitem[case-insensitive-pure-python-module]>']
[(<Function test_popitem[case-insensitive-pure-python-module]>,
  None,
  140541205124888,
  -760398202047905062),
 (<Function test_popitem[case-insensitive-pure-python-module]>,
  None,
  140541205124888,
  -760398202047905062)]
(Pdb) pp id(item), hash(item)
(140541205124888, -760398202047905062)
```
🤔 *Why* does this dict have duplicate keys? 😱

Anyway.. I confirmed that doing `SETUPTOOLS_SCM_PRETEND_VERSION_FOR_PYTEST='8.2.2.dev0+last-working-right-before-pr12414-regression' pip install 'pytest @ https://github.com/pytest-dev/pytest/archive/b41d5a52bbb808780ab310456d71e5ce509fd402.tar.gz'` makes the problem go away (which is expected because it does not yet have the `OrderedDict.move_to_end()` call).

And so this makes https://github.com/pytest-dev/pytest/pull/12414 (https://github.com/pytest-dev/pytest/pull/12409) responsible for the regression.

cc @bluetech I hope you'll have at least some idea of where to look because I've spent enough time staring at this w/o any clue...


---

UPD: I also forgot to mention that removing our own `pytest_collection_modifyitems` in `conftest.py` does not help in any way, it still reproduces. Plus, changing the fixture scopes to match what we have in `conftest.py` has no effect either.

UPD2: pypy3.11-7.3.19 shows this behavior too.
