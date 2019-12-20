run_all = False
quit_early = False

from pprint import pprint
import os
import os.path
import sys



def _get_build_info():
    build_apps_dir = str(os.path.join('build', 'apps')) + os.path.sep
    assert build_apps_dir in sys.executable
    build_dir, _, suffix = sys.executable.partition(build_apps_dir)
    suffix_parts = suffix.split(os.path.sep)
    assert len(suffix_parts) == 4
    assert suffix_parts[0] == suffix_parts[-1]
    app_name, rust_target_id, build_type = suffix_parts[:-1]
    return build_dir, app_name, rust_target_id, build_type

def _get_dist_root():
    build_dir, app_name, rust_target_id, build_type = _get_build_info()
    dist_root = os.path.join(build_dir, 'target', rust_target_id, build_type,
                             'pyoxidizer', 'python.608871543e6d', 'python', 'install')
    return dist_root

def _get_cpython_stdlib(dist_root):
    if sys.platform == 'nt':
        return os.path.join(dist_root, 'Lib')
    else:
        return os.path.join(dist_root, 'lib', ('python'+sys.version[0:3]))

dist_root = _get_dist_root()
ext_stdlib_root = _get_cpython_stdlib(dist_root)

os.environ['_PYTHON_PROJECT_BASE'] = dist_root
sys._home = dist_root

# This is needed to set base paths needed for sysconfig to provide the
# correct paths, esp Python.h
sys.base_exec_prefix = sys.exec_prefix = sys.base_prefix = sys.prefix = dist_root


from import_hooks import (
    add_import_error,
    add_empty_load,
    add_after_import_hook,
    unregister_import_hook,
)

from external_file_dunder import (
    add_external_file_dunder,
    add_file_dunder_during,
    add_relocated_external_file_dunder,
    add_external_cpython_test_file_dunder,
)

from file_resource_redirect import (
    add_junk_file_dunder,
    redirect_get_data_resources_open_binary,
    overload_open,
    certifi_where_hack,
    _fake_root,
)

from xot import (
    TestPackage,
    run_tests,
    set_package_base_patterns,
    package_versions,
    _is_std_lib,
    remove_test_modules,
)

set_package_base_patterns([
    '/home/jayvdb/projects/osc/home:jayvdb:branches:devel:languages:python/python-{pypi_name}/{pypi_name}-{version}/',
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
])



# This module is unusable unless another import hook is created
add_external_file_dunder(ext_stdlib_root, ['lib2to3.pygram'])

no_load_packages = [
    # setuptools loads lib2to3, which tries to load its grammar file
    #'lib2to3',

    # https://github.com/HypothesisWorks/hypothesis/issues/2196
    # 'hypothesis', 'hypothesis.extra.pytestplugin',

    # urllib3 uses built extension brotli if present
    # however it is needed by httpbin
    # 'brotli',
    # requests uses built extension simplejson if present
    #'simplejson',
    # hypothesis uses django and numpy if present,
    # and those cause built extensions to load
    'django', 'numpy',
    # Other packages which will load built extension
    #'flask',
    #'scandir',
]
add_import_error(no_load_packages)

add_empty_load([
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

add_empty_load(empty_load_packages)

add_junk_file_dunder([
    'pluggy',
    'coverage.html', 'coverage.control',
    'pycparser.c_lexer', 'pycparser.c_parser',
    'ruamel.yaml.main',
    'tqdm._version',
    'networkx.release', 'networkx.generators.atlas',
    'plumbum',
    'botocore', 'botocore.httpsession',
])


add_after_import_hook(
    ['certifi.core'],
    certifi_where_hack,
)

add_empty_load(no_load_packages)
h = add_empty_load(['networkx.algorithms.tree.recognition'])
import networkx
unregister_import_hook(h)

import sys
del sys.modules['networkx.algorithms.tree.recognition']

import networkx.algorithms.tree.recognition
print(networkx.algorithms.tree.recognition.__spec__)

add_junk_file_dunder([
    'hashid',
], is_module=True)


redirect_get_data_resources_open_binary(['pytz', 'jsonschema', 'text_unidecode', 'pyx'])
redirect_get_data_resources_open_binary(['dateutil.zoneinfo', 'jsonrpcclient.parse'], is_module=True)
overload_open(['lark.load_grammar', 'lark.tools.standalone'], is_module=True)
overload_open(['pycountry', 'pycountry.db', 'stdlib_list.base'])

# doesnt work:
#import_hooks.redirect_get_data_resources_open_binary(['yaspin'], is_module=True)

#pytest.main(['-v', '-pno:django', '/home/jayvdb/projects/osc/d-l-py/python-mock/mock-2.0.0/mock/tests/__main__.py'])


# needs to be before! during exec
#import_hooks.overload_open(['netaddr.eui.ieee', 'netaddr.ip.iana'], is_module=True)


# dont work: 'phabricator', 'tldextract', 's3transfer'
overload_open(['whois', 'depfinder', 'virtualenv'])

# for tinycss2
#import pathlib
#pathlib._NormalAccessor.open = pathlib._normal_accessor.open = import_hooks._catch_fake_open

# This module is unusable unless another import hook is created
#import_hooks.add_external_file_dunder(ext_stdlib_root, ['lib2to3.pygram'])

# black:
add_relocated_external_file_dunder(ext_stdlib_root, 'blib2to3.pygram', 'b')

add_file_dunder_during(ext_stdlib_root, 'test_future.test_imports_urllib', 'urllib')
add_file_dunder_during(ext_stdlib_root, 'greenlet', 'distutils')
add_file_dunder_during(ext_stdlib_root, 'hypothesis', 'os')

#import_hooks.add_external_file_dunder( , 'tornado.testing')

#import_hooks.add_relocated_external_file_dunder(
#    ext_stdlib_root, "blist.test.test_support", "blist")
#import blist.test.test_support

assert sys.oxidized
pyox_finder = sys.meta_path[0]
_pyox_modules = list(pyox_finder.package_list())

# pyox_finder.__spec__.__module__ = None



test_results = {}



# for Pyphen needs os.listdir hacked
import pkg_resources
def fake_resource_filename(package, name):
    return '{}/{}/{}'.format(_fake_root, package, name)

pkg_resources.resource_filename = fake_resource_filename


# Needed for test.support.__file__

add_external_cpython_test_file_dunder(ext_stdlib_root, support_only=True)

add_relocated_external_file_dunder(
    ext_stdlib_root, 'future.backports.urllib.request', 'future.backports')


# Needed by psutil test_setup_script
add_file_dunder_during(ext_stdlib_root, 'setuptools', 'distutils')

# needs test.support
regex_package = TestPackage('regex', [
    'test_main',
    'test_hg_bugs',  # _pickle.PicklingError: Can't pickle <built-in function compile>: import of module '_regex' failed
])  # opensuse outdated


packages = [
    TestPackage('pyelftools', [  # uses 'test/' so is good to place early to ensure no cpython `test` problems
        'run_examples_test.py',  # ImportError: cannot import name 'run_exe' from 'utils' (unknown location)
        # probably need to de-import 'utils' loaded from another package test suite
    ]),

    TestPackage('tornado', test_ignores=[
        '*',
        'TestIOStreamWebMixin', 'TestReadWriteMixin', 'TestIOStreamMixin',
        'AutoreloadTest', 'GenCoroutineTest', 'HTTPServerRawTest', 'UnixSocketTest', 'BodyLimitsTest', 'TestIOLoopConfiguration', 'TestIOStream', 'TestIOStreamSSL', 'TestIOStreamSSLContext', 'TestPipeIOStream',
        'LoggingOptionTest',
        'SubprocessTest',
        'simple_httpclient_test',  # a few failures
        'test_error_line_number_extends_sub_error',
    ]),  # lots of failures

    #...,
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

    TestPackage('websocket-client', mod_name='websocket'),
    TestPackage('websockets'),  # opensuse outdated

    TestPackage('setuptools', [  # outdated
    ], other_mods=['easy_install', 'pkg_resources']),  # mostly not useful within PyOxidizer, esp without pip, however pkg_resources is very important
    #TestPackage('html5lib', [
    #    'test_stream.py',
    #    'testdata/',
    #]), # ==1.0.1
    TestPackage('humanize', ['*']), # ==0.4  __file__
    TestPackage('hypothesis', [
        '*',
        'django/', 'numpy/', 'pandas/', 'py2/', 'dpcontracts/',
        'pytest/',
        'py3/test_lookup_py38.py',
        'datetime/test_dateutil_timezones.py',
        'cover/test_settings.py',  # fixture 'testdir' not found
    ]), # ==4.46.1  ln -s hypothesis-hypothesis-python-4.46.1 hypothesis-4.46.1
    TestPackage('python-memcached', [
        'TestMemcache',  # needs running memcached
    ], mod_name='memcache'), # ==1.58
    TestPackage('python-mimeparse'), # ==1.6.0  ln -s mimeparse_test.py python_mimeparse_test.py
    TestPackage('rfc3987'), # ==1.3.8  # use -- doctest
    TestPackage('u-msgpack-python'), # ==2.5.1
    TestPackage('strict-rfc3339', version='0.7'),  # ln -s strict-rfc3339-version-0.7 strict-rfc3339-0.7

    TestPackage('versiontools', [
        'test_cant_import', 'test_not_found',  # minor ImportError string differences
    ]), # ==1.9.1
    TestPackage('tzlocal', [
        'test_fail',  # UserWarning: Can not find any timezone configuration, defaulting to UTC.
    ], version='2.0.0'),  # /usr/lib/python3.7/site-packages/tzlocal/
    TestPackage('padme'),
    TestPackage('webencodings'), # ==0.5.1
    TestPackage('webcolors'), # ==1.8.1
    TestPackage('atomicwrites'), # ==1.3.0
    TestPackage('iso8601', version='0.1.12'),  # /usr/lib/python3.7/site-packages/iso8601/

    TestPackage('bson', version='0.5.8'), #==0.5.8  # "bson.tests", line 8, in <module> NameError: name '__file__' is not defined
    TestPackage('backcall'), #==0.1.0
    TestPackage('blinker'), #==1.4
    TestPackage('colorclass', ['*']), #==2.2.0  has no tests
    TestPackage('docrepr', ['*']), #==0.1.1  has no tests
    TestPackage('python-dotenv', ['test_cli.py', 'test_core.py']), #==0.10.2 depends on unix only `sh`
    TestPackage('fastimport'), # ==0.9.8

    #...,

    TestPackage('PyNaCl', [
        # '*',
        'test_bindings.py', 'test_box.py',  # binary() got an unexpected keyword argument 'average_size'
        'test_wrong_types',  # pytest5 incompatibility
    ], other_mods=['nacl', '_sodium']),

    #...,

    TestPackage('bcrypt', other_mods=['_bcrypt']),  # pep 517

    TestPackage('pyparsing'),
    TestPackage('unicodedata2'),

    TestPackage('ruamel.std.pathlib', ['*']),  # no tests?
    TestPackage('ruamel.yaml', [
        'test_collections_deprecation',
    ], other_mods=['_ruamel_yaml']),  # upstream issue
    TestPackage('psutil', [
        '*',
        'test_process', 'TestProcessUtils', 'TestScripts', 'TestTerminatedProcessLeaks', 'test_multi_sockets_proc', 'test_memory_leaks',  # sys.executable
        'test_pid_exists', 'test_wait_procs', 'test_wait_procs_no_timeout', 'test_proc_environ',  # subprocess
        'test_warnings_on_misses', 'test_missing_sin_sout', 'test_no_vmstat_mocked',  # filename issues
        'TestFSAPIs',  # DSO loading
        'test_connections',  # all but one fail
        'TestSystemVirtualMemory', 'test_emulate_use_sysfs', 'test_percent', 'test_cpu_affinity',  # vm problems
        'test_power_plugged',
        'test_cmdline', 'test_name',  # probable bug in how psutil calculates PYTHON_EXE
        'test_sanity_version_check',  # need to disable psutil.tests.reload_module
        'test_cmdline', 'test_pids', 'test_issue_687', # strange
        'test_unix_socketpair',
        'test_memory_info_ex',   # side effect of -Wignore
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
        'test_disable_warnings',  # side-effect of -Wignore
        'test_render_part', 'test_parse_url', 'test_match_hostname_mismatch', 'test_url_vulnerabilities',
    ]),
    TestPackage('pyOpenSSL', [
        'test_verify_with_time',  # in TestX509StoreContext
        'memdbg.py',  # creates a DSO and fails when importing it
        'test_debug.py',
        'EqualityTestsMixin', 'util.py',  # pytest incompatible structure
        'test_export_text',  # not sure
    ], mod_name='OpenSSL'),
    TestPackage('pycparser', [
        'test_c_generator.py', 'test_c_parser.py',  # inspect.getfile fails
    ], other_mods=['utils']),
    TestPackage('certifi', ['*']),  # has no tests
    TestPackage('pip', ['*']),  # completely broken, starting with __file__
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
        'test_quote_unquote_text',  # hypothesis error due to slowness
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
        'test_iterblobs',  # side-effect of -Wignore
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
    ], mod_name='sqlalchemy'),  # outdated
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
    TestPackage('WebOb', [
        'test_update_behavior_warning',  # side-effect of -Wignore
    ], version='1.8.5'),
    TestPackage('WebTest', ['*'], mod_name='webtest'),  # __file__
    TestPackage('xmlschema', ['*']),  # __file__
    TestPackage('yaspin', ['*']),  # __file__
    TestPackage('netaddr', ['*']),  # __file__
    TestPackage('more-itertools', ['SetPartitionsTests'], version='7.2.0'),
    TestPackage('packaging', [
        '*',
        'test_invalid_url', 'test_parseexception_error_msg',  # pytest5 incompatibility
        'test_cpython_abi_py3', 'test_cpython_abi_py2', 'test_cpython_tags', 'test_sys_tags_on_mac_cpython', 'test_sys_tags_on_windows_cpython', 'test_sys_tags_linux_cpython',  # AttributeError: module 'packaging.tags' has no attribute '_cpython_abi'
        'test_check_glibc_version_warning',  # side-effect of -Wignore
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

h = add_relocated_external_file_dunder(
    ext_stdlib_root, 'backports.test', 'backports')

import backports.test.support
backports.test.__file__
sys.modules['test'] = backports.test
sys.modules['test.support'] = backports.test.support

# TODO: add a hook system to setup test.support only
# for specific packages
#sys_modules_pre = set(sys.modules.copy())
run_tests([regex_package], quit_early=quit_early, no_load_packages=no_load_packages)

# todo evict all new modules after each job
#sys_modules_post = set(sys.modules.copy())
#print('new mods', sorted(sys_modules_post - sys_modules_pre))

unregister_import_hook(h)

remove_test_modules()
test_results = run_tests(packages, quit_early=quit_early)

pprint(test_results)

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
        if package == ...:
            continue
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
    if _is_std_lib(mod, ext_stdlib_root):
        continue
    for package in packages:
        if package == ...:
            continue
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
