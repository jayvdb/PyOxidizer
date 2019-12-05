from pprint import pprint
from importlib import import_module

import import_hooks

# , '-pno:flaky'
base_pytest_args = [
    '--continue-on-collection-errors', '-c', '/dev/null', '-rs', '--disable-pytest-warnings', '-pno:xdoctest', #['-v',]
    # Breaks --ignore https://github.com/bitprophet/pytest-relaxed/issues/8
    '-pno:relaxed',

    #'-pno:requests-mock', '-pno:hypothesis', '-pno:timeout', '-pno:mock',
    # '-pno:xonsh',
    #'-pno:aspectlib',    '-pno:betamax',    '-pno:case',    '-pno:doctestplus',    '-pno:instafail',    '-pno:disable-plugin',    '-pno:pypi',
    #'-pno:flaky',    '-pno:django-webtest',    '-pno:celery',    '-pno:pylama',    '-pno:pyfakefs',    '-pno:attrib',    '-pno:cov',
    #'-pno:testinfra',    '-pno:spec',    '-pno:profiling',    '-pno:reorder',    '-pno:django',    '-pno:httpbin',    '-pno:forked',
    #'-pno:xdist',
    #'-pno:httpserver',
    #'-pno:asyncio',
    #'-pno:expect',
    #'-pno:localserver',
    #'-pno:xprocess',
]
base_pytest_args.append('--maxfail=10')

run_all = False
quit_early = True

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
    'celery', 'celery.contrib.pytest', 'pytest_xprocess',
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
f = import_hooks.add_empty_load(['networkx.algorithms.tree.recognition'])
#print(f)
import_hooks.add_junk_file_dunder([
    'distorm3',
    'pluggy',
    'coverage.html', 'coverage.control', 'pycparser.c_lexer', 'pycparser.c_parser',
    'httplib2', 'httplib2.certs',
    'ruamel.yaml.main',
    'tqdm._version',
    'networkx.release', 'networkx.generators.atlas',
    'plumbum',
    'botocore', 'botocore.httpsession',
])

"""
import networkx
import_hooks.unregister_import_hook(f)
import sys
del sys.modules['networkx.algorithms.tree.recognition']
import networkx.algorithms.tree.recognition
print(networkx.algorithms.tree.recognition.__spec__)

import_hooks.add_junk_file_dunder([
    'hashid',
], is_module=True)
"""

import_hooks.redirect_get_data_resources_open_binary(['pytz', 'jsonschema', 'text_unidecode', 'pyx'])
import_hooks.redirect_get_data_resources_open_binary(['dateutil.zoneinfo', 'jsonrpcclient.parse'], is_module=True)
import_hooks.overload_open(['lark.load_grammar', 'lark.tools.standalone'], is_module=True)
import_hooks.overload_open(['pycountry', 'pycountry.db', 'stdlib_list.base'])

# doesnt work:
#import_hooks.redirect_get_data_resources_open_binary(['yaspin'], is_module=True)


import_hooks.add_after_import_hook(
    ['certifi.core'],
    import_hooks.certifi_where_hack,
)

#import certifi.core
#certifi.core.where()
#open(certifi.core.where())

import os

import sys

pyox_finder = None
assert sys.oxidized
pyox_finder = sys.meta_path[0]
_pyox_modules = list(pyox_finder.package_list())

import os.path


dist_root = './build/target/x86_64-unknown-linux-gnu/debug/pyoxidizer/python.608871543e6d/python/install'
dist_root = os.path.abspath(dist_root)
cpython_root = dist_root + '/lib/python3.7/'

os.environ['_PYTHON_PROJECT_BASE'] = dist_root
sys._home = dist_root

"""
print('sys.config', sys.prefix)
print('sys.config', sys.prefix)
print('Importing sysconfig')
import sysconfig
print('_CONFIG_VARS', sysconfig._CONFIG_VARS)
print('_PREFIX', sysconfig._PREFIX)
print('_EXEC_PREFIX', sysconfig._EXEC_PREFIX)
print('_BASE_PREFIX', sysconfig._BASE_PREFIX)

pprint(sysconfig.get_paths())
#pprint(sysconfig.get_config_vars())
#print(sysconfig.get_config_h_filename())

#print(sysconfig.get_path('platinclude'))
print()
from distutils.sysconfig import get_python_lib  # used to determine stdlib

print(get_python_lib())
print(get_python_lib(standard_lib=True))
print(cpython_root)

#sys.exit(1)

print('Importing pytest ...')
import pytest
print('Finished importing pytest!!')
import importlib
"""



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

    if not version:
        try:
            data = importlib.resources.open_binary(name, 'VERSION').read()
            return data.decode('utf-8').strip()
        except Exception as e:
            if verbose:
                print('_find_version({}): no file VERSION failed: {!r}'.format(name, e))

    if not version:
        try:
            v_mod = __import__(mod.__name__ + '.version', mod.__name__)
            if verbose:
                print('imported {!r}'.format(v_mod))
            v_mod = v_mod.version
            if verbose:
                print('found version {!r}'.format(v_mod))
            version = v_mod.version
            if verbose:
                print('found version {!r}'.format(version))
        except ImportError as e:
            if verbose:
                print('_find_version({}): {!r}'.format(name, e))

    if not version:
        try:  # pipx
            v_mod = __import__(mod.__name__ + '.main', fromlist=['main'])
            if verbose:
                print('imported {!r}'.format(v_mod))
            version = v_mod.__version__
            if verbose:
                print('found version {!r}'.format(v_mod))
        except ImportError as e:
            if verbose:
                print('_find_version({}): {!r}'.format(name, e))

    if not version:
        if verbose:
            print('version not found for {mod}')
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

def _find_tests_under(base, mod_name):
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
    elif os.path.isdir(base + 'test/'):
        return 'test/'
    elif os.path.isdir(base + '_test/'):  # ruamel.yaml
        return '_test/'
    elif os.path.isdir(base + 'testing/'):
        return 'testing/'
    elif os.path.isdir(base + 'ast3/tests/'):  # typed-ast
        return 'ast3/tests/'
    elif os.path.isdir(base + 't/'):  # vine
        if os.path.exists(base + 't/integration/tests/test_multiprocessing.py'):
            return 't/unit/'  # billiard ^ is py2 only
        return 't/'
    elif os.path.exists(base + 'test.py'):
        return 'test.py'

_platbase = '/usr/lib64/python3.7/lib-dynload/'
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
    return (os.path.isdir(std_lib_dir + name)
            or os.path.exists(std_lib_dir + name + '.py')
            or os.path.exists(_platbase + name + '.cpython-37m-x86_64-linux-gnu.so')  # TODO: use plat extension
            )


def package_versions(modules=None, builtins=False, standard_lib=None, exclude_imported=False,
                     std_lib_dir=None, verbose=False):
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

    builtin_packages = {name.split('.')[0] for name in root_packages
                        if name in sys.builtin_module_names
                        or '_' + name in sys.builtin_module_names}

    # Improve performance by removing builtins from the list if possible.
    if builtins is False:
        root_packages = list(root_packages - builtin_packages)

    #print('root_packages')
    #pprint(sorted(root_packages))

    std_lib_packages = []

    paths = {}
    data = {}

    for name in sorted(root_packages):
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
            package = import_module(name)  # TODO: aggressive import? and version
        except Exception as e:
            if verbose:
                print('import_module({}) failed: {!r}'.format(name, e))
            info['err'] = e
            data[name] = info
            continue

        info['package'] = package

        if '__file__' in package.__dict__:
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
            assert path not in paths, 'Path {} of the package is in defined paths {}'.format(path, paths)
            paths[path] = name
        else:
            if _is_std_lib(name, std_lib_dir):
                std_lib_packages.append(name)
                if standard_lib is False:
                    continue
                info['type'] = 'standard libary'

        if name.startswith('unicodedata'):  # also includes unicodedata2
            info['ver'] = package.unidata_version
        else:
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



def run_pytest(pypi_name=None, mod_name=None, version=None, test_path=None, excludes=[], add_test_file_dunder=False, verbose=False):
    print('run_pytest {} {} {}'.format(pypi_name, mod_name, version))
    if mod_name:
        mod = aggressive_import(mod_name)
    else:
        try:
            mod = aggressive_import(pypi_name)
        #except ImportError as e:
        #    return "Skipping {}: {!r}".format(pypi_name, e)
        except Exception as e:
            if verbose:
                print("aggressive_import {} failed: {!r}".format(pypi_name, e))
            raise e
        mod_name = mod.__name__

    if verbose:
        print('run_pytest {} {} {}'.format(pypi_name, mod_name, version))

    if not version:
        version = _find_version(mod, verbose=verbose)

    if verbose:
        if mod_name != pypi_name:
            print('{}({}) = {}'.format(pypi_name, mod_name, version))
        else:
            print('{} = {}'.format(pypi_name, version))

    found_bases = []
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
    elif verbose:
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
            if verbose:
                print('Adding __file__ for {}'.format(add_test_file_dunder))
            import_hooks.add_external_file_dunder(package_base, [add_test_file_dunder])

    if mod_name == 'tornado':
        import_hooks.add_external_file_dunder(package_base, ['tornado.testing'])

    pytest_args = base_pytest_args.copy()

    if mod_name == 'ruamel.yaml':
        pytest_args += ['--ignore', '_test/lib']

    if excludes:
        ignores = [item for item in excludes if item.endswith('/') or item.endswith('.py')]
        excludes = [item for item in excludes if item not in ignores]
        for item in ignores:
            pytest_args.append('--ignore-glob=*' + item)


    if excludes:
        if len(excludes) == 1:
            pytest_args += ['-k', 'not {}'.format(excludes[0])]
        else:
            pytest_args += ['-k', 'not ({})'.format(' or '.join(excludes))]

    pytest_args.append('./' + test_path)

    os.chdir(package_base)
    print("Running {}-{} tests: {}> pytest {}".format(pypi_name, version, package_base, pytest_args))
    return pytest.main(pytest_args)


def remove_test_modules():
    for name in list(sys.modules.keys()):
        if name.startswith('test_') or name.endswith('_test') or name.startswith('test.') or name.startswith('tests.') or name in ['test', 'tests', 'conftest']:
           del sys.modules[name]

skip_completed = [
    # should be patched!?  but green with one exclusion
    'toolz', 'cytoolz',

    # green
    'simplejson', 'MarkupSafe', 'idna', 'yarl', 'multidict', 'pyOpenSSL', 'msgpack',
    'wheel',
    'aiodns', 'dnspython',
    'ptyprocess',
    'rfc3986',
    'vine',
    'kitchen',
    'colorama',
    'Flask',
    'Jinja2',
    {'attr': 'attrs'},  # mod, package
    'texttable',
    'click-spinner',
    'emoji',
    'soupsieve',
    'jsonpointer',
    'dulwich',
    'xmltodict',
    'jmespath',
    'titlecase',
    'tabulate',
    'pyxattr',
    'wrapt',
    'multipledispatch',
    'pyasn1',
    'ordered-set',
    'toml',
    'orderedmultidict',  # v1.0.1 needs __file__ to supply __version__
    'dparse',
    'click-didyoumean',
    'cached-property',
    'pluggy',
    'userpath',
    'pyserial',
    'pathspec',
    'pyperclip',
    'bcrypt',  # pep 517
    'rdflib',  # master, unreleased
    'PyNaCl',
    'ConfigUpdater',
    'itsdangerous',

    'aiohttp',  # opensuse outdated
    'future',  # opensuse outdated
    'six',  # opensuse outdated
    'semver',  # opensuse outdated
    'shellingham',
    'websockets',  # opensuse outdated
    'asn1crypto',  # opensuse outdated
    'decorator',  # ??
    'immutables',  # outdated
    'python-stdnum',  # outdated
    'zstd',  # outdated
    'pytz',  # opensuse outdated  pytz:95: in open_resource  NameError: name '__file__' is not defined
    'regex',  # opensuse outdated; depends on `test.support`
    'xxhash',  # outdated
    'SQLAlchemy',  # outdated
    'graphviz',  # outdated
    'python-slugify',  # outdated

    # green; no version
    ('repoze.lru', '0.7'),
    ('zope.interface', '4.6.0'),
    ('zope.event', '4.4'),
    ('zope.deprecation', '4.4.0'),
    ('persistent', '4.5.0'),
    ('zipp', '0.6.0'),
    ('wcwidth', '0.1.7'),
    ('isodate', '0.6.0'),
    {'lark': ('lark-parser', '0.7.7')},
    ('httmock', '1.3.0'),
    ('backports.test.support', '0.1.1'),
    ('click-aliases', '1.0.1'),
    ('blindspin', '2.0.1'),
    ('class-proxy', '1.1.0'),

    # test collection needs help
    'pytimeparse',  # passes if I do `ln -s testtimeparse.py test_timeparse.py`
    'cChardet',  # opensuse no have  `mv test.py test_cChardet.py`
    'click',  # ln -s Click-7.0 click-7.0
    'weakrefmethod',  # ln -s test_weakmethod.py test_weakrefmethod.py
    'sortedcontainers',  # ln -s python-sortedcontainers-2.1.0 sortedcontainers-2.1.0
    'billiard',
    'precis-i18n',  # ln -s precis_i18n-1.0.0 precis-i18n-1.0.0
    'filelock',  # ln -s py-filelock-3.0.12 filelock-3.0.12
    'typed-ast',  # ln -s typed_ast-1.4.0 typed-ast-1.4.0
    ('text-unidecode', '1.3'),  # ln -s test_unidecode.py test_text_unidecode.py

    # no tests
    ('certstream', '1.10'),  # https://github.com/CaliDog/certstream-python/issues/29
    'click-completion',  # outdated
    ('mulpyplexer', '0.08'),
    ('click-help-colors', '0.6'),  # has tests in master, but incompatible with 0.6
    'hashID',  # no tests, but broken https://github.com/psypanda/hashID/issues/47
    'stdlib-list',
    'termcolor',

    # substantial failures; pytz
    'cryptography',
    'pygments',  # one failure testColonInComment , yaml error
    'requests',
    'lz4',  # outdated
    'ruamel.yaml',  # upstream issue
    ('python-whois', '0.7.2'),  # outdated __file__ ; very weird use of os.getcwd()
    ('pycountry', '18.12.8'),  # exposes LOCALE_DIR, etc which will fail even if internal access is fixed
    'networkx',  # outdated ; hack needs polishing
    'python-dateutil',  # outdated , serious tz issues
    'plumbum',

    # skipping
    'sentry_sdk',  #imports other stuff which breaks stuff
    'raven',  # https://github.com/getsentry/raven-python/issues/1353
    'cssselect',  #depends on lxml
    'psutil',  #need to set TRAVIS
    'cmd2', # https://github.com/python-cmd2/cmd2/issues/802
    'blist', # not py37 compat
    'urllib3', # needs tornado special version? [pytest] section in setup.cfg files is no longer supported, change to [tool:pytest] instead
    'phabricator', #  __file__ & open during exec
    'tldextract', #  __file__ & open during exec
    'vpip', # fails in pip
    'pyglet',  # outdated  ModuleNotFoundError: No module named 'tests.interactive.interactive_test_base'

    'textstat',  # fails due to pyphen
    'vistir',  # fails due to yaspin
    'Mako', # fails due to Babel
    'plotly', # fails due to Babel
    'pint', # fails due to Babel
    's3transfer',  # fails due to boto
    ('vcrpy', '2.0.1'), # needs httpbin; fails in boto

    # unnecessary
    'tlz',  # part of toolz
    'past',  # part of future
    '_pyrsistent_version',  # part of pyrsistent
    'ldapurl',  # part of ldap
    'peutils',  # part of pefile
]


#pytest.main(['-v', '-pno:django', '/home/jayvdb/projects/osc/d-l-py/python-mock/mock-2.0.0/mock/tests/__main__.py'])


#import_hooks.overload_open(['lark.load_grammar', 'lark.tools.standalone'], is_module=True)

# needs to be before! during exec
#import_hooks.overload_open(['netaddr.eui.ieee', 'netaddr.ip.iana'], is_module=True)


# dont work: 'phabricator', 'tldextract', 's3transfer'
import_hooks.overload_open(['whois', 'depfinder', 'virtualenv'])

# for tinycss2
#import pathlib
#pathlib._NormalAccessor.open = pathlib._normal_accessor.open = import_hooks._catch_fake_open

# for Pyphen needs os.listdir hacked
import pkg_resources
def fake_resource_filename(package, name):
    return '{}/{}/{}'.format(import_hooks._fake_root, package, name)

pkg_resources.resource_filename = fake_resource_filename

#'gridfs', part of pymongo
#pvectorc is part of pyrsistent
#tornado/speedups

packages = [
    #'netaddr', #  __file__ causes some failures
    #'yaspin',  # __file__ still failing
    #'Pyphen',  # uses os.listdir  https://github.com/Kozea/Pyphen/issues/25
    # 'tinycss2',  # __file__, but uses pathlib, which is impenetrable  https://github.com/Kozea/tinycss2/issues/21

    #'PyX',  # File "pyx.config", line 305, in <module> IndexError: list index out of range.  Suspect that pyox is only using package top level name for package name
    #'Werkzeug',  # lots of errors
    #'botocore',
    'boto',  # depends on botocore
    'boto3',  # depends on botocore  # AttributeError: module 'boto3' has no attribute '__file__'

    #'docker',  # outdated , depends on _bcrypt & nacl._sodium ; significant failures
    #{'compose': 'docker-compose'},
    #...,

    'pefile',
    ...,


    ('bson', '0.5.8'),
    'tornado',

    'chardet',
    'rcssmin',  # custom test runner run_tests.py

    'greenlet',  # Python.h


    'pyelftools',

    # redo
    'psutil',  #need to set TRAVIS

    # 'nltk',  # depends on all of its data

    # 'jsonschema',  # File "jsonschema._utils", line 58, in load_schema AttributeError: 'NoneType' object has no attribute 'decode'
    'ZConfig',  # version problem 3.0 vs 3.5.0

    'netmiko',
    'paramiko',
    'distro',
    ('funcparserlib', '0.3.6'),
    'ldap',
    'mockito',
    ('monotonic', '1.5'),
    'py',
    'lml',
    'logutils',
    ('rainbow_logging_handler', '2.2.2'),
    ('case-conversion', '2.1.0'),
    #'ropgadget', depends on capstone  https://github.com/aquynh/capstone/blob/master/bindings/python/capstone/__init__.py
    #'unicorn', File "unicorn.unicorn", line 94, in <module> ImportError: ERROR: fail to load the dynamic library.  https://github.com/unicorn-engine/unicorn/tree/master/bindings/python/unicorn  shared lib only
    #'virtualenv',  lots of errors
    'capstone',
    'flexmock',
    'mocket',
    'tox' # File "tox.constants", line 9, in <module> NameError: name '__file__' is not defined

    'Babel', # fails

    # lots of failures
    #('ndg-httpsclient', '0.5.1'),  # ln -s ndg_httpsclient-0.5.1 ndg-httpsclient-0.5.1


    # 'docutils', 2to3
    # 'redis',  # outdated  needs local redis

    # 'objgraph', different results
    #('multi_key_dict', '2.0.3')  # no tests?
    #'mongodict',  # use github ; relies on pymongo



    # 'tqdm',  # outdated   tests do not run
    # 'pyparsing',  # outdated
    # 'zstandard', compiled bits missing


    #'mock',  # mock.tests is empty

    #'peewee',



    #'pymongo',  # ModuleNotFoundError: No module named 'test.version'
    #'cell',
    'httplib2',

    #'pycparser',
    #'cffi',
    #'Django',

    'Flask-Login', # tests not in opensuse



    ('argcomplete', '1.10.0'),
    # 'distorm3',  # __file__ ;extlib  https://github.com/gdabah/distorm/issues/142
    #{'pwnlib': 'pwntools'},  # https://github.com/Gallopsled/pwntools/issues/1366


    ('jsonrpcclient', '3.3.4'),  # no tests in sdist; get github
    'depfinder',  # fails __file__ even with hack

    ('requests-file', '1.4.3'),
    ('retrying', '1.3.3'),
    # ('shovel', '0.4.0'),  # all failing
    'pipx',

    'importlib-metadata',  # ln -s importlib_metadata-0.17 importlib-metadata-0.17  (0.17 is old..??)
    #'pycares',
    #('typeshed', '0.0.1'),

    #'coverage',
    # 'greenlet',  fatal error: 'Python.h' file not found
    #
    # fails in tests?




    # conflicts with `test`
    #'pygit2',

    # incompatible with pytest
    #'async_timeout',  #  ln -s async-timeout-3.0.1 async_timeout-3.0.1  #fixture 'event_loop' not found
    # 'stdio-mgr',
    # ('bom-open', '0.4'),  # depends on stdio-mgr
    #'xdoctest', uses its own pytest plugin, which cant be found in pyox
    # 'html5lib',  # ERROR collecting test_stream.py; then incompatible with pytest
    #'black',  # opensuse outdated
    # 'PyYAML',
    # 'packaging',

    # other not usable
    # {'clitable': 'textfsm'}, # conflicts with texttable
]
# mock: AttributeError: module 'mock.tests' has no attribute 'testpatch'
test_package_excludes = {
    'pyOpenSSL': ['test_verify_with_time'],  # in TestX509StoreContext

    'wheel': ['test_bdist_wheel', 'test_tagopt'],  # uses sys.executable
    'importlib-metadata': ['test_zip'],
    'simplejson': ['TestTool'],
    'tabulate': ['test_cli'],
    'zstd': ['test_version'],
    'virtualenv': ['test_cmdline'],
    'jsonschema': ['test_cli'],
    'logutils': ['test_hashandlers'],  # unknown
    'billiard': ['integration'],
    'cached-property': ['test_threads_ttl_expiry'],
    'dparse': ['test_update_pipfile'],
    'backports.test.support': ['test_assert_python_failure', 'test_assert_python_ok_raises'],  # cli
    'dulwich': [
        'test_blackbox', 'GitReceivePackTests', 'test_missing_arg',  # subprocess
    ],
    'botocore': [  # supposed to use nose test runner
        'test_client_method_help', 'test_paginator_help_from_client', 'test_waiter_help_documentation',  # help() not included in PyOxidizer
        'test_dynamic_client_error', 'test_s3_special_case_is_before_other_retry', 'test_s3_addressing', 'TestCreateClient', 'TestClientMonitoring', 'TestSessionPartitionFiles', 'TestGenerateDBAuthToken', 'test_internal_endpoint_resolver_is_same_as_deprecated_public', # botocore.session:160: in create_default_resolver botocore.loaders:132: in _wrapper  botocore.exceptions.DataNotFoundError: Unable to load data for: endpoints
        'CloudFrontWaitersTest',  # botocore.exceptions.DataNotFoundError: Unable to load data for: cloudfront
        'TestGenerateDocs', 'TestClientDocumenter', 'test_example', 'test_method', 'docs',  # botocore.exceptions.DataNotFoundError: Unable to load data for: _retry
        'test_get_response_nonstreaming_ng', 'test_get_response_nonstreaming_ok', 'test_get_response_streaming_ng', 'test_get_response_streaming_ok', 'TestGenerateUrl',  'TestGeneratePresignedPost', # session.get_service_model('s3') botocore.exceptions.UnknownServiceError: Unknown service: 's3'. Valid service names are:
    ],
    'pyelftools': ['run_examples_test'],
    'pyperclip': ['TestKlipper'],  # KDE service
    'Werkzeug': ['test_no_memory_leak_from_Rule_builder', 'test_find_modules'],
    'python-dateutil': [
        'testAmbiguousNegativeUTCOffset', 'testAmbiguousPositiveUTCOffset', 'ZoneInfoGettzTest',  # tz problems
        'testPickleZoneFileGettz', 'testPickleZoneFileGettz',
    ],
    'plumbum': [
        'test_sudo', 'test_remote', 'test_copy_move_delete',
        'test_slow', 'test_append',  # incompatible with pytest capture
        'test_mkdir_mode', 'test_env', 'test_local', 'test_iter_lines_error', 'test_atomic_file2', 'test_pid_file', 'test_atomic_counter', 'test_connection',  # sys.executable
    ],
    'flexmock': [
        'test_flexmock_ordered_works_with_same_args',
        'test_flexmock_ordered_works_with_same_args_after_default_stub',
        'test_flexmock_preserves_stubbed_class_methods_between_tests',
        'test_flexmock_preserves_stubbed_object_methods_between_tests',
    ],  # concerning
    'multipledispatch': ['test_benchmark', 'test_multipledispatch'],
    'colorama': ['testInitDoesntWrapOnEmulatedWindows', 'testInitDoesntWrapOnNonWindows'],
    'asn1crypto': ['test_load_order'],  # test requires asn1crypto.__file__ ; rather than allow for all tests, disable one test
    'Jinja2': ['TestModuleLoader'],
    'cryptography': [
        'test_vector_version',  # ignore mismatch of cryptography master vs vectors released
        'test_osrandom_engine_is_default',  # uses python -c
        'TestAssertNoMemoryLeaks',  # test_openssl_memleak is skipped on openSUSE
        'TestEd25519Certificate', 'TestSubjectKeyIdentifierExtension', 'test_load_pem_cert', # missing files in vectors
        'test_aware_not_valid_after', 'test_aware_not_valid_before', 'test_aware_last_update', 'test_aware_next_update', 'test_aware_revocation_date',  #pytz problems
    ],
    'wrapt': ['test_before_and_after_import', 'test_before_import'],  # 'PyOxidizerFinder' object has no attribute 'load_module'
    'rdflib': ['test_module_names'],
    'pygments': [
		'test_cmdline',
		'testCanRecognizeAndGuessExampleFiles', 'testApplicationCalendarXml', # fails because MarkupSafe distribution isnt provided by PyOxidizer
		'testColonInComment',  # Yaml bug
    ],
    'SQLAlchemy': [
        'aaa_profiling',  # unnecessary and slow
        # should be QueryTest_sqlite+pysqlite_3_30_1.test_order_by_nulls :
        'QueryTest_sqlite',  # AssertionError: Unexpected success for 'test_order_by_nulls' (not postgresql and not oracle and not firebird)
        'test_column_property_select',  # sqlite3.OperationalError: misuse of aggregate: max()
    ],
    'regex': [
        'test_main',
        'test_hg_bugs',  # _pickle.PicklingError: Can't pickle <built-in function compile>: import of module '_regex' failed
    ],
    'aiohttp': [
        'test_aiohttp_request_coroutine', # [pyloop]
        'test_aiohttp_request_ctx_manager_not_found',
        'test_server_close_keepalive_connection', 'test_handle_keepalive_on_closed_connection',  # test_client_functional.py:2741:coroutine 'noop2' was never awaited
        'test_connector', 'test_urldispatch',  # needs refining; also AttributeError: module 'aiohttp' has no attribute '__file__'
        'test_aiohttp_plugin_async_gen_fixture',  # not important
    ],
    'pyOpenSSL': ['test_verify_with_time'],  # in TestX509StoreContext
    'tornado': ['AutoreloadTest'],
    'future': [
        'test_requests',  # halts
        'test_futurize',  # mostly failing, probably sys.executable
        'test_mixed_annotations', 'test_multiple_param_annotations',  # sys.executable
    ],
    'Flask': [
        'test_scriptinfo',  # fails if directory contains ':'
        'test_main_module_paths',
        'test_installed_module_paths', #[False]',
        'test_installed_package_paths', #[False]',
        'test_prefix_package_paths',  #[False]',
        'test_egg_installed_paths',
    ],
    'python-whois': [
        'test_ipv6',
        'test_simple_ascii_domain',  # flaky
        'test_il_parse',  # test_il_parse might be upstream error?
    ],
    'pycountry': [
        'test_subdivisions_directly_accessible',  # 4844 vs 4836
        'test_locales',  # fails in gettext
    ],
    # patched!
    'toolz': ['test_tlz'],
    'cytoolz': ['test_tlz'],
    'lz4': ['test_roundtrip_1'],  # concerning - should be isolated with further at least test_roundtrip_1[data1-4-True-True-True-0-store_size0]
    'lark': ['test_tools', 'TestStandalone', 'TestNearley'],
}

test_results = {}



class TestPackage:
    def __init__(self, name, test_ignores=None, pypi_name=None, mod_name=None, version=None, other_mods=None):
        self.pypi_name = pypi_name or name
        self.mod_name = mod_name or name.replace('-', '_')
        self._mods = [self.mod_name] + (other_mods or [])
        self.version = version
        self.test_ignores = test_ignores

    def __str__(self):
        return self.mod_name

    def __eq__(self, other):
        if isinstance(other, str):
            return other in self._mods
        return super().__eq__(other)

    def __contains__(self, item):
        if item in self._mods:
            return True
        for mod in self._mods:
            if item.startswith(mod + '.'):
                return True
        return False

    def __hash__(self):
        return self._mods


def run_tests(packages, skip={}, quit_early=False):
    for package in packages:
        print('looking at {}'.format(package))
        if package == ...:
            test_results[package] = 'break!'
            break

        mod_name, version, excludes = None, None, None
        if isinstance(package, TestPackage):
            mod_name = package.mod_name 
            excludes = package.test_ignores
            version = package.version

            # Overwrites variable with str
            package = package.pypi_name

        elif isinstance(package, dict):
            mod_name, package = next(iter(package.items()))

        if isinstance(package, tuple):
            # Overwrites variable with str
            package, version = package


        if package in no_load_packages or package.lower() in no_load_packages:
            test_results[package] = 'load avoided'
            continue

        if package in skip or package.lower() in skip:
            continue

        if excludes is None:
            excludes = test_package_excludes.get(package)

        if excludes and excludes[0] == '*':
            rv = 0
        else:
            try:
                rv = run_pytest(package, mod_name, version, excludes=excludes)
            except BaseException as e:
                if quit_early:
                    raise
                rv = e
        test_results[package] = rv

        if rv and quit_early:
            if isinstance(rv, Exception):
                raise rv
            sys.exit(rv)

        # Avoid clashes in test module names, like test_pickle in multidict and yarl
        # which causes pytest to fail
        remove_test_modules()

    pprint(test_results)

# Needed for test.support.__file__

import_hooks.add_external_cpython_test_file_dunder(cpython_root, support_only=True)

# This module is unusable unless another import hook is created
import_hooks.add_external_file_dunder(cpython_root, ['lib2to3.pygram'])

# black:
import_hooks.add_relocated_external_file_dunder(cpython_root, 'blib2to3.pygram', 'b')

import_hooks.add_file_dunder_during(cpython_root, 'test_future.test_imports_urllib', 'urllib')

import_hooks.add_file_dunder_during(cpython_root, 'greenlet', 'distutils')
import_hooks.add_file_dunder_during(cpython_root, 'setuptools', 'distutils')

import_hooks.add_file_dunder_during(cpython_root, 'hypothesis', 'os')

#import_hooks.add_external_file_dunder( , 'tornado.testing')

import_hooks.add_relocated_external_file_dunder(
    cpython_root, 'future.backports.urllib.request', 'future.backports')

#import_hooks.add_relocated_external_file_dunder(
#    cpython_root, "blist.test.test_support", "blist")
#import blist.test.test_support


packages = [
    TestPackage('psutil', [
        'test_process', 'TestProcessUtils', 'TestScripts', 'TestTerminatedProcessLeaks', 'test_multi_sockets_proc', 'test_memory_leaks', # sys.executable
        'test_pid_exists', 'test_wait_procs', 'test_wait_procs_no_timeout', 'test_proc_environ', # subprocess
        'test_warnings_on_misses', 'test_missing_sin_sout', 'test_no_vmstat_mocked',  # filename issues
        'TestFSAPIs',  # DSO loading
        'test_connections',  # all but one fail
        'test_emulate_use_sysfs', 'test_percent', 'test_cpu_affinity',  # vm problems
        'test_power_plugged',
        # setuptools.dist:585: in _parse_config_files: AttributeError: module 'distutils' has no attribute '__file__'
        'test_cmdline', 'test_name',  # probable bug in how psutil calculates PYTHON_EXE
        'test_sanity_version_check',  # need to disable psutil.tests.reload_module
        'test_cmdline', 'test_pids', 'test_issue_687', # strange
    ]),

    TestPackage('cffi', [
        'TestBitfield', 'test_verify', 'TestDistUtilsCPython',  # loads built extension dynamically
        'TestZIntegration',  # popen
        'cffi0/test_vgen.py', 'cffi0/test_vgen2.py',  # lots of error
        'cffi1/test_parse_c_type.py',  # module 'cffi.cffi_opcode' has no attribute '__file__'
        'test_commontypes', 'test_zdist',  # module 'cffi' has no attribute '__file__'
        'TestNewFFI1',  # __file__
        'test_recompiler', 'embedding',  # __file__
        'cffi1/test_re_python.py',  # AttributeError: module 'distutils' has no attribute '__file__'
    ], other_mods=['_cffi_backend']),

    TestPackage('chardet'),
    TestPackage('six', ['test_lazy']),  # assertion fails due to other packages; not worth isolating
    TestPackage('brotlipy', mod_name='brotli', version='0.7.0', test_ignores=[
        'test_streaming_compression', 'test_streaming_compression_flush',  # they take too long to complete
        'test_compressed_data_with_dictionaries',  # removed functionality in brotli 1.x
    ]),
    TestPackage('urllib3', [
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
    ]),
    TestPackage('certifi', ['*']),  # has no tests
    TestPackage('pip', ['*']),  # completely broken, starting with __file__
    TestPackage('setuptools', ['*'], other_mods=['easy_install', 'pkg_resources']),  # mostly not useful within PyOxidizer, esp without pip, however pkg_resources is very important
    TestPackage('cryptography', [
        'test_vector_version',  # ignore mismatch of cryptography master vs vectors released
        'test_osrandom_engine_is_default',  # uses python -c
        'TestAssertNoMemoryLeaks',  # test_openssl_memleak is skipped on openSUSE
        'TestEd25519Certificate', 'TestSubjectKeyIdentifierExtension', 'test_load_pem_cert', # missing files in vectors
        'test_aware_not_valid_after', 'test_aware_not_valid_before', 'test_aware_last_update', 'test_aware_next_update', 'test_aware_revocation_date',  #pytz problems
    ]),
    TestPackage('requests', [
        'test_errors', # 2/4 "test_errors" fail, which is problematic
        'test_https_warnings',  # this one is problematic
        'TestTimeout',
        'test_proxy_error',
        # https://github.com/psf/requests/pull/5251
        'test_rewind_body_failed_tell', 'test_rewind_body_no_seek', 'test_conflicting_post_params', 'test_proxy_error'  # pytest compatibility
    ]),
    TestPackage('markupsafe'),
    TestPackage('idna'),

    TestPackage('PyYAML', mod_name='yaml', other_mods=['_yaml'], test_ignores=['*']),  # tests incompatible with pytest, and need test DSOs which cant be loaded

    TestPackage('tornado', test_ignores=['*']),  # lots of failures
    TestPackage('test-server', test_ignores=['*']),  # AttributeError: module 'tornado.web' has no attribute 'asynchronous'
    TestPackage('PySocks', mod_name='socks', other_mods=['sockshandler'], test_ignores=['*']),  # requires test_server
]

# psutil expects TRAVIS to signal deactivating unstable tests
os.environ['TRAVIS'] = '1'

run_tests(packages, quit_early=quit_early)

_pyox_packages = package_versions(_pyox_modules, standard_lib=False)
print('_pyox_packages')
pprint(_pyox_packages)

for package in _pyox_packages:
    if package not in packages:
        print(f'package {package} wasnt tested')

untested = []
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
    print(f'mod {package} not tested')

assert not untested

#print(sys.builtin_module_names)
sys.exit(1)
#import httpbin
#sys.exit(1)

#run_tests(packages, skip=skip_completed, quit_early=quit_early)



ignore =  no_load_packages
print('ignore list: {}'.format(ignore))

remainder = sorted([name for name, data in _pyox_packages.items() if name not in ignore and data.get('ver')])

print('packages with versions')
pprint(remainder)

#packages_to_run = [p for p in packages if p.mod_name in remainder]


run_tests(remainder, skip=packages, quit_early=False)

sys.exit(0)

#pytest.main(['-v', '/home/jayvdb/projects/osc/d-l-py/python-cmarkgfm/cmarkgfm-0.4.2/tests'])

#os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'

import sys
#sys.executable = None

# all green

#incompatible with pytest
# runtests.py in project root
#pytest.main(['-v', '/home/jayvdb/projects/osc/d-l-py/python-peewee/peewee-3.11.2/tests'])


# depends on test.support
#pytest.main(['-v', '/home/jayvdb/projects/osc/d-l-py/python-gevent/gevent-1.4.0/src/greentest/3.7'])

# halts running subprocess during collection, twice and then dies without running tests
# try running each separately to find the cause
#pytest.main(['-v', '/home/jayvdb/projects/osc/d-l-py/python-gevent/gevent-1.4.0/src/gevent/tests/', '-k', 'not (test__subprocess or test__monkey_sigchld_3 or test__backdoor)'])

# incompatible with pytest
# needs to be run from in the project root
#pytest.main(['-v', '/home/jayvdb/projects/osc/d-l-py/python-PyYAML/PyYAML-5.1.2/tests/lib3'])
#import test_all
#test_all.main()


# one failure
#pytest.main(['-v', '/home/jayvdb/projects/osc/d-l-py/python-lz4/lz4-2.1.10/tests'])

# imports ok

# cmarkgfm._cmark


# zope.interface._zope_interface_coptimizations.cpython-37m-x86_64-linux-gnu.so ???

# aiohttp._websocket

# tests look related to paths
#pytest.main(['-v', '/home/jayvdb/projects/osc/d-l-py/python-pygit2/pygit2-0.28.2/test'])

# serious errors
#pytest.main(['-v', '/home/jayvdb/projects/osc/d-l-py/python-pycares/pycares-3.0.0/tests/tests.py'])


#pytest.main(['-v', '-pno:django', '-pno:flaky', '/home/jayvdb/projects/osc/d-l-py/python-sentry-sdk/sentry-python-0.13.1/tests'])

# tests need to be built in
#pytest.main(['-v', '/home/jayvdb/projects/osc/d-l-py/python-lxml/lxml-4.4.1/src/lxml/tests'])

# doesnt work like this
#pytest.main(['-v', 'chardet-c-detector.py', 'chardet-c-init-detect-close.py', 'chardet-compatible-basic.py', 'chardet-compatible-incrementally.py', 'chardet-compatible-multiple-files.py'])

#pytest.main(['-v', '/home/jayvdb/projects/python/chardet/src/tests/test.py'])

# __file__
#pytest.main(['-v', '/home/jayvdb/projects/osc/d-l-py/python-pycparser/pycparser-2.19/tests'])
# Python.h
#pytest.main(['-v', '-W', 'ignore::UserWarning', '/home/jayvdb/projects/osc/d-l-py/python-cffi/cffi-1.13.2/c', '/home/jayvdb/projects/osc/d-l-py/python-cffi/cffi-1.13.2/testing'])

# lots and lots of failures
#pytest.main(['-v', '-pno:xdist', '/home/jayvdb/projects/osc/d-l-py/python-coverage/coverage-4.5.4/tests', '-k', 'not test_concurrency'])

# rerun

# needs to be runtests from project root
#pytest.main(['-v', '/home/jayvdb/projects/osc/d-l-py/python-Cython/Cython-0.29.13/tests'])

