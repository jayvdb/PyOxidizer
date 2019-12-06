run_all = False
quit_early = False
ignore_star_test_ignore = False

from pprint import pprint
import importlib
import os
import os.path
import sys

dist_root = './build/target/x86_64-unknown-linux-gnu/debug/pyoxidizer/python.608871543e6d/python/install'
dist_root = os.path.abspath(dist_root)
cpython_root = dist_root + '/lib/python3.7/'

os.environ['_PYTHON_PROJECT_BASE'] = dist_root
sys._home = dist_root

# This is needed to set base paths needed for sysconfig to provide the
# correct paths, esp Python.h
sys.base_exec_prefix = sys.exec_prefix = sys.base_prefix = sys.prefix = dist_root

from distutils.sysconfig import get_python_lib  # used to determine stdlib

import import_hooks

# FIXME:
_platbase = '/usr/lib64/python3.7/lib-dynload/'

base_pytest_args = [
    '--continue-on-collection-errors',
    '-c/dev/null',  # TODO: make OS agnostic
    '-rs',
    '--disable-pytest-warnings',
    #'--cache-clear',
    '-pno:cacheprovider',
    # Breaks --ignore
    '-pno:xdoctest',
    # Breaks --ignore https://github.com/bitprophet/pytest-relaxed/issues/8
    '-pno:relaxed',
    '-pno:flaky',
    '-pno:doctestplus',  # breaks jsonpointer tests
    '-pno:profiling',  # broken regex SyntaxError('invalid escape sequence..')

    # useful to check clashes of test packages with real packages
    #'--import-mode=append',
]
base_pytest_args.append('--maxfail=10')


package_base_patterns = [
    '/home/jayvdb/projects/osc/d-l-py/python-{pypi_name}/{pypi_name}-{version}/',
    '/home/jayvdb/projects/osc/d-l-py/python-{pypi_name}{version_major}/{pypi_name}-{version}/',
    '/home/jayvdb/projects/osc/devel:languages:python:pytest/python-{pypi_name}/{pypi_name}-{version}/',
    '/home/jayvdb/projects/osc/devel:languages:python:numeric/python-{pypi_name}/{pypi_name}-{version}/',
    '/home/jayvdb/projects/osc/devel:languages:python:flask/python-{pypi_name}/{pypi_name}-{version}/',
    '/home/jayvdb/projects/osc/devel:languages:python:django/python-{pypi_name}/{pypi_name}-{version}/',
    '/home/jayvdb/projects/osc/devel:languages:python:aws/python-{pypi_name}/{pypi_name}-{version}/',
    '/home/jayvdb/projects/python/{pypi_name}/',
    '/home/jayvdb/projects/python/{mod_name}/',
    '/home/jayvdb/projects/osc/py-new/python-{pypi_name}/{pypi_name}-{version}/',
]



class TestPackage:
    def __init__(self, name, test_ignores=None, pypi_name=None, mod_name=None, version=None, other_mods=None):
        self.pypi_name = pypi_name or name
        self._mod_name = mod_name or name.replace('-', '_')
        self._mods = [self.mod_name] + (other_mods or [])
        self.version = version
        self.test_ignores = test_ignores

    @property
    def _mod_is_default(self):
        return self.mod_name == self.pypi_name.replace('-', '_')

    @property
    def mod_name(self):
        return self._mod_name

    @mod_name.setter
    def mod_name(self, value):
        self._mod_name = value
        self._mods[0] = value

    def __str__(self):
        return self._mod_name

    def __repr__(self):
        return f'TestPackage({self.pypi_name})'

    def __eq__(self, other):
        if isinstance(other, str):
            return other in self._mods
        return super().__eq__(other)

    def __contains__(self, item):
        if item in self._mods:
            #print('__contains__ {!r} {!r}'.format(self._mods, item))
            return True
        for mod in self._mods:
            if item.startswith(mod + '.'):
                return True
        return False

    def __hash__(self):
        return hash(self._mod_name)


# These looks like tests, but are not
not_tests = ['jinja2.tests']

no_load_packages = [
    # setuptools loads lib2to3, which tries to load its grammar file
    'lib2to3',

    # https://github.com/HypothesisWorks/hypothesis/issues/2196
    # 'hypothesis', 'hypothesis.extra.pytestplugin',

    # urllib3 uses built extension brotli if present
    # however it is needed by httpbin
    # 'brotli',
    # requests uses built extension simplejson if present
    'simplejson',
    # hypothesis uses django and numpy if present,
    # and those cause built extensions to load
    'django', 'numpy',
    # Other packages which will load built extension
    #'flask',
    'scandir',
]
import_hooks.add_import_error(no_load_packages)

import_hooks.add_empty_load([
    # 'pytest-cov' and 'coverage' may exist commonly in site-packages,
    # however coverage uses a built extension which we do not want to load
    'pytest_cov', 'pytest_cov.plugin',
    'django_webtest.pytest_plugin', 'django_webtest',
    # Other pytest plugins which might be loaded
    'celery', 'celery.contrib.pytest',
    # 'pytest_xprocess',

    # pluggy imports this on py37 :/
    #'importlib_metadata',
])



empty_load_packages = [
    # ---- old stuff:

    # depends on PyYAML
    # 'pytest_httpbin.plugin',

    # __file__
    'cell',  # https://github.com/celery/cell/issues/21
    #'httplib2',
    # 'distorm3',
    'kombu', # this doesnt work 'celery',
    #'tinycss2',  # 30,000+  FileNotFoundError: [Errno 2] No such file or directory: 'VERSION'

    'blist',  # not py37 compat

    'sentry_sdk',  # breaks dns
    # 'pyx',  # blows up
    'webbrowser', # grrrr
    #'pyglet',
    'eventlet',
    'jsonrpcclient.__main__',
    'dns',  # KeyError: 'dns.rdtypes.ANY'
    'tinycss2', 'pyphen', 'phabricator',

    # stdlib problems
    'this',
    'macpath',
    'formatter',
    'antigravity',
]

import_hooks.add_empty_load(empty_load_packages)

import_hooks.add_junk_file_dunder([
    'pluggy',
    'coverage.html', 'coverage.control',
    'pycparser.c_lexer', 'pycparser.c_parser',
    'ruamel.yaml.main',
    'tqdm._version',
    'networkx.release', 'networkx.generators.atlas',
    'plumbum',
    'botocore', 'botocore.httpsession',
])


import_hooks.add_after_import_hook(
    ['certifi.core'],
    import_hooks.certifi_where_hack,
)

import_hooks.add_empty_load(no_load_packages)
h = import_hooks.add_empty_load(['networkx.algorithms.tree.recognition'])
import networkx
import_hooks.unregister_import_hook(h)

import sys
del sys.modules['networkx.algorithms.tree.recognition']

import networkx.algorithms.tree.recognition
print(networkx.algorithms.tree.recognition.__spec__)

import_hooks.add_junk_file_dunder([
    'hashid',
], is_module=True)


import_hooks.redirect_get_data_resources_open_binary(['pytz', 'jsonschema', 'text_unidecode', 'pyx'])
import_hooks.redirect_get_data_resources_open_binary(['dateutil.zoneinfo', 'jsonrpcclient.parse'], is_module=True)
import_hooks.overload_open(['lark.load_grammar', 'lark.tools.standalone'], is_module=True)
import_hooks.overload_open(['pycountry', 'pycountry.db', 'stdlib_list.base'])

# doesnt work:
#import_hooks.redirect_get_data_resources_open_binary(['yaspin'], is_module=True)

#pytest.main(['-v', '-pno:django', '/home/jayvdb/projects/osc/d-l-py/python-mock/mock-2.0.0/mock/tests/__main__.py'])


# needs to be before! during exec
#import_hooks.overload_open(['netaddr.eui.ieee', 'netaddr.ip.iana'], is_module=True)


# dont work: 'phabricator', 'tldextract', 's3transfer'
import_hooks.overload_open(['whois', 'depfinder', 'virtualenv'])

# for tinycss2
#import pathlib
#pathlib._NormalAccessor.open = pathlib._normal_accessor.open = import_hooks._catch_fake_open

# This module is unusable unless another import hook is created
#import_hooks.add_external_file_dunder(cpython_root, ['lib2to3.pygram'])

# black:
import_hooks.add_relocated_external_file_dunder(cpython_root, 'blib2to3.pygram', 'b')

import_hooks.add_file_dunder_during(cpython_root, 'test_future.test_imports_urllib', 'urllib')
import_hooks.add_file_dunder_during(cpython_root, 'greenlet', 'distutils')
import_hooks.add_file_dunder_during(cpython_root, 'hypothesis', 'os')

#import_hooks.add_external_file_dunder( , 'tornado.testing')

#import_hooks.add_relocated_external_file_dunder(
#    cpython_root, "blist.test.test_support", "blist")
#import blist.test.test_support

assert sys.oxidized
pyox_finder = sys.meta_path[0]
_pyox_modules = list(pyox_finder.package_list())

# pyox_finder.__spec__.__module__ = None

def aggressive_import(name):
    if 'python-' in name:
        name = name.replace('python-', '')

    exceptions = []

    if '-' in name:
        try:
            package, _, module = name.partition('-')
            mod = __import__(name.replace('-', '.'), package)
            mod = getattr(mod, module)
            return mod
        except ImportError as e:
            exceptions.append(e)

        name = name.replace('-', '_')

    try:
        mod = importlib.import_module(name)
        return mod
    except ImportError as e:
        exceptions.append(e)
    try:
        mod = importlib.import_module(name.lower())
        return mod
    except ImportError as e:
        exceptions.append(e)
    try:
        mod = importlib.import_module(name.upper())
        return mod
    except ImportError as e:
        exceptions.append(e)

    if name.lower().startswith('py'):
        try:
            mod = importlib.import_module(name[2:])
            return mod
        except ImportError as e:
            exceptions.append(e)
        try:
            mod = importlib.import_module(name.lower()[2:])
            return mod
        except ImportError as e:
            exceptions.append(e)

    if name.lower().endswith('py'):
        try:
            mod = importlib.import_module(name[:-2])
            return mod
        except ImportError as e:
            exceptions.append(e)
        try:
            mod = importlib.import_module(name.lower()[:-2])
            return mod
        except ImportError as e:
            exceptions.append(e)

    if name.lower().endswith('python'):
        try:
            mod = importlib.import_module(name[:-6])
            return mod
        except ImportError as e:
            exceptions.append(e)
        try:
            mod = importlib.import_module(name.lower()[:-6])
            return mod
        except ImportError as e:
            exceptions.append(e)

    if exceptions:
        raise exceptions[0]

    raise ImportError('{} not found'.format(name))


def _find_version(mod, verbose=False):
    name = mod.__name__

    version = None

    try:
        version = mod.__version__
    except AttributeError as e:
        try:
            version = mod.version
        except AttributeError as e2:
            try:
                version = mod.VERSION
            except AttributeError as e2:
                pass

    if not version or name == 'pytimeparse':
        try:
            data = importlib.resources.open_binary(name, 'VERSION').read()
            return data.decode('utf-8').strip()
        except Exception as e:
            if verbose:
                print('_find_version({}): no file VERSION failed: {!r}'.format(name, e))

    if not version:
        try:
            """v_mod = __import__(mod.__name__ + '.version', mod.__name__)
            if verbose:
                print('imported {!r}'.format(v_mod))
            v_mod = v_mod.version
            if verbose:
                print('found version {!r}'.format(v_mod))
            """
            v_mod = importlib.import_module(mod.__name__ + '.version')
            if verbose:
                print('imported {!r}'.format(v_mod))
        except ImportError as e:
            if verbose:
                print('_find_version({}): {!r}'.format(name, e))
        else:
            try:
                version = v_mod.__version__
            except AttributeError:
                version = v_mod.version
            if verbose:
                print('found version {!r}'.format(version))

    if not version:
        try:  # pipx
            v_mod = __import__(mod.__name__ + '.main', fromlist=['main'])
            if verbose:
                print('imported {!r}'.format(v_mod))
            version = v_mod.__version__
            if verbose:
                print('found version {!r}'.format(v_mod))
        except (AttributeError, ImportError) as e:
            if verbose:
                print('_find_version({}): {!r}'.format(name, e))

    if name.startswith('unicodedata'):  # also includes unicodedata2
        version = mod.unidata_version

    if not version:
        if verbose:
            print(f'version not found for {mod}')
        return

    try:
        version = version()
    except Exception:
        pass

    if isinstance(version, tuple):
        version = '.'.join(str(i) for i in version)

    if verbose:
        print('_find_version({}) = {}'.format(mod, version))

    return version

def _find_tests_under(base, mod_name, verbose=False):
    base = base + '/' if not base.endswith('/') else base

    if verbose:
        print('looking under {}'.format(base))

    # peewee if os.path.exists(base + 'runtests.py'):
    #    return 'runtests.py'
    if os.path.isdir(base + 'tests/'):
        if os.path.isdir(base + 'tests/lib3/'):  # PyYAML
            return 'tests/lib3/'
        if mod_name == 'botocore' and os.path.isdir(base + 'tests/unit/'):
            return 'tests/unit/'
        if os.path.exists(base + 'tests/test.py'):
            return 'tests/test.py'
        if os.path.exists(base + 'tests/tests.py'):
            return 'tests/tests.py'
        if os.path.exists(base + 'test.py'):  # chardet 4 has tests/ and test.py
            return 'test.py'
        return 'tests/'
    if os.path.exists(base + 'tests.py') and mod_name + '.tests' not in not_tests:
        return 'tests.py'
    elif os.path.exists(base + 'test_' + mod_name + '.py'):  # six
        return 'test_' + mod_name + '.py'
    elif os.path.exists(base + 'simple_unit_tests.py'):  # pyparsing
        return 'simple_unit_tests.py'
    elif os.path.exists(base + 'unitTests.py'):  # pyparsing not working
        return 'unitTests.py'
    elif os.path.isdir(base + 'test/'):  # todo: check for .py files
        return 'test/'
    elif os.path.isdir(base + '_test/'):  # ruamel.yaml
        return '_test/'
    elif os.path.isdir(base + 'testing/'):
        return 'testing/'
    elif os.path.isdir(base + 'ast3/tests/'):  # typed-ast
        return 'ast3/tests/'
    elif os.path.isdir(base + 't/'):  # celery: vine & billiard
        if os.path.exists(base + 't/integration/tests/test_multiprocessing.py'):
            return 't/unit/'  # billiard ^ is py2 only
        return 't/'
    elif os.path.exists(base + 'test.py'):
        return 'test.py'


PY2 = False
py37_builtins = ('_abc', '_ast', '_codecs', '_collections', '_functools', '_imp', '_io', '_locale', '_operator', '_signal', '_sre', '_stat', '_string', '_symtable', '_thread', '_tracemalloc', '_warnings', '_weakref', 'atexit', 'builtins', 'errno', 'faulthandler', 'gc', 'itertools', 'marshal', 'posix', 'pwd', 'sys', 'time', 'xxsubtype', 'zipimport')

def _is_std_lib(name, std_lib_dir):
    name, _, _ = name.partition('.')
    if name in py37_builtins:
        return True
    elif name in ['__phello__', 'config-3', '_frozen_importlib', '_frozen_importlib_external'] or name.startswith('config_3'):
        return True
    elif name in ['_pyoxidizer_importer']:
        return True
    rv = (os.path.isdir(std_lib_dir + name)
          or os.path.exists(std_lib_dir + name + '.py')
          or os.path.exists(_platbase + name + '.cpython-37m-x86_64-linux-gnu.so')  # TODO: use plat extension
          )
    #print('_is_std_lib', name, std_lib_dir)
    return rv


def package_versions(modules=None, builtins=None, namespace_packages=None,
                     standard_lib=None, exclude_imported=False,
                     std_lib_dir=None, verbose=False, exclude=None, exclude_main=True):
    """Retrieve package version information.

    When builtins or standard_lib are None, they will be included only
    if a version was found in the package.

    @param modules: Modules to inspect
    @type modules: list of strings
    @param builtins: Include builtins
    @type builtins: Boolean, or None for automatic selection
    @param standard_lib: Include standard library packages
    @type standard_lib: Boolean, or None for automatic selection
    """
    if not modules:
        modules = sys.modules.keys()

    if not std_lib_dir:
        std_lib_dir = get_python_lib(standard_lib=True)
    std_lib_dir = (
        std_lib_dir + '/' if not std_lib_dir.endswith('/') else std_lib_dir)

    root_packages = {key.split('.')[0] for key in modules}
    namespace_subpackages = set()
    for nspkg in namespace_packages or []:
        if nspkg not in root_packages:
            continue
        submodules = {'.'.join(key.split('.')[:2]) for key in modules if key.startswith(nspkg + '.')}
        namespace_subpackages |= submodules

    builtin_packages = {name.split('.')[0] for name in root_packages
                        if name in sys.builtin_module_names
                        or '_' + name in sys.builtin_module_names}

    if standard_lib is False and builtins is None:
        builtins = False

    # Improve performance by removing builtins from the list if possible.
    if builtins is False:
        root_packages = set(root_packages - builtin_packages)
    if exclude_main:
        root_packages -= {'__main__', '__mp_main__'}

    if verbose:
        print('root packages:', sorted(root_packages))

    std_lib_packages = []

    paths = {}
    data = {}

    for name in sorted(root_packages | namespace_subpackages):
        if exclude and name in exclude:
            continue

        info = {'name': name}

        if _is_std_lib(name, std_lib_dir):
            std_lib_packages.append(name)
            if standard_lib is False:
                continue
            info['type'] = 'standard libary'

        if name in builtin_packages:
            info['type'] = 'builtins'

        # print('About to import {}'.format(name))
        if exclude_imported and name in sys.modules:
            if verbose:
                print(f'Skipping {name}')
            continue

        try:
            package = importlib.import_module(name)
        except Exception as e:
            if verbose:
                print('import_module({}) failed: {!r}'.format(name, e))
            info['err'] = e
            data[name] = info
            continue

        info['package'] = package

        if '__file__' in package.__dict__ and package.__file__:
            # Determine if this file part is of the standard library.
            if os.path.normcase(package.__file__).startswith(
                    os.path.normcase(std_lib_dir)):
                std_lib_packages.append(name)
                if standard_lib is False:
                    continue
                info['type'] = 'standard libary'

            # Strip '__init__.py' from the filename.
            path = package.__file__
            if '__init__.py' in path:
                path = path[0:path.index('__init__.py')]

            if PY2:
                path = path.decode(sys.getfilesystemencoding())

            info['path'] = path
            if path in paths:
                print('Path {} of the package {} is already in defined paths assosciated with {}'.format(path, package, paths[path]))
            paths[path] = name
        else:
            if _is_std_lib(name, std_lib_dir):
                std_lib_packages.append(name)
                if standard_lib is False:
                    continue
                info['type'] = 'standard libary'

        version = _find_version(package)
        if version:
            info['ver'] = version

        # If builtins or standard_lib is None,
        # only include package if a version was found.
        if (builtins is None and name in builtin_packages) or \
                (standard_lib is None and name in std_lib_packages):
            if 'ver' in info:
                data[name] = info
            else:
                # Remove the entry from paths, so it isn't processed below
                del paths[info['path']]
        else:
            data[name] = info

    return data



def run_pytest(package, test_path=None, add_test_file_dunder=False, verbose=False):
    pypi_name = package.pypi_name
    mod_name = package.mod_name
    version = package.version
    excludes = package.test_ignores

    if verbose:
        print('run_pytest {} {} {}'.format(pypi_name, mod_name, version))

    import pytest

    if not package._mod_is_default:
        mod = aggressive_import(mod_name)
    else:
        try:
            mod = aggressive_import(pypi_name)
        except Exception as e:
            if verbose:
                print("aggressive_import {} failed: {!r}".format(pypi_name, e))
            raise e
        package.mod_name = mod_name = mod.__name__

    if not version:
        version = _find_version(mod, verbose=verbose)

    print('\nrun_pytest {} {} {}'.format(pypi_name, mod_name, version))

    if verbose:
        if not package._mod_is_default:
            print('{}({}) = {}'.format(pypi_name, mod_name, version))
        else:
            print('{} = {}'.format(pypi_name, version))

    found_bases = []
    hooks = []
    for pattern in package_base_patterns:
        package_base = pattern.format(
           pypi_name=pypi_name, mod_name=mod_name, version=version, version_major=version[0] if isinstance(version, str) else None)
        if os.path.isdir(package_base):
            if verbose:
                print('run_pytest found {}'.format(package_base))
            found_bases.append(package_base)
            if not test_path:
                mod_path = mod_name.replace('.', '/')
                test_path = _find_tests_under(package_base, mod_name)
                add_test_file_dunder = True
                if not test_path:
                    test_path = _find_tests_under(package_base + mod_path + '/', mod_name)
                    if test_path:
                        test_path = mod_path + '/' + test_path
                        add_test_file_dunder = test_path
                if not test_path:
                    test_path = _find_tests_under(package_base + 'src/' + mod_path + '/', mod_name)
                    if test_path:
                        package_base += 'src/'
                        test_path = mod_path + '/' + test_path
                        add_test_file_dunder = test_path
                if mod_name != mod_path:
                    if not test_path:
                        test_path = _find_tests_under(package_base + mod_name + '/', mod_name)
                        if test_path:
                            test_path = mod_name + '/' + test_path
                            add_test_file_dunder = test_path
                    if not test_path:
                        test_path = _find_tests_under(package_base + 'src/' + mod_name + '/', mod_name)
                        if test_path:
                            package_base += 'src/'
                            test_path = mod_name + '/' + test_path
                            add_test_file_dunder = test_path
                if not test_path:
                    test_path = _find_tests_under(package_base + 'src/', mod_path)
                    if test_path:
                        package_base += 'src/'
                        test_path = test_path
                        add_test_file_dunder = test_path
                if not test_path:  # kitchen
                    test_path = _find_tests_under(package_base + mod_name + '3/', mod_name)
                    if test_path:
                        package_base += mod_name + '3/'
                        test_path = test_path
                        add_test_file_dunder = test_path
                if not test_path:  # regex
                    test_path = _find_tests_under(package_base + mod_name + '_3/' + mod_name + '/', mod_name)
                    if test_path:
                        package_base += mod_name + '_3/'
                        test_path = mod_name + '/' + test_path
                        add_test_file_dunder = test_path
                if not test_path and verbose:
                    print('Couldnt find tests under {}'.format(package_base))

            if test_path:
                break
    else:
        if found_bases:
            return 'tests for {} not found in {!r}'.format(pypi_name, found_bases)
        else:
            return 'base for {} {} not found'.format(pypi_name, version)

    if add_test_file_dunder:
        if add_test_file_dunder is True:
            add_test_file_dunder = mod_name + '/' + 'tests/'
        add_test_file_dunder = add_test_file_dunder.replace('.py', '')
        add_test_file_dunder = add_test_file_dunder.replace('/', '.')
        if add_test_file_dunder.endswith('.'):
            add_test_file_dunder = add_test_file_dunder[:-1]
        if add_test_file_dunder not in not_tests:
            #if verbose:
            print('Adding __file__ for {} @ {}'.format(add_test_file_dunder, package_base))
            hooks.append(import_hooks.add_external_file_dunder(package_base, [add_test_file_dunder]))

    if mod_name == 'tornado':
        hooks.append(import_hooks.add_external_file_dunder(package_base, ['tornado.testing']))

    pytest_args = base_pytest_args.copy()
    if test_path == 't/' or mod_name in ['billiard', 'vine']:
        pytest_args.remove('-c/dev/null')

    if mod_name == 'ruamel.yaml':
        pytest_args += ['--ignore', '_test/lib']

    if excludes:
        ignores = [item for item in excludes if item.endswith('/') or item.endswith('.py')]
        excludes = [item for item in excludes if item not in ignores]
        for item in ignores:
            pytest_args.append('--ignore-glob=*' + item)

    if excludes and '*' in excludes:
        excludes.remove('*')

    if excludes:
        if len(excludes) == 1:
            pytest_args += ['-k', 'not {}'.format(excludes[0])]
        else:
            pytest_args += ['-k', 'not ({})'.format(' or '.join(excludes))]

    pytest_args.append('./' + test_path)

    os.chdir(package_base)
    print("Running {}-{} tests: {}> pytest {}".format(pypi_name, version, package_base, pytest_args))
    rv = pytest.main(pytest_args)
    for hook in hooks:
        import_hooks.unregister_import_hook(hook)
    return rv


def remove_test_modules(verbose=False):
    for name in sorted(sys.modules.keys()):
        # utils is owned by pycparser
        # case.pytest needs evicting otherwise vine fails
        if name.startswith('test_') or name.endswith('_test') or name.startswith('test.') or name.startswith('t.') or name.startswith('tests.') or name in ['t', 'utils', 'linecache', 'test', 'tests', 'conftest', 'case.pytest'] or name.startswith('pytest') or name.startswith('_pytest') or name == 'py' or name.startswith('py.'):
           if verbose:
               print('removing imported {}'.format(name))
           del sys.modules[name]

    #backports.test.__file__
    #sys.modules['test'] = backports.test
    #sys.modules['test.support'] = backports.test.support
    # vine fails without this>?
    #import case.pytest

    #assert 'tests' not in sys.modules
    #print(sorted(sys.modules))
    #import tests
    #print(tests.__file__)
    #assert 'kitchen3' not in tests.__file__


test_results = {}


def run_tests(packages, skip={}, quit_early=False, verbose=False):
    cwd = os.getcwd()
    sys_path = sys.path.copy()
    for package in packages:
        if verbose:
            print('looking at {}'.format(package))
        if package == ...:
            test_results[package] = 'break due to `...`!'
            break
        if isinstance(package, str) and len(package) > 50:
            print('skipping long string')
            continue

        if not isinstance(package, TestPackage):
            package = TestPackage(package)

        mod_name = package.mod_name 
        excludes = package.test_ignores
        version = package.version

        pypi_name = package.pypi_name

        if pypi_name in no_load_packages or pypi_name.lower() in no_load_packages:
            test_results[pypi_name] = 'load avoided'
            continue

        if pypi_name in skip or pypi_name.lower() in skip:
            continue

        if excludes and excludes[0] == '*' and (not ignore_star_test_ignore or len(excludes) == 1):
            print('Skipping {}'.format(package))
            rv = 0
        else:
            try:
                rv = run_pytest(package)
            except BaseException as e:
                if quit_early:
                    raise
                rv = e

        os.chdir(cwd)
        sys.path[:] = sys_path

        test_results[package] = rv

        if rv and quit_early or isinstance(rv, KeyboardInterrupt):
            if isinstance(rv, BaseException):
                raise rv
            sys.exit(rv)

        # Avoid clashes in test module names, like test_pickle in multidict and yarl
        # which causes pytest to fail
        remove_test_modules(verbose=verbose)

    pprint(test_results)


# for Pyphen needs os.listdir hacked
import pkg_resources
def fake_resource_filename(package, name):
    return '{}/{}/{}'.format(import_hooks._fake_root, package, name)

pkg_resources.resource_filename = fake_resource_filename


# Needed for test.support.__file__

import_hooks.add_external_cpython_test_file_dunder(cpython_root, support_only=True)

import_hooks.add_relocated_external_file_dunder(
    cpython_root, 'future.backports.urllib.request', 'future.backports')


# Needed by psutil test_setup_script
import_hooks.add_file_dunder_during(cpython_root, 'setuptools', 'distutils')

# needs test.support
regex_package = TestPackage('regex', [
    'test_main',
    'test_hg_bugs',  # _pickle.PicklingError: Can't pickle <built-in function compile>: import of module '_regex' failed
])  # opensuse outdated


packages = [
    TestPackage('pycountry', [
        'test_subdivisions_directly_accessible',  # 4844 vs 4836
        'test_locales',  # fails in gettext
    ], version='18.12.8'),  # exposes LOCALE_DIR, etc which will fail even if internal access is fixed
    TestPackage('vine'),
    # test suites break: async Event loop closed?
    TestPackage('decorator'),
    TestPackage('weakrefmethod'),  # ln -s test_weakmethod.py test_weakrefmethod.py
    TestPackage('pyasn1'),
    TestPackage('filelock'),  # ln -s py-filelock-3.0.12 filelock-3.0.12
    TestPackage('cached-property', ['test_threads_ttl_expiry']),
    TestPackage('Jinja2', ['TestModuleLoader']),
    TestPackage('async-timeout'),  # ln -s python-async_timeout python-async-timeout
    #...,

    TestPackage('tornado', test_ignores=[
        '*',
        'TestIOStreamWebMixin', 'TestReadWriteMixin', 'TestIOStreamMixin',
        'AutoreloadTest', 'GenCoroutineTest', 'HTTPServerRawTest', 'UnixSocketTest', 'BodyLimitsTest', 'TestIOLoopConfiguration', 'TestIOStream', 'TestIOStreamSSL', 'TestIOStreamSSLContext', 'TestPipeIOStream',
        'LoggingOptionTest',
        'SubprocessTest',
        'simple_httpclient_test',  # a few failures
        'test_error_line_number_extends_sub_error',
    ]),  # lots of failures
    TestPackage('PyNaCl', [
        '*',
        'test_bindings.py', 'test_box.py',  # binary() got an unexpected keyword argument 'average_size'
        'test_wrong_types',  # pytest5 incompatibility
    ], other_mods=['_sodium']),

    #...,

    TestPackage('bcrypt', other_mods=['_bcrypt']),  # pep 517

    TestPackage('pyparsing'),
    TestPackage('unicodedata2'),

    TestPackage('ruamel.std.pathlib', ['*']),  # no tests?
    TestPackage('ruamel.yaml', other_mods=['_ruamel_yaml']),  # upstream issue

    TestPackage('psutil', [
        '*',
        'test_process', 'TestProcessUtils', 'TestScripts', 'TestTerminatedProcessLeaks', 'test_multi_sockets_proc', 'test_memory_leaks',  # sys.executable
        'test_pid_exists', 'test_wait_procs', 'test_wait_procs_no_timeout', 'test_proc_environ',  # subprocess
        'test_warnings_on_misses', 'test_missing_sin_sout', 'test_no_vmstat_mocked',  # filename issues
        'TestFSAPIs',  # DSO loading
        'test_connections',  # all but one fail
        'test_emulate_use_sysfs', 'test_percent', 'test_cpu_affinity',  # vm problems
        'test_power_plugged',
        'test_cmdline', 'test_name',  # probable bug in how psutil calculates PYTHON_EXE
        'test_sanity_version_check',  # need to disable psutil.tests.reload_module
        'test_cmdline', 'test_pids', 'test_issue_687', # strange
        'test_unix_socketpair',
    ]),
    TestPackage('cffi', [
        '*',
        'TestBitfield', 'test_verify', 'TestDistUtilsCPython',  # loads built extension dynamically
        'TestZIntegration',  # popen
        'cffi0/test_vgen.py', 'cffi0/test_vgen2.py',  # lots of error
        'cffi1/test_parse_c_type.py',  # module 'cffi.cffi_opcode' has no attribute '__file__'
        'test_commontypes', 'test_zdist',  # module 'cffi' has no attribute '__file__'
        'TestNewFFI1',  # __file__
        'test_recompiler', 'embedding',  # __file__
        'cffi1/test_re_python.py',  # AttributeError: module 'distutils' has no attribute '__file__'
    ], other_mods=['_cffi_backend']),
    TestPackage('six', ['test_lazy']),  # assertion fails due to other packages; not worth isolating
    TestPackage('brotlipy', mod_name='brotli', version='0.7.0', test_ignores=[
        'test_streaming_compression', 'test_streaming_compression_flush',  # they take too long to complete
        'test_compressed_data_with_dictionaries',  # removed functionality in brotli 1.x
    ]),
    TestPackage('urllib3', [
        '*',
        'contrib/', 'with_dummyserver/', 'test_connectionpool.py', # requires tornado
        'test_cannot_import_ssl',  # probably oxidization makes test impossible
        'test_render_part', 'test_parse_url', 'test_match_hostname_mismatch', 'test_url_vulnerabilities',
    ]),
    TestPackage('pyOpenSSL', [
        'test_verify_with_time',  # in TestX509StoreContext
        'memdbg.py',  # creates a DSO and fails when importing it
        'test_debug.py',
        'EqualityTestsMixin', 'util.py',  # pytest incompatible structure
    ], mod_name='OpenSSL'),
    TestPackage('pycparser', [
        'test_c_generator.py', 'test_c_parser.py',  # inspect.getfile fails
    ], other_mods=['utils']),
    TestPackage('certifi', ['*']),  # has no tests
    TestPackage('pip', ['*']),  # completely broken, starting with __file__
    TestPackage('setuptools', ['*'], other_mods=['easy_install', 'pkg_resources']),  # mostly not useful within PyOxidizer, esp without pip, however pkg_resources is very important
    TestPackage('cryptography', [
        '*',
        'test_vector_version',  # ignore mismatch of cryptography master vs vectors released
        'test_osrandom_engine_is_default',  # uses python -c
        'TestAssertNoMemoryLeaks',  # test_openssl_memleak is skipped on openSUSE
        'TestEd25519Certificate', 'TestSubjectKeyIdentifierExtension', 'test_load_pem_cert', # missing files in vectors
        'test_aware_not_valid_after', 'test_aware_not_valid_before', 'test_aware_last_update', 'test_aware_next_update', 'test_aware_revocation_date',  #pytz problems
    ]),
    TestPackage('requests', [
        '*',
        'test_errors', # 2/4 "test_errors" fail, which is problematic
        'test_https_warnings',  # this one is problematic
        'TestTimeout',
        'test_proxy_error',
        # https://github.com/psf/requests/pull/5251
        'test_rewind_body_failed_tell', 'test_rewind_body_no_seek', 'test_conflicting_post_params', 'test_proxy_error'  # pytest compatibility
    ]),
    TestPackage('MarkupSafe'),
    TestPackage('idna'),
    TestPackage('chardet', ['*']),

    TestPackage('PyYAML', mod_name='yaml', other_mods=['_yaml'], test_ignores=['*']),  # tests incompatible with pytest, and need test DSOs which cant be loaded

    TestPackage('test-server', test_ignores=['*']),  # AttributeError: module 'tornado.web' has no attribute 'asynchronous'
    TestPackage('PySocks', mod_name='socks', other_mods=['sockshandler'], test_ignores=['*']),  # requires test_server

    # not listed

    TestPackage('importlib-metadata', ['test_zip']),
    TestPackage('jsonschema', [
        'test_cli.py',
        'test_jsonschema_test_suite.py',  # requires data set
        'test_validators.py',  # ImportError: cannot import name 'RefResolutionError' from 'jsonschema.validators'
        'test_repr',
    ]),
    TestPackage('logutils', ['test_hashandlers', 'RedisQueueTest']),  # unknown
    TestPackage('botocore', [  # supposed to use nose test runner
        'test_client_method_help', 'test_paginator_help_from_client', 'test_waiter_help_documentation',  # help() not included in PyOxidizer
        'test_dynamic_client_error', 'test_s3_special_case_is_before_other_retry', 'test_s3_addressing', 'TestCreateClient', 'TestClientMonitoring', 'TestSessionPartitionFiles', 'TestGenerateDBAuthToken', 'test_internal_endpoint_resolver_is_same_as_deprecated_public', # botocore.session:160: in create_default_resolver botocore.loaders:132: in _wrapper  botocore.exceptions.DataNotFoundError: Unable to load data for: endpoints
        'CloudFrontWaitersTest',  # botocore.exceptions.DataNotFoundError: Unable to load data for: cloudfront
        'TestGenerateDocs', 'TestClientDocumenter', 'test_example', 'test_method', 'docs',  # botocore.exceptions.DataNotFoundError: Unable to load data for: _retry
        'test_get_response_nonstreaming_ng', 'test_get_response_nonstreaming_ok', 'test_get_response_streaming_ng', 'test_get_response_streaming_ok', 'TestGenerateUrl',  'TestGeneratePresignedPost', # session.get_service_model('s3') botocore.exceptions.UnknownServiceError: Unknown service: 's3'. Valid service names are:
    ]),
    TestPackage('flexmock', [  # concerning, not investigated
        'test_flexmock_ordered_works_with_same_args',
        'test_flexmock_ordered_works_with_same_args_after_default_stub',
        'test_flexmock_preserves_stubbed_class_methods_between_tests',
        'test_flexmock_preserves_stubbed_object_methods_between_tests',
        'test_flexmock_removes_new_stubs_from_classes_after_tests',
    ]),
    TestPackage('virtualenv', [
        '*',  # ImportError: cannot import name '__file__' from 'virtualenv_support'
        # also 'test_cmdline',
    ], other_mods=['virtualenv_support']),
    TestPackage('Werkzeug', [
        'test_no_memory_leak_from_Rule_builder', 'test_find_modules',
        'test_debug.py', 'test_serving.py',   # hang somewhere in here
        'test_proxy_fix', 'test_http_proxy', 'test_append_slash_redirect',
        'test_shared_data_middleware',
    ]),
    TestPackage('pyelftools', [
        'run_examples_test.py',  # ImportError: cannot import name 'run_exe' from 'utils' (unknown location)
        # probably need to de-import 'utils' loaded from another package test suite
    ]),



    # should be patched!?  but green with one exclusion
    TestPackage('toolz', ['test_tlz'], other_mods=['tlz']),  # 'cytoolz',
    TestPackage('cytoolz', ['test_tlz']),  # 'cytoolz',

    # green
    TestPackage('kitchen', [
        'test_easy_gettext_setup_non_unicode', 'test_lgettext', 'test_lngettext', 'test_lgettext', 'test_lngettext', 'test_invalid_fallback_no_raise',  # not investigated
    ]),
    TestPackage('texttable', ['test_cli']),

    TestPackage('simplejson', ['TestTool']),
    TestPackage('msgpack'),
    TestPackage('wheel', ['test_bdist_wheel', 'test_tagopt']),  # uses sys.executable),
    TestPackage('aiodns', ['test_query_a_bad']),
    TestPackage('dnspython'),
    TestPackage('ptyprocess'),
    TestPackage('rfc3986'),
    TestPackage('colorama', ['testInitDoesntWrapOnEmulatedWindows', 'testInitDoesntWrapOnNonWindows']),
    TestPackage('Flask', [
        'test_scriptinfo',  # fails if directory contains ':'
        'test_main_module_paths',
        'test_installed_module_paths', #[False]',
        'test_installed_package_paths', #[False]',
        'test_prefix_package_paths',  #[False]',
        'test_egg_installed_paths',
        'test_aborting',
    ]),
    TestPackage('attrs', [
        '*',
        'test_multiple_empty',  # inspect.getsource failed
    ], mod_name='attr'),
    TestPackage('click-spinner'),
    TestPackage('emoji'),
    TestPackage('jsonpointer'),
    TestPackage('xmltodict'),
    TestPackage('jmespath'),
    TestPackage('titlecase'),
    TestPackage('tabulate', ['test_cli']),
    TestPackage('wrapt', ['test_before_and_after_import', 'test_before_import']),  # 'PyOxidizerFinder' object has no attribute 'load_module',
    TestPackage('multipledispatch', ['test_benchmark', 'test_multipledispatch']),
    TestPackage('ordered-set'),
    TestPackage('toml'),
    TestPackage('orderedmultidict'),  # v1.0.1 needs __file__ to supply __version__
    TestPackage('dparse', ['test_update_pipfile']),
    TestPackage('pluggy'),
    TestPackage('userpath', ['*']),  # requires pytest run inside tox
    TestPackage('pyserial'),
    TestPackage('pathspec'),
    TestPackage('pyperclip', ['TestKlipper']),  # KDE service
    TestPackage('rdflib', ['test_module_names']),  # master, unreleased
    TestPackage('ConfigUpdater', version='1.0.1'),
    TestPackage('itsdangerous'),

    # opensuse outdated
    TestPackage('pyxattr'),
    TestPackage('dulwich', [
        '*',
        'test_blackbox', 'GitReceivePackTests', 'test_missing_arg',  # subprocess
    ]),
    TestPackage('yarl'),
    TestPackage('multidict'),
    TestPackage('aiohttp', [
        '*',
        'test_aiohttp_request_coroutine', # [pyloop]
        'test_client_fingerprint.py',  # ssl = pytest.importorskip('ssl'): KeyError: 'ssl'
        'test_warning_checks',  # ValueError: Pytest terminal summary report not found
        'test_testcase_no_app',  # fails if pytest plugin cacheprovider is disabled
        'test_aiohttp_request_ctx_manager_not_found',
        'test_server_close_keepalive_connection', 'test_handle_keepalive_on_closed_connection',  # test_client_functional.py:2741:coroutine 'noop2' was never awaited
        'test_connector', 'test_urldispatch',  # needs refining; also AttributeError: module 'aiohttp' has no attribute '__file__'
        'test_aiohttp_plugin_async_gen_fixture', 'test_aiohttp_plugin_async_fixture',  # not important
    ]),
    TestPackage('future', [
        '*',
        'test_requests',  # halts
        'test_futurize',  # mostly failing, probably sys.executable
        'test_mixed_annotations', 'test_multiple_param_annotations',  # sys.executable
        'test_bad_address',
        'test_future/test_futurize.py', 'test_future/test_libfuturize_fixers.py', 'test_past/test_translation.py', 'test_correct_exit_status',  # lib2to3 disabled
    ], other_mods=['past', 'libfuturize', 'libpasteurize']),  # opensuse outdated
    #'six',  # opensuse outdated
    TestPackage('semver'),  # opensuse outdated
    TestPackage('shellingham'),
    TestPackage('websockets'),  # opensuse outdated
    TestPackage('asn1crypto', [
        'test_load_order',  # test requires asn1crypto.__file__ ; rather than allow for all tests, disable one test,  # opensuse outdated
        'test_extended_date_strftime', 'test_extended_datetime_strftime',  # tz bug
    ]),
    TestPackage('immutables'),  # outdated
    TestPackage('python-stdnum'),  # outdated
    TestPackage('zstd', ['test_version']),  # outdated
    TestPackage('pytz'),  # opensuse outdated  pytz:95: in open_resource  NameError: name '__file__' is not defined
    TestPackage('xxhash'),  # outdated
    TestPackage('SQLAlchemy', [
        '*',
        'aaa_profiling',  # unnecessary and slow
        # should be QueryTest_sqlite+pysqlite_3_30_1.test_order_by_nulls :
        'QueryTest_sqlite',  # AssertionError: Unexpected success for 'test_order_by_nulls' (not postgresql and not oracle and not firebird)
        'test_column_property_select',  # sqlite3.OperationalError: misuse of aggregate: max()
        'ComponentReflectionTest_sqlite',  # ComponentReflectionTest_sqlite+pysqlite_3_30_1.test_deprecated_get_primary_keys
        'test_deprecated_flags',  # AttributeError: 'object' object has no attribute '_sa_instance_state'
    ]),  # outdated
    TestPackage('graphviz'),  # outdated
    TestPackage('python-slugify'),  # outdated

    # green; no version
    TestPackage('repoze.lru', version='0.7'),
    TestPackage('zope.interface', version='4.6.0'),
    TestPackage('zope.event', version='4.4'),
    TestPackage('zope.deprecation', version='4.4.0'),
    TestPackage('persistent', version='4.5.0'),
    TestPackage('zipp', version='0.6.0'),
    TestPackage('wcwidth', version='0.1.7'),
    TestPackage('isodate', version='0.6.0'),
    TestPackage('lark-parser', [
        '*',
        'test_tools', 'TestStandalone', 'TestNearley',  # sys.executable / __file__
    ], mod_name='lark', version='0.7.7'),
    TestPackage('httmock', version='1.3.0'),
    TestPackage('backports.test.support', [
        'test_assert_python_failure', 'test_assert_python_ok_raises',  # cli
    ], version='0.1.1'),
    TestPackage('click-aliases', version='1.0.1'),
    TestPackage('blindspin', version='2.0.1'),
    TestPackage('class-proxy', version='1.1.0'),
    # test collection needs help
    TestPackage('pytimeparse'),  # passes if I do `ln -s testtimeparse.py test_timeparse.py`
    TestPackage('cChardet'),  # opensuse no have  `mv test.py test_cChardet.py`
    TestPackage('click'),  # ln -s Click-7.0 click-7.0
    TestPackage('sortedcontainers'),  # ln -s python-sortedcontainers-2.1.0 sortedcontainers-2.1.0
    TestPackage('billiard', ['integration']),
    TestPackage('precis-i18n', [
        'test_ietf_vectors.py',  # collection error
        'test_derived_props_files',  # No such file or directory: '.../test/iana-precis-tables-6.3.0.csv'
        'test_idempotent.py',  # hangs
    ]),  # ln -s precis_i18n-1.0.0 precis-i18n-1.0.0
    TestPackage('typed-ast'),  # ln -s typed_ast-1.4.0 typed-ast-1.4.0
    TestPackage('text-unidecode', version='1.3'),  # ln -s test_unidecode.py test_text_unidecode.py

    # no tests
    #TestPackage('certstream', ['*'], version='1.10'),  # https://github.com/CaliDog/certstream-python/issues/29
    #TestPackage('click-completion', ['*']),  # outdated
    #TestPackage('mulpyplexer', ['*'], version='0.08'),
    #TestPackage('click-help-colors', ['*'], version='0.6'),  # has tests in master, but incompatible with 0.6
    #TestPackage('hashID', ['*'], mod_name='hashid'),  # no tests, but broken https://github.com/psypanda/hashID/issues/47
    #TestPackage('stdlib-list', ['*']),
    #TestPackage('termcolor', ['*']),

    # substantial failures; pytz
    TestPackage('Pygments', [
        'test_cmdline',
        'testCanRecognizeAndGuessExampleFiles', 'testApplicationCalendarXml', # fails because MarkupSafe distribution isnt provided by PyOxidizer
        'testColonInComment',  # one failure testColonInComment , yaml bug
        'testEnhancedFor',  # java
        'testBrokenUnquotedString',  # praat
    ]),
    TestPackage('lz4', [
        '*',
        'test_roundtrip_1',  # concerning - should be isolated with further at least test_roundtrip_1[data1-4-True-True-True-0-store_size0]),  # outdated
    ]),
    TestPackage('python-whois', [
        'test_ipv4', 'test_ipv6',  # bugs
        'test_simple_ascii_domain',  # flaky
        'test_il_parse',  # test_il_parse might be upstream error?
    ], version='0.7.2'),  # outdated __file__ ; very weird use of os.getcwd()
    TestPackage('networkx'),  # outdated ; hack needs polishing
    TestPackage('python-dateutil', [
        'testAmbiguousNegativeUTCOffset', 'testAmbiguousPositiveUTCOffset', 'ZoneInfoGettzTest',  # tz problems
        'testPickleZoneFileGettz', 'testPickleZoneFileGettz',
        'test_parse_unambiguous_nonexistent_local', 'test_tzlocal_parse_fold',
        'TzLocalNixTest',
        'test_tzlocal_utc_equal', 'test_tzlocal_offset_equal',
    ]),  # outdated , serious tz issues
    TestPackage('plumbum', [
        'test_sudo', 'test_remote', 'test_copy_move_delete',
        'test_slow', 'test_append',  # incompatible with pytest capture
        'test_mkdir_mode', 'test_env', 'test_local', 'test_iter_lines_error', 'test_atomic_file2', 'test_pid_file', 'test_atomic_counter', 'test_connection',  # sys.executable
        'test_home', 'test_nohup',
    ]),
    TestPackage('pyrsistent', other_mods=['_pyrsistent_version', 'pvectorc'], version='0.15.4'),  # TODO: get version?

    # late additions
    TestPackage('soupsieve', ['*']),  # File "soupsieve.util", line 9, in <module>: NameError: name '__file__' is not defined
    TestPackage('waitress', [
        'test_functional.py',  # hangs
        'TestAPI_UseIPv4Sockets', 'TestAPI_UseIPv6Sockets',
        'TestAPI_UseUnixSockets',
    ], version='1.3.1'),
    TestPackage('WebOb', version='1.8.5'),
    TestPackage('websocket-client', mod_name='websocket'),
    TestPackage('WebTest', ['*'], mod_name='webtest'),  # __file__
    TestPackage('xmlschema', ['*']),  # __file__
    TestPackage('yaspin', ['*']),  # __file__
    TestPackage('netaddr', ['*']),  # __file__
    TestPackage('more-itertools', ['SetPartitionsTests'], version='7.2.0'),
    TestPackage('packaging', [
        '*',
        'test_invalid_url', 'test_parseexception_error_msg',  # pytest5 incompatibility
        'test_cpython_abi_py3', 'test_cpython_abi_py2', 'test_cpython_tags', 'test_sys_tags_on_mac_cpython', 'test_sys_tags_on_windows_cpython', 'test_sys_tags_linux_cpython',  # AttributeError: module 'packaging.tags' has no attribute '_cpython_abi'
    ]),
    TestPackage('stdio-mgr', [
        'test_catch_warnings', 'test_capture_stderr_warn',  # pytest arg incompat
    ]),

    TestPackage('bottle', ['*']),  # NameError("name '__file__' is not defined")}
    TestPackage('distro', [
        'TestCli',
        'TestLSBRelease',
        'TestSpecialRelease',
        'TestOverall',
        'TestGetAttr',
        'TestInfo',
    ]),  #  ln -s distro-1.4.0 distro-20190617
    TestPackage('docutils', ['*']),  # test collection problem
    TestPackage('elementpath', [
        'test_schema_proxy.py',  # xmlschema.codepoints:562: in build_unicode_categories: NameError: name '__file__' is not defined
    ]),
    TestPackage('pycares', [
        'test_custom_resolvconf', 'test_getnameinfo', 'test_idna_encoding',  # not investigated
        'test_idna_encoding_query_a', 'test_query_a_bad', 'test_query_timeout',
        'test_query_txt_multiple_chunked', 'test_result_not_ascii',
        'test_query_any', 'test_query_mx', 'test_query_ns',
    ], other_mods=['_cares']),
    TestPackage('beautifulsoup4', ['*'], mod_name='bs4'),  # NameError("name '__file__' is not defined")}
    TestPackage('cmd2', ['*']),  # AttributeError("module 'docutils.parsers.rst.states' has no attribute '__file__'")}
    TestPackage('click-didyoumean', ['*']),  # all broken, not investigated

]

# psutil expects TRAVIS to signal deactivating unstable tests
os.environ['TRAVIS'] = '1'

package_names = []
for package in packages:
    if isinstance(package, TestPackage):
       package_names.append(package.pypi_name)

namespace_packages = {package.pypi_name.split('.')[0] for package in packages if isinstance(package, TestPackage) and '.' in package.pypi_name}

#print(namespace_packages)

# Create requirements file
#package_names = sorted(package_names)
#for name in package_names:
#    print(str(name))
#sys.exit(1)


# conflicks wiht './test.py'

h = import_hooks.add_relocated_external_file_dunder(
    cpython_root, 'backports.test', 'backports')

import backports.test.support
backports.test.__file__
sys.modules['test'] = backports.test
sys.modules['test.support'] = backports.test.support

# TODO: add a hook system to setup test.support only
# for specific packages
#sys_modules_pre = set(sys.modules.copy())
run_tests([regex_package], quit_early=quit_early)

# todo evict all new modules after each job
#sys_modules_post = set(sys.modules.copy())
#print('new mods', sorted(sys_modules_post - sys_modules_pre))

import_hooks.unregister_import_hook(h)

remove_test_modules()
run_tests(packages, quit_early=quit_early)

packages.append(regex_package)

"""
for package in packages:
    mod = None
    if not package._mod_is_default:
        mod_name = package.mod_name
    else:
        mod_name = package.pypi_name
    try:
        mod = aggressive_import(mod_name)
    except Exception as e:
        print("aggressive_import {} failed: {!r}".format(package.pypi_name, e))
        test_results[package] = 1
        continue
    if package._mod_is_default:
        print("updating {} mod_name to {}".format(package.pypi_name, mod.__name__))
        package.mod_name = mod.__name__
    test_results[package] = 0
"""


_pyox_packages = package_versions(_pyox_modules, standard_lib=False, namespace_packages=namespace_packages)

assert 'repoze.lru' in _pyox_packages


print('_pyox_packages:')
pprint(_pyox_packages)

untested = []

for mod, info in _pyox_packages.items():
    for package in packages:
        if mod in package:
            # print('found {!r} in {!r}'.format(mod, package))
            if package not in test_results:
                if info.get('err'):
                    print(f'listed {mod} wasnt imported: {info["err"]}')
                elif not info.get('ver'):
                    print(f'listed & unversioned package {mod} wasnt tested:\n  {info}')
                else:
                    print(f'listed package {mod} wasnt tested:\n  {info}')
                untested.append(package)
            break
    else:
        if not info.get('ver'):
            print(f'unlisted & unversioned package {mod} wasnt tested:\n  {info}')
        else:
            print(f'unlisted package {mod} wasnt tested:\n  {info}')
        untested.append(TestPackage(mod))

for mod in sorted(_pyox_modules):
    if _is_std_lib(mod, cpython_root):
        continue
    for package in packages:
        if mod in package:
            break
    else:
        for package in untested:
            if mod in package:
                break
        else:
            untested.append(TestPackage(mod))

for package in untested:
    print(f'{package} not known')
if not untested:
    print('All packages tested')

test_dependencies = package_versions(standard_lib=False,
                                     namespace_packages=namespace_packages,
                                     exclude=_pyox_modules)

print('Test dependencies:')
pprint(test_dependencies)

sys.exit(not untested)
