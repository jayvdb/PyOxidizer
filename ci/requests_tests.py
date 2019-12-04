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
    '--continue-on-collection-errors', '-c', '/dev/null', '-rs', '--disable-pytest-warnings',
    # Breaks --ignore
    '-pno:xdoctest',
    # Breaks --ignore https://github.com/bitprophet/pytest-relaxed/issues/8
    '-pno:relaxed',
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

import_hooks.add_junk_file_dunder([
    'pluggy',
    'coverage.html', 'coverage.control',
    'pycparser.c_lexer', 'pycparser.c_parser',
])


import_hooks.add_after_import_hook(
    ['certifi.core'],
    import_hooks.certifi_where_hack,
)


assert sys.oxidized
pyox_finder = sys.meta_path[0]
_pyox_modules = list(pyox_finder.package_list())


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
        except (AttributeError, ImportError) as e:
            if verbose:
                print('_find_version({}): {!r}'.format(name, e))

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

    if verbose:
        print('root packages:', sorted(root_packages))

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
            package = importlib.import_module(name)
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

    import pytest

    if mod_name:
        mod = aggressive_import(mod_name)
    else:
        try:
            mod = aggressive_import(pypi_name)
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
    if verbose:
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
        return hash(self.mod_name)


test_results = {}


def run_tests(packages, skip={}, quit_early=False, verbose=False):
    for package in packages:
        if verbose:
            print('looking at {}'.format(package))
        if package == ...:
            test_results[package] = 'break due to `...`!'
            break

        if isinstance(package, TestPackage):
            mod_name = package.mod_name 
            excludes = package.test_ignores
            version = package.version

            pypi_name = package.pypi_name
        else:
            assert isinstance(package, str)
            pypi_name = mod_name = package
            version = excludes = None

        if pypi_name in no_load_packages or pypi_name.lower() in no_load_packages:
            test_results[pypi_name] = 'load avoided'
            continue

        if pypi_name in skip or pypi_name.lower() in skip:
            continue

        if excludes and excludes[0] == '*':
            rv = 0
        else:
            try:
                rv = run_pytest(pypi_name, mod_name, version, excludes=excludes)
            except BaseException as e:
                if quit_early:
                    raise
                rv = e

        # Uses TestPackage if given
        test_results[package] = rv

        if rv and quit_early:
            if isinstance(rv, Exception):
                raise rv
            sys.exit(rv)

        # Avoid clashes in test module names, like test_pickle in multidict and yarl
        # which causes pytest to fail
        remove_test_modules()

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

packages = [
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
        '*',
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
print('_pyox_packages:')
pprint(_pyox_packages)

untested = []

for mod, info in _pyox_packages.items():
    for package in packages:
        if mod in package:
            if package not in test_results:
                print(f'listed package {mod} wasnt tested: {info}')
                untested.append(package)
            break
    else:
        print(f'unlisted package {mod} wasnt tested: {info}')
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

sys.exit(not untested)
