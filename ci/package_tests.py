quit_early = False
skip_slow = True

from pprint import pprint
import os
import os.path
import sys



def _get_build_info():
    build_apps_dir = str(os.path.join('build', 'apps')) + os.path.sep
    assert build_apps_dir in sys.executable
    project_dir, _, suffix = sys.executable.partition(build_apps_dir)
    print(project_dir, _, suffix)
    suffix_parts = suffix.split(os.path.sep)
    assert len(suffix_parts) == 4
    assert suffix_parts[0] == suffix_parts[-1]
    app_name, rust_target_id, build_type = suffix_parts[:-1]
    return project_dir, app_name, rust_target_id, build_type

def _get_dist_root():
    project_dir, app_name, rust_target_id, build_type = _get_build_info()
    print(project_dir, app_name, rust_target_id, build_type)
    dist_root = os.path.join(project_dir, 'build', 'target', rust_target_id, build_type,
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


from distutils.sysconfig import get_python_lib  # used to determine stdlib

print('stdlib', get_python_lib(standard_lib=True))
lib2to3_dir = os.path.join(get_python_lib(standard_lib=True), 'lib2to3')
assert os.path.isdir(lib2to3_dir), '{} does not exist'.format(lib2to3_dir)
#sys.exit(1)

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
    #'pyglet',
    'eventlet',
    'jsonrpcclient.__main__',
    'dns',  # KeyError: 'dns.rdtypes.ANY'
    'tinycss2', 'pyphen', 'phabricator',

    # stdlib problems
    'antigravity',
    'formatter',
    'macpath',
    'webbrowser', # grrrr
    'this',
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
    'pip', 'pip._vendor', 'pip._vendor.pep517.wrappers', 'pip._internal.utils.misc',
])


add_after_import_hook(
    ['certifi.core', 'pip._vendor.certifi.core'],
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
    'soupsieve.util',
], is_module=True)


redirect_get_data_resources_open_binary(['pytz', 'jsonschema', 'text_unidecode', 'pyx'])
redirect_get_data_resources_open_binary(['dateutil.zoneinfo', 'jsonrpcclient.parse'], is_module=True)
overload_open(['lark.load_grammar', 'lark.tools.standalone'], is_module=True)
overload_open(['pycountry', 'pycountry.db', 'stdlib_list.base'])

# doesnt work:
redirect_get_data_resources_open_binary(['yaspin.spinners'], is_module=True)

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
_pyox_modules = sorted(pyox_finder.package_list())

# These should be True
assert 'nacl._sodium' in _pyox_modules
assert '_sodium' not in _pyox_modules

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
    # Important additions
    #TestPackage('vistir'),
    #TestPackage('click-help-colors', version='0.6'),  # has tests in master, but incompatible with 0.6  ModuleNotFoundError("No module named 'click.help'")
    #TestPackage('stdlib-list'),

    TestPackage('soupsieve'),  #  fix upstream: File "soupsieve.util", line 9, in <module>: NameError: name '__file__' is not defined
    TestPackage('beautifulsoup4', [
        'test_html5lib.py', 'test_lxml.py',  # py2 syntax
        'TestWarnings', 'test_custom_builder_class',  # side-effect of disabling warnings
        'test_smart_quote_substitution',
        'test_ascii_in_unicode_out',  # 'unicode' not defined
        'test_extract_multiples_of_same_tag',
        'test_deprecated_member_access',
        'test_copy_preserves_encoding',
        'test_copy_tag_copies_contents',
        'test_prettify_outputs_unicode_by_default',
    ], mod_name='bs4'),  # NameError("name '__file__' is not defined")}
    # ...,
    TestPackage('chardet', pip_cache_file='git+https://github.com/chardet/chardet'),

    TestPackage('pyelftools', [  # uses 'test/' so is good to place early to ensure no cpython `test` problems
        'run_examples_test.py',  # ImportError: cannot import name 'run_exe' from 'utils' (unknown location)
        # probably need to de-import 'utils' loaded from another package test suite
    ]),

    TestPackage('tornado', test_ignores=[
        'TestIOStreamWebMixin', 'TestReadWriteMixin', 'TestIOStreamMixin',
        'AutoreloadTest', 'GenCoroutineTest', 'HTTPServerRawTest', 'UnixSocketTest', 'BodyLimitsTest', 'TestIOLoopConfiguration', 'TestIOStream', 'TestIOStreamSSL', 'TestIOStreamSSLContext', 'TestPipeIOStream',
        'LoggingOptionTest',
        'SubprocessTest',
        'simple_httpclient_test',  # a few failures
        'test_error_line_number_extends_sub_error',
    ]),  # lots of failures

    TestPackage('logutils', ['test_hashandlers', 'RedisQueueTest']),  # unknown
    TestPackage('Flask', [
        'test_scriptinfo',  # fails if directory contains ':'
        'test_main_module_paths',
        'test_installed_module_paths', #[False]',
        'test_installed_package_paths', #[False]',
        'test_prefix_package_paths',  #[False]',
        'test_egg_installed_paths',
        'test_aborting',
    ]),

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

    TestPackage('html5lib', [
        'test_stream.py',
        'testdata/',
    ]), # ==1.0.1
    # TODO: not built in?
    TestPackage('hypothesis', [
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

    TestPackage('backcall'), #==0.1.0
    TestPackage('blinker'), #==1.4
    TestPackage('python-dotenv', ['test_cli.py', 'test_core.py']), #==0.10.2 depends on unix only `sh`
    TestPackage('fastimport'), # ==0.9.8

    TestPackage('imagesize', version='1.1.0'),

    #...,

    TestPackage('PyNaCl', [
        'test_bindings.py', 'test_box.py',  # binary() got an unexpected keyword argument 'average_size'
        'test_wrong_types',  # pytest5 incompatibility
    ], other_mods=['nacl', '_sodium']),

    #...,

    TestPackage('bcrypt', other_mods=['_bcrypt']),  # pep 517

    TestPackage('pyparsing'),
    TestPackage('unicodedata2'),

    TestPackage('ruamel.yaml', [
        'test_collections_deprecation',
    ], other_mods=['_ruamel_yaml']),  # upstream issue
    TestPackage('psutil', [
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
        'test_redirecting_to_bad_url', 'TestGetEnvironProxies', 'test_set_environ',  # recent additions caused by some other package
        # https://github.com/psf/requests/pull/5251
        'test_rewind_body_failed_tell', 'test_rewind_body_no_seek', 'test_conflicting_post_params', 'test_proxy_error'  # pytest compatibility
    ]),
    TestPackage('MarkupSafe'),
    TestPackage('idna'),


    # not listed


    TestPackage('jsonschema', [
        'test_cli.py',
        'test_jsonschema_test_suite.py',  # requires data set
        'test_validators.py',  # ImportError: cannot import name 'RefResolutionError' from 'jsonschema.validators'
        'test_repr',
    ]),
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
    TestPackage('attrs', [
        'test_multiple_empty',  # inspect.getsource failed
    ], mod_name='attr'),
    TestPackage('yaspin'),
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
    TestPackage('pyserial'),
    TestPackage('pathspec'),
    TestPackage('pyperclip', ['TestKlipper']),  # KDE service
    TestPackage('rdflib', ['test_module_names'], pip_cache_file='git+https://github.com/RDFLib/rdflib'),  # master, unreleased
    TestPackage('ConfigUpdater', version='1.0.1'),
    TestPackage('itsdangerous'),

    # opensuse outdated
    TestPackage('pyxattr'),
    TestPackage('dulwich', [
        'test_blackbox', 'GitReceivePackTests', 'test_missing_arg',  # subprocess
        'test_iterblobs',  # side-effect of -Wignore
    ]),
    TestPackage('yarl'),
    TestPackage('multidict'),
    TestPackage('aiohttp', [
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


    # substantial failures; pytz
    TestPackage('Pygments', [
        'test_cmdline',
        'testCanRecognizeAndGuessExampleFiles', 'testApplicationCalendarXml', # fails because MarkupSafe distribution isnt provided by PyOxidizer
        'testColonInComment',  # one failure testColonInComment , yaml bug
        'testEnhancedFor',  # java
        'testBrokenUnquotedString',  # praat
    ]),
    TestPackage('lz4', [
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
    TestPackage('waitress', [
        'test_functional.py',  # hangs
        'TestAPI_UseIPv4Sockets', 'TestAPI_UseIPv6Sockets',
        'TestAPI_UseUnixSockets',
    ], version='1.3.1'),
    TestPackage('WebOb', [
        'test_update_behavior_warning',  # side-effect of -Wignore
    ], version='1.8.5'),
    TestPackage('more-itertools', ['SetPartitionsTests'], version='7.2.0'),
    TestPackage('packaging', [
        'test_invalid_url', 'test_parseexception_error_msg',  # pytest5 incompatibility
        'test_cpython_abi_py3', 'test_cpython_abi_py2', 'test_cpython_tags', 'test_sys_tags_on_mac_cpython', 'test_sys_tags_on_windows_cpython', 'test_sys_tags_linux_cpython',  # AttributeError: module 'packaging.tags' has no attribute '_cpython_abi'
        'test_check_glibc_version_warning',  # side-effect of -Wignore
    ]),
    TestPackage('stdio-mgr', [
        'test_catch_warnings', 'test_capture_stderr_warn',  # pytest arg incompat
    ], pip_cache_file='git+https://github.com/bskinn/stdio-mgr'),

    TestPackage('distro', [
        'TestCli',
        'TestLSBRelease',
        'TestSpecialRelease',
        'TestOverall',
        'TestGetAttr',
        'TestInfo',
    ], version='1.4.0'),  #  Fix upstream, code version says it is `20190617`
    TestPackage('elementpath', [
        'test_schema_proxy.py',  # xmlschema.codepoints:562: in build_unicode_categories: NameError: name '__file__' is not defined
    ]),
    TestPackage('pycares', [
        'test_custom_resolvconf', 'test_getnameinfo', 'test_idna_encoding',  # not investigated
        'test_idna_encoding_query_a', 'test_query_a_bad', 'test_query_timeout',
        'test_query_txt_multiple_chunked', 'test_result_not_ascii',
        'test_query_any', 'test_query_mx', 'test_query_ns',
    ], other_mods=['_cares']),

    TestPackage('pip', [
        'tests/functional/', 'tests/lib/',  # test init problems
        'test_pip_version_check',  # uses pkg_resources looking for pip
        # trimming as per openSUSE
        'network',
        'test_config_file_venv_option',
        'test_build_env_allow_only_one_install',
        'test_build_env_requirements_check',
        'test_build_env_overlay_prefix_has_priority',
        'test_build_env_isolation',
        # color log problems
        'tests/unit/test_base_command.py', 'tests/unit/test_build_env.py', 'tests/unit/test_cache.py',
        # failures
        'test_broken_pipe_in_stderr_flush',
        'test_environment_marker_extras',
        'test_unhashed_deps_on_require_hashes',
        'test_mismatched_versions',
        'TestCallSubprocess',
        'test_virtualenv_no_global',
        # extra failures when pip is tested last
        'test_str_to_display__decode_error',
        'test_skip_invalid_wheel_link',
        'test_format_with_timestamp',
        'test_missing_PATH_env_treated_as_empty_PATH_env',
    ]),
]

untestable = [
    # TODO
    TestPackage('importlib-metadata', ['test_zip']),  # wrong version being installed
    TestPackage('click-didyoumean', ['*']),  # all broken, not investigated

    TestPackage('tqdm', [
        '*',  # Tests are not collecting
    ], version='4.40.2'),
    TestPackage('setuptools', [
        '*',  # Tests are not collecting
    ], other_mods=['easy_install', 'pkg_resources']),  # mostly not useful within PyOxidizer, esp without pip, however pkg_resources is very important
    TestPackage('bson', version='0.5.8'), #==0.5.8  # "bson.tests", line 8, in <module> NameError: name '__file__' is not defined

    # Test runner problems
    TestPackage('userpath', ['*']),  # requires pytest run inside tox
    TestPackage('PyYAML', mod_name='yaml', other_mods=['_yaml'], test_ignores=['*']),  # tests incompatible with pytest, and need test DSOs which cant be loaded
    TestPackage('docutils', ['*']),  # test collection problem, also see cmd2
    TestPackage('rfc3987', ['*']), # Only has doctests, and pytest requires __file__ for loading doctest

    TestPackage('test-server', test_ignores=['*']),  # AttributeError: module 'tornado.web' has no attribute 'asynchronous'
    TestPackage('PySocks', mod_name='socks', other_mods=['sockshandler'], test_ignores=['*']),  # requires test_server

    # __file__ problems
    TestPackage('humanize', ['*']), # ==0.4 humanize.i18n", line 11, in <module>: NameError: name '__file__' is not defined
    TestPackage('WebTest', ['*'], mod_name='webtest'),  # __file__
    TestPackage('xmlschema', ['*']),  # xmlschema.codepoints", line 562, in build_unicode_categories: NameError: name '__file__' is not defined
    TestPackage('netaddr', ['*']),  # __file__
    TestPackage('bottle', ['*']),  # NameError("name '__file__' is not defined")}
    TestPackage('cmd2', ['*']),  # AttributeError("module 'docutils.parsers.rst.states' has no attribute '__file__'")}
    TestPackage('virtualenv', [
        '*',  # ImportError: cannot import name '__file__' from 'virtualenv_support'
        # also 'test_cmdline',
    ], other_mods=['virtualenv_support']),
    TestPackage('Babel', ['*'], mod_name='babel'),  # __file__
    TestPackage('Sphinx', ['*'], mod_name='sphinx'),  # __file__
    TestPackage('alabaster', ['*'], version='0.7.12'),  # todo: remove version and fix version finder
    TestPackage('sphinxcontrib.applehelp', ['*']),  # broken because of Sphinx
    TestPackage('sphinxcontrib.devhelp', ['*']),  # broken because of Sphinx
    TestPackage('sphinxcontrib.htmlhelp', ['*']),  # broken because of Sphinx
    TestPackage('sphinxcontrib.jsmath', ['*']),  # broken because of Sphinx
    TestPackage('sphinxcontrib.qthelp', ['*']),  # broken because of Sphinx
    TestPackage('sphinxcontrib.serializinghtml', ['*']),  # broken because of Sphinx

    # no tests
    TestPackage('ruamel.std.pathlib', ['*']),  # no tests?  Needed by ruamel.yaml
    TestPackage('certifi', ['*']),  # has no tests

    #TestPackage('certstream', ['*'], version='1.10'),  # https://github.com/CaliDog/certstream-python/issues/29
    #TestPackage('click-completion', ['*']),  # outdated
    #TestPackage('mulpyplexer', ['*'], version='0.08'),
    #TestPackage('hashID', ['*'], mod_name='hashid'),  # no tests, but broken https://github.com/psypanda/hashID/issues/47
    #TestPackage('termcolor', ['*']),
    TestPackage('colorclass', ['*']), #==2.2.0  has no tests
    TestPackage('docrepr', ['*']), #==0.1.1  has no tests
    TestPackage('snowballstemmer', ['*'], version='2.0.0'),  # no tests available
]

slow_test_suites = [
    'chardet',
    'tornado',
    'html5lib',
    'PyNaCl',
    'psutil',
    'cffi',
    'urllib3',
    'cryptography',
    'requests',
    'attrs',
    'dulwich',
    'aiohttp',
    'future',
    'SQLAlchemy',
    'lark-parser',
    'lz4',
    'packaging',
    'hypothesis',
]


def parse_wheel_filename(filename):
    """Parse python and platform according to PEP 427 for wheels."""

    stripped_filename = filename.strip(".whl")
    try:
        proj, vers, build, pyvers, abi, platform = stripped_filename.split("-")
    except ValueError:  # probably no build version available
        proj, vers, pyvers, abi, platform = stripped_filename.split("-")
        build = None

    return proj, vers, build, pyvers, abi, platform


def parse_sdist_filename(filename):
    """Parse sdist."""
    if filename.endswith(".zip"):
        stripped_filename = filename[:-4]
    elif filename.endswith(".tar.gz"):
        stripped_filename = filename[:-7]
    elif filename.endswith(".tar.bz2"):
        stripped_filename = filename[:-8]
    elif filename.endswith(".tar.xz"):
        stripped_filename = filename[:-7]

    ext = filename[len(stripped_filename):]

    #assert '-' in stripped_filename, '{} unrecognised: {} '.format(filename, stripped_filename)
    try:
        proj, vers = stripped_filename.rsplit('-', 1)
    except ValueError:
        proj, vers = stripped_filename, None

    return proj, vers, ext


from landinggear.extract_packages import Extractor
import glob

class MyExtractor(Extractor):

    def get_sdist_package_names(self, name):
        return set([
            name,
            name.lower(),
            name.replace('-', '_'),
            name.replace('_', '-'),
            name.title(),
        ])

    def __init__(self, package_dir, packages):
        super().__init__(package_dir)
        self._all = packages

    def _create_package_dir(self):
        if not os.path.exists(self.package_dir):
            self.emit("Creating package dir: %s" % (self.package_dir,))
            os.mkdir(self.package_dir)

    def filter_existing(self):
        self._wanted = []
        self._create_package_dir()
        for package in self._all:
             if package.pip_cache_file: continue
             for package_name in self.get_sdist_package_names(package.pypi_name):
                 package_glob = '{}-{}.*'.format(package_name, package.version)
                 filepath = os.path.join(self.package_dir, package_glob)
                 results = list(glob.glob(filepath))
                 #print(filepath, results)
                 if results:
                     assert len(results) == 1
                     package.pip_cache_file = results[0]
                     break
             if not results:
                  print('{}=={} not found'.format(package.pypi_name, package.version))
                  self._wanted.append(package)

    def iter_caches(self):
        if not self._wanted:
            return []
        for cached_package in super().iter_caches():
            if cached_package.is_package:
                filename = cached_package.package_filename
                if filename.endswith('.whl'):
                    bits = parse_wheel_filename(filename)
                    proj, vers = bits[0], bits[1]
                    ext = '.whl'
                    continue
                else:
                    proj, vers, ext = parse_sdist_filename(filename)
                if not vers:
                    print('Invalid name {} {} {}'.format(cached_package.package_filename, proj, cached_package.filepath))
                    continue
                import distutils.version  # todo: move
                try:
                    verdata = distutils.version.LooseVersion(vers)
                except Exception as e:
                    print('Invalid version {} {} {}: {}'.format(cached_package.package_filename, vers, cached_package.filepath, e))
                try:
                    if not verdata.version[0]:
                        if not verdata.version[1]:
                            if not verdata.version[2]:
                                print('Odd version {} {} {}: {!r}'.format(cached_package.package_filename, vers, cached_package.filepath, verdata))
                except Exception as e:
                    print('Invalid version {} {} {}: {}'.format(cached_package.package_filename, vers, cached_package.filepath, e))
                for package in self._wanted:
                    for name in self.get_sdist_package_names(package.pypi_name):
                         if name == proj:
                            if vers == package.version:
                                print('found {} {}: {}'.format(package.pypi_name, package.version, filename))
                                yield cached_package
                                break
                            else:
                                print('found non-matching {} {}: {}'.format(package.pypi_name, package.version, filename))


extractor = MyExtractor('landinggear-output', packages)
extractor.filter_existing()
print(len(extractor._all), len(extractor._wanted))
extractor.extract_packages()
sys.exit(1)

skip_packages = no_load_packages.copy()
if skip_slow:
    skip_packages += slow_test_suites

# psutil expects TRAVIS to signal deactivating unstable tests
os.environ['TRAVIS'] = '1'

package_names = []
#for package in packages:
#    if isinstance(package, TestPackage):
#       package_names.append(package.pypi_name)


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
regex_test_result = run_tests(
    [regex_package],
    quit_early=quit_early,
)

# todo evict all new modules after each job
#sys_modules_post = set(sys.modules.copy())
#print('new mods', sorted(sys_modules_post - sys_modules_pre))

unregister_import_hook(h)

remove_test_modules()

# pip_shims & pip is needed for landinggear, but causes cached-property tests to fail
del sys.modules['pip_shims']
if 'pip' in sys.modules:
    for m in sorted(sys.modules):
        if m.startswith('pip'):
            del sys.modules[m]

# Main test run
# TODO: skipped packages are not resolved, so they appear as unknown
#       if mod_name is not the same as pypi_name

test_results = run_tests(
    packages,
    quit_early=quit_early,
    skip_packages=skip_packages,
)

packages.append(regex_package)
test_results[regex_package] = regex_test_result[regex_package]

failures = {}
# TODO: Assert that all tested packages are built into PyOxidizer
for package, result in test_results.items():
    if result:
        failures[package] = result

if failures:
    print('Failures:')
    for package, result in failures.items():
        print(package, result)

non_test_results = run_tests(untestable)

pprint(non_test_results)

for package, result in non_test_results.items():
    test_results[package] = result
    if not result:
        print('Unexpected success:', package, result)

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

packages += untestable

namespace_packages = {package.pypi_name.rsplit('.', 1)[0] for package in packages if isinstance(package, TestPackage) and '.' in package.pypi_name}
for package in namespace_packages.copy():
    top_level = package.split('.')[0]
    namespace_packages.add(top_level)


namespace_packages.add('sphinxcontrib')
print('Namespace packages: ', namespace_packages)

assert 'repoze' in namespace_packages
assert 'zope' in namespace_packages
assert 'ruamel' in namespace_packages
assert 'ruamel.std' in namespace_packages

_pyox_packages = package_versions(_pyox_modules, standard_lib=False, namespace_packages=namespace_packages)

assert 'repoze.lru' in _pyox_packages

#print('_pyox_packages:')
#pprint(_pyox_packages)

untested = []

for mod, info in _pyox_packages.items():
    if mod in namespace_packages:
        continue
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

assert TestPackage('repoze') not in untested

for mod in sorted(_pyox_modules):
    if _is_std_lib(mod):
        continue
    if mod in namespace_packages:
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

assert TestPackage('repoze') not in untested

for package in untested:
    print(f'{package} not known')
if not untested:
    print('All packages tested')

# TODO: _sodium should not be listed as a test dependency,
# however `import nacl._sodium` also creates `_sodium` in sys.modules
# Also occurs in 'real' python3
test_dependencies = package_versions(standard_lib=False,
                                     namespace_packages=namespace_packages,
                                     exclude=_pyox_modules)

print('Test dependencies:')
pprint(test_dependencies)

sys.exit(not failures and not untested)

# Error in atexit._run_exitfuncs:
#Traceback (most recent call last):
#  File "multiprocessing.util", line 277, in _run_finalizers
#  File "multiprocessing.util", line 201, in __call__
#  File "billiard.pool", line 1662, in _terminate_pool
#  File "billiard.pool", line 1638, in _help_stuff_finish
#KeyboardInterrupt
