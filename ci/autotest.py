import import_hooks

skip_test_modules = set([
    # Core dumps due to   File "test.support", line 172 in _save_and_remove_module
    # File "test.support", line 255 in import_fresh_module
    "test.test_asyncio",
    "test.test_email",
  
    # halts
    "test.test_cmd_line_script",
    "test.test_file_eintr",
    "test.test_httpservers",
    "test.test_readline",
    "test.test_signal",
    "test.test_subprocess",
    "test.test_multiprocessing_forkserver",
    "test.test_multiprocessing_spawn",

    #"test_importlib",

    "test.test_datetime",  # crashs due to missing _testcapi
    "test.test_code",  # missing _PyEval_RequestCodeExtraIndex
    "test.test_ctypes",  # attempts loading external file _ctypes_test
    "test.test_tcl",  # crashes
    "test.test_ttk_textonly",  # crashes
    "test.test_ssl",  # crashes ssl.SSLError: peer did not return a certificate
    "test.test_idle",  # depends on tk
    "test.test_wsgiref",  # depends on test_httpservers
    "lib2to3.tests.test_main",
    "test.test_importlib.frozen.test_loader",
    "test.test_importlib.frozen.test_finder",
    "test.test_importlib.test_namespace_pkgs",
    "test.test_importlib.test_resource",
    "test.test_importlib.extension.test_finder",
])

cpython_root = './build/target/x86_64-unknown-linux-gnu/debug/pyoxidizer/python.608871543e6d/python/install/lib/python3.7/'

import os.path

cpython_root = os.path.abspath(cpython_root)

import_hooks.add_no_load(skip_test_modules)

import_hooks.add_external_cpython_test_file_dunder(cpython_root)


# inspect.findsource(inspect)
# sys.meta_path[0].get_source('inspect')

# This module is unusable unless another import hook is created
import_hooks.add_external_file_dunder(cpython_root, ['lib2to3.pygram'])

# These need analysis to determine whether the need for __file__ renders the module unusable

# This should be refined to specific tests where argparse.__file__ is needed, and/or
# argparse patched to work without __file__
import_hooks.add_file_dunder_during(cpython_root, 'test.test_argparse', 'argparse')
import_hooks.add_file_dunder_during(cpython_root, 'test.test_ast', 'ast')
import_hooks.add_file_dunder_during(cpython_root, 'test.test_imp', 'imp')
import_hooks.add_file_dunder_during(cpython_root, 'test.test_import', 'os')
import_hooks.add_file_dunder_during(cpython_root, 'test.test_import', 'importlib._bootstrap_external')
import_hooks.add_file_dunder_during(cpython_root, 'test.test_import', 'importlib._bootstrap')
import_hooks.add_file_dunder_during(cpython_root, 'test.test_linecache', 'linecache')
import_hooks.add_file_dunder_during(cpython_root, 'test.test_modulefinder', 'tempfile')
import_hooks.add_file_dunder_during(cpython_root, 'test.test_multiprocessing_fork', 'multiprocessing')
import_hooks.add_file_dunder_during(cpython_root, 'test.test_pydoc', 'pydoc')
import_hooks.add_file_dunder_during(cpython_root, 'test.test_pydoc', 'string')
import_hooks.add_file_dunder_during(cpython_root, 'test.test_venv', 'venv')
import_hooks.add_file_dunder_during(cpython_root, 'test.test_zipfile', 'email')
import_hooks.add_file_dunder_during(cpython_root, 'unittest.test', 'unittest')

import_hooks.add_file_dunder_during(cpython_root, 'distutils.tests', 'distutils')

# not working
import_hooks.add_file_dunder_during(cpython_root, 'test.test_urllib2', 'urllib.request')

print('during hooks added')

# _ctypes_test needs a __file__ , but it cant be a .py

from unittest import skip, SkipTest

def get_test_module(name):
    if name.startswith('distutils.tests') or name.startswith('unittest.test.') or '.data.' in name or name.startswith('lib2to3.tests.') or name.startswith('test.test_importlib.') or name in ['test.test_json.test_tool']:
        return name
    elif name.startswith('test.'):
        return name[5:].split('.', 1)[0]

func_delete = {
    # sys.executable
    'test_doctest': ['test_CLI', 'test_unicode'],
    # substantial problems
    'test_pdb': ['test_list_commands'],
    #'test_asyncio': ['load_tests'],
}

func_skip = {
    # sys.executable
    'test_keyword': ['TestKeywordGeneration._generate_keywords'],
    'test_popen': ['PopenTest._do_test_commandline'],
}

# unittest.TestSuite
func_empty_suite = {
    'test_importlib': ['load_tests'],
}

capi_tests = {
    'test_array': ['BaseTest.test_obsolete_write_lock'],
    'test_atexit': ['SubinterpreterTest'],
    'test_buffer': ['TestBufferProtocol.test_memoryview_sizeof'],
    'test_bytes': ['ByteArrayTest.test_obsolete_write_lock'],
    'test_call': ['FastCallTests'],
    'test_cmath': ['CMathTests.test_polar_errno'],
    'test_codecs': ['BasicUnicodeTest.test_basics_capi'],
    'test_coroutines': ['CAPITest'],
    'test_csv': ['Test_Csv.test_writerows_legacy_strings'],
    'test_decimal': [
        'CExplicitConstructionTest.test_from_legacy_strings',
        'PyExplicitConstructionTest.test_from_legacy_strings',
        'CContextAPItests.test_from_legacy_strings',
        'PyContextAPItests.test_from_legacy_strings',
    ],
    'test_deque': ['TestBasic.test_sizeof'],
    'test_dict': ['CAPITest', 'DictTest.test_splittable_setattr_after_pop'],
    'test_fcntl': [
        'TestFcntl.test_fcntl_bad_file_overflow',
        'TestFcntl.test_flock_overflow',
    ],
    'test_fileio': ['COtherFileTests.testInvalidFd_overflow'],
    'test_finalization': ['LegacyFinalizationTest'],
    'test_float': ['IEEEFormatTestCase.test_serialized_float_rounding'],
    'test_format': ['FormatTest.test_precision_c_limits'],
    'test_gc': [
        'GCTests.test_legacy_finalizer',
        'GCTests.test_legacy_finalizer_newclass',
    ],
    'test_genericclass': ['CAPITest'],
    'test_exceptions': [
        'ExceptionTests.testSettingException',
        'ExceptionTests.test_MemoryError',
        'ExceptionTests.test_exception_with_doc',
        'ExceptionTests.test_memory_error_cleanup',
    ],
    'test_import': [
        'ImportTests.test_from_import_missing_attr_has_name_and_so_path',
    ],
    'test_inspect': [
        'TestClassesAndFunctions.test_getfullagrspec_builtin_func',
        'TestClassesAndFunctions.test_getfullagrspec_builtin_func_no_signature',
        'TestSignatureObject.test_signature_on_builtins',
        'TestSignatureObject.test_signature_on_builtins_no_signature',
        'TestSignatureObject.test_signature_on_decorated_builtins',
        'TestSignatureObject.test_signature_on_builtins',
    ],
    'test_io': [
        'CTextIOWrapperTest.test_device_encoding',
        'PyTextIOWrapperTest.test_device_encoding',
    ],
    'test_poll': ['PollTests.test_poll_c_limits'],
    'test_posix': ['PosixTester.test_pipe2_c_limits'],
    'test_repl': ['TestInteractiveInterpreter.test_no_memory'],
    'test_socket': [
        'GeneralModuleTests.testNtoHErrors',
        'GeneralModuleTests.test_listen_backlog_overflow',
        'BasicTCPTest._testShutdown_overflow',
        'BasicTCPTest._testShutdown_overflow',
        'NonBlockingTCPTests.testSetBlocking_overflow',
    ],
    'test_sys': [
        'SysModuleTest.test_getallocatedblocks',
        'SysModuleTest.test_setrecursionlimit_recursion_depth',
        'SizeofTest',
    ],
    'test_threading': [
        'ThreadTests.test_frame_tstate_tracing',
        'SubinterpThreadingTests.test_threads_join',
        'SubinterpThreadingTests.test_threads_join_2',
    ],
    'test_unicode': [
        'CAPITest',
        'UnicodeTest.test_formatting_c_limits',
        'UnicodeTest.test_formatting_huge_precision_c_limits',
    ],
    'test_userstring': ['UserStringTest.test_formatting_c_limits'],
    'test_weakref': ['ReferencesTestCase.test_cfunction'],
}

def raise_skip(reason):
    raise SkipTest(reason)

force_skip = lambda *args, **kwargs: raise_skip('see autotest.py')

def teardown_fixup(self):
    self.visit = 1
    raise_skip('testcapi missing')

#del test.test_doctest.__dict__['test_unicode']  # possibly sys.executable
#test.test_keyword.TestKeywordGeneration._generate_keywords = lambda *args, **kwargs: raise_skip('exec sys.executable')
# test.test_popen.PopenTest._do_test_commandline = lambda *args, **kwargs: raise_skip('exec sys.executable')

sys_executable_tests = {
    'distutils.tests.test_spawn': ['SpawnTestCase.test_find_executable'],
    'lib2to3.tests.test_parser': ['TestPgen2Caching.test_load_grammar_from_subprocess'],
    'test_atexit': ['GeneralTest.test_shutdown'],
    'test_base64': ['TestMain'],
    #'test_asyncio.test_events'
    'test_builtin': ['ShutdownTest'],
    'test_calendar': ['CommandLineTestCase'],
    'test_cgitb': [
        'TestCgitb.test_syshook_no_logdir_default_format',
        'TestCgitb.test_syshook_no_logdir_text_format',
    ],
    'test_cmd_line': ['CmdLineTest'],
    'test_compileall': [
        'CommmandLineTestsNoSourceEpoch',
        'CommmandLineTestsWithSourceEpoch',
    ],
    'test_cprofile': [
        'CProfileTest.test_module_path_option',
        'TestCommandLine',
    ],
    'test_exceptions': [
        'ExceptionTests.test_memory_error_in_PyErr_PrintEx',
        'ExceptionTests.test_recursion_normalizing_exception',
        'ExceptionTests.test_recursion_normalizing_infinite_exception',
        'ExceptionTests.test_recursion_normalizing_with_no_memory',
    ],
    'test_gc': ['GCTests.test_garbage_at_shutdown'],
    'test_gzip': ['TestCommandLine'],
    'test.test_json.test_tool': ['TestTool.test_stdin_stdout'],
    'test_multiprocessing_fork': [
        'TestFlags.test_flags',
        'TestStartMethod.test_context',
        'TestStartMethod.test_set_get',
    ],
    'test_os': [
        'PidTests.test_getppid',
        'SpawnTests',
        'URandomTests.test_urandom_subprocess',
    ],
    'test_parser': ['ParserStackLimitTestCase.test_trigger_memory_error'],
    'test_platform': ['PlatformTest.test_popen'],

    'test_quopri': [
        'QuopriTestCase.test_scriptdecode',
        'QuopriTestCase.test_scriptencode',
    ],
    'test_regrtest': ['ArgsTestCase', 'ProgramsTestCase'],

    'test_script_helper': [
        'TestScriptHelper.test_assert_python_failure',
        'TestScriptHelper.test_assert_python_ok_raises',
    ],
    'test_tarfile': ['CommandLineTest'],
    'test_threading': [
        'SubinterpThreadingTests.test_daemon_threads_fatal_error',
        'ThreadTests.test_finalize_runnning_thread',
    ],
    'test_trace': ['TestCommandLine', 'TestCoverageCommandLineOutput'],
    'test_traceback': [
        'CExcReportingTests',
        'TracebackCases.test_encoded_file',
        'TracebackFormatTests',
    ],
    'test_support': [
        'TestSupport.test_args_from_interpreter_flags',
        'TestSupport.test_optim_args_from_interpreter_flags',
    ],
    'test_sys': [
        'SysModuleTest.test_executable',
        'SysModuleTest.test_ioencoding',
        'SysModuleTest.test_recursionlimit_fatalerror',
        'SysModuleTest.test_sys_tracebacklimit',
    ],
    'test_tracemalloc': ['TestCommandLine'],
    'test_unicodedata': ['UnicodeMiscTest.test_failed_import_during_compiling'],
    'test_venv': [
        'EnsurePipTest',
        'BasicTest.test_deactivate_with_strict_bash_opts',
        'BasicTest.test_executable',
        'BasicTest.test_executable_symlinks',
        'BasicTest.test_multiprocessing',
        'BasicTest.test_prefixes',
    ],
    'test_warnings_broken': [
        'CEnvironmentVariableTests.test_conflicting_envvar_and_command_line',
        'PyEnvironmentVariableTests.test_conflicting_envvar_and_command_line',
    ],
    'test_zipfile': ['CommandLineTest'],
    'unittest.test.test_program': ['TestCommandLineArgs.testSelectedTestNamesFunctionalTest'],
    'unittest.test.test_runner': ['Test_TextTestRunner.test_warnings'],
}

removed_data_tests = {
    'test_source_encoding': [
        'MiscSourceEncodingTest.test_bad_coding',
        'MiscSourceEncodingTest.test_bad_coding2',
    ],
    'test_tokenize': ['TestTokenizerAdheresToPep0263.test_bad_coding_cookie'],
    'test_future': [
        'FutureTest.test_badfuture3',
        'FutureTest.test_badfuture4',
        'FutureTest.test_badfuture5',
        'FutureTest.test_badfuture6',
        'FutureTest.test_badfuture7',
        'FutureTest.test_badfuture8',
        'FutureTest.test_badfuture9',
        'FutureTest.test_badfuture10',
    ],
    'test_py_compile': [
        'PyCompileTestsWithSourceEpoch.test_bad_coding',
        'PyCompileTestsWithoutSourceEpoch.test_bad_coding',
    ],
    'test_unicode_identifiers': ['PEP3131Test.test_invalid'],
    'test_utf8source': ['PEP3120Test.test_badsyntax'],
}

# test import/filename oddities, likely due to __file__ hacks
filename_diff_tests = {
    'test_exceptions': [
        'ExceptionTests.test_unhandled',
        'ExceptionTests.test_unraisable',
    ],
    'test_asyncore': ['HelperFunctionTests.test_compact_traceback'],

    'test_dis': [
        'DisTests.test_bug_1333982',
        'DisTests.test_disassemble_recursive',
        'DisWithFileTests.test_bug_1333982',
        'DisWithFileTests.test_disassemble_recursive',
    ],
    'test_import': ['ImportTracebackTests'],
    'test_inspect': ['TestRetrievingSourceCode.test_getsourcefile'],
    'test_profile': ['ProfileTest.test_cprofile'],
    'test_pyexpat': ['HandlerExceptionTest.test_exception'],
    'test_trace': [
        'TestCallers',
        'TestCoverage',
        'TestFuncs',
        'TestLineCounts',
        'TestRunExecCounts',
    ],
    'test_traceback': [
        'MiscTracebackCases.test_extract_stack',
        'TestStack.test_format_locals',
    ],
    'test_warnings': [
        'CWarnTests.test_stacklevel',
        'CWarnTests.test_stacklevel_import',
        'PyWarnTests.test_stacklevel_import',
    ],
    'test_multiprocessing_fork': ['WithProcessesTestSubclassingProcess.test_stderr_flush'],
    'unittest.test.test_case': [
        'Test_TestCase.testAssertWarnsContext',
        'Test_TestCase.testAssertWarnsRegexContext',
    ],
}

# Entire or substantial module failures, some unknown reasons
# doctest:
#test.test_pdb.test_list_commands = skip('known module failures')

substantial_module_skip = {
    'test_bdb': ['StateTestCase','BreakpointTestCase','IssuesTestCase'],
    'test_c_locale_coercion': ['LocaleCoercionTests', 'LocaleConfigurationTests'],
    'test_concurrent_futures': [
        'ProcessPoolForkExecutorDeadlockTest',
        'ProcessPoolForkProcessPoolShutdownTest.test_context_manager_shutdown',
        'ProcessPoolForkProcessPoolShutdownTest.test_del_shutdown',
        'ProcessPoolForkserverAsCompletedTest',
        'ProcessPoolForkserverExecutorDeadlockTest',
        'ProcessPoolForkserverFailingInitializerTest',
        'ProcessPoolForkserverInitializerTest',
        'ProcessPoolForkserverProcessPoolExecutorTest',
        'ProcessPoolForkserverProcessPoolShutdownTest',
        'ProcessPoolForkserverWaitTest',
        'ProcessPoolSpawnAsCompletedTest',
        'ProcessPoolSpawnExecutorDeadlockTest',
        'ProcessPoolSpawnFailingInitializerTest',
        'ProcessPoolSpawnInitializerTest',
        'ProcessPoolSpawnProcessPoolExecutorTest',
        'ProcessPoolSpawnProcessPoolShutdownTest',
        'ProcessPoolSpawnWaitTest',
    ],
    'test_dataclasses': ['TestMakeDataclass.test_non_identifier_field_names'],
    'test_ensurepip': ['TestBootstrap', 'TestBootstrappingMainFunction'],
    'test_faulthandler': ['FaultHandlerTests'],
    'test_hash': [
        'BytesHashRandomizationTests','MemoryviewHashRandomizationTests',
        'StrHashRandomizationTests',
        'DatetimeDateTests.test_randomized_hash',
        'DatetimeDatetimeTests.test_randomized_hash',
        'DatetimeTimeTests.test_randomized_hash',
    ],
    'test_gc': ['GCTests.test_get_count'],
    'test.test_importlib.extension.test_loader': [
        'Frozen_MultiPhaseExtensionModuleTests',
        'Source_MultiPhaseExtensionModuleTests',
        'Frozen_LoaderTests',
        'Source_LoaderTests',
        #'Source_InspectLoaderTests',
        # 'Source_ExecModuleTests',
    ],
    'test.test_importlib.frozen.test_finder': [
        'Frozen_FindSpecTests',
        'Source_FindSpecTests',
    ],
    'test.test_importlib.frozen.test_loader': [
        'Frozen_ExecModuleTests',
        #'Frozen_InspectLoaderTests',
        'Source_ExecModuleTests',
        'Source_InspectLoaderTests',
        'Source_LoaderTests',
    ],
    'test.test_importlib.test_resource': [
        'ResourceDiskTests.test_contents',
        'ResourceDiskTests.test_is_resource_missing',
        'ResourceDiskTests.test_is_resource_subresource_directory',
        'SubdirectoryResourceFromZipsTest',
        'NamespaceTest.test_namespaces_cannot_have_resources',
    ],
    'test.test_importlib.test_api': ['Frozen_ReloadTests', 'Source_ReloadTests'],
    'test.test_importlib.test_namespace_pkgs': [
        'SeparatedNestedZipNamespacePackages',
        'SeparatedZipNamespacePackages',
        'SingleNestedZipNamespacePackage',
    ],
    'test.test_importlib.test_read': ['ReadZipTests'],
    'test.test_importlib.test_path': [
        'CommonTests.test_importing_module_as_side_effect',
        'CommonTests.test_package_name',
        'CommonTests.test_package_object',
        'CommonTests.test_pathlib_path',
        'CommonTests.test_string_path',
        'PathZipTests',
        'PathDiskTests.test_reading',
    ],
    'test.test_importlib.test_namespace_pkgs': ['ZipWithMissingDirectory'],
    'test.test_importlib.test_open': ['OpenZipTests'],


    'test_logging': ['QueueListenerTest', 'ExceptionTest.test_formatting'],
    'test_multiprocessing_fork': ['TestSemaphoreTracker'],
    'test_multiprocessing_main_handling': [
        'ForkCmdLineTest', 'ForkServerCmdLineTest', 'SpawnCmdLineTest',
    ],
    'test_pdb': [
        'PdbTestCase.test_issue13120',
        'PdbTestCase.test_issue16180',
        'PdbTestCase.test_blocks_at_first_code_line',
        'PdbTestCase.test_breakpoint',
        'PdbTestCase.test_errors_in_command',
        'PdbTestCase.test_issue13183',
        'PdbTestCase.test_issue13210',
        'PdbTestCase.test_module_is_run_as_main',
        'PdbTestCase.test_module_without_a_main',
        'PdbTestCase.test_relative_imports',
        'PdbTestCase.test_relative_imports_on_plain_module',
        'PdbTestCase.test_run_module',
        'PdbTestCase.test_run_pdb_with_pdb',
    ],
    # extra 'sys' in sys.modules
    'test_modulefinder': [
        'ModuleFinderTest.test_absolute_imports',
        'ModuleFinderTest.test_maybe',
        'ModuleFinderTest.test_maybe_new',
        'ModuleFinderTest.test_package',
        'ModuleFinderTest.test_replace_paths',
    ],
    # missing source code?
    'test_atexit': ['GeneralTest.test_print_tracebacks'],
    'test_coroutines': ['OriginTrackingTest.test_origin_tracking_warning'],
    'test_inspect': [
        'TestRetrievingSourceCode.test_getframeinfo_get_first_line',
        'TestInterpreterStack.test_stack',
        'TestInterpreterStack.test_trace',
    ],
    'unittest.test.testmock.testpatch': ['PatchTest.test_tracebacks'],
    # ValueError: sys.__spec__ is None
    'test_pkgutil': [
        'ImportlibMigrationTests.test_find_loader_avoids_emulation',
        'ImportlibMigrationTests.test_get_loader_avoids_emulation',
    ],
    'lib2to3.tests.test_refactor': [
        'TestRefactoringTool.test_bom',
        'TestRefactoringTool.test_crlf_newlines',
        'TestRefactoringTool.test_false_file_encoding',
        'TestRefactoringTool.test_file_encoding',
    ],
    'test_warnings': [
        '_WarningsTests.test_default_action',
        'CFilterTests.test_filterwarnings',
        'CFilterTests.test_mutate_filter_list',
        'CFilterTests.test_always_after_default',
        'CFilterTests.test_error_after_default',
        'CFilterTests.test_ignore_after_default',
    ],
    'test_zipimport': ['CompressedZipImportTestCase', 'UncompressedZipImportTestCase'],
    'test_zipimport_support': ['ZipSupportTests'],
}

oddballs = {
    'test_getpass': ['GetpassRawinputTest.test_uses_stderr_as_default'],
    'test_imp': [
        'ImportTests.test_issue1267',
        'ImportTests.test_issue16421_multiple_modules_in_one_dll',
        'ImportTests.test_issue24748_load_module_skips_sys_modules_check',
        'ImportTests.test_load_from_source',
    ],
    'test_import': [
        'ImportTests.test_concurrency',
        'RelativeImportTests.test_import_from_unloaded_package',
        'ImportTests.test_delete_builtins_import',
    ],
    'test_logging': ['StreamHandlerTest.test_error_handling'],
    'test_threaded_import': ['ThreadedImportTests.test_parallel_path_hooks'],
    'test_threading': ['InterruptMainTests.test_interrupt_main_error'],
    'test_pkgutil': [
        'PkgutilTests.test_getdata_filesys',
        'PkgutilTests.test_getdata_zipfile',
        'PkgutilTests.test_walkpackages_filesys',
        'PkgutilTests.test_walkpackages_zipfile',
    ],
    'test_pydoc': ['PydocDocTest.test_mixed_case_module_names_are_lower_cased'],
    'test_socket': [
        'BasicTCPTest.testShutdown_overflow',
        'BasicTCPTest2.testShutdown_overflow',
    ],
    'test_sys': [
        'SysModuleTest.test_c_locale_surrogateescape',
        'SysModuleTest.test_posix_locale_surrogateescape',
        'SysModuleTest.test_current_frames',
    ],
    'test_traceback': ['PyExcReportingTests.test_cause_recursive'],
    'test_warnings': ['PyWarnTests.test_missing_filename_main_with_argv'],
    'unittest.test.test_discovery': ['TestDiscovery.test_discovery_from_dotted_path_builtin_modules'],
    'unittest.test.testmock.testsentinel': ['SentinelTest.testPickle'],
    'unittest.test.testmock.testwith': ['TestMockOpen.test_mock_open_read_with_argument'],
    'unittest.test.test_loader': ['Test_TestLoader.test_loadTestsFromNames__module_not_loaded'],
}

test_skip_sets = {
    'testcapi missing': capi_tests,
    'sys.executable': sys_executable_tests,
    'removed data file': removed_data_tests,
    'filename hacks': filename_diff_tests,
    'significant problems': substantial_module_skip,
    'oddballs': oddballs,
    'missing symbol': {
        'test_threading': ['ThreadTests.test_PyThreadState_SetAsyncExc'],
    },
    'missing internals': {
        'test_pyclbr': ['PyclbrTest'],
    },
    'PyOxidizer repr': {
        'test_frame': ['ReprTest.test_repr'],
        'test_reprlib': ['LongReprTest.test_module'],
        'test_fstring': ['TestCase.test_global'],
        'test_module': [
            'ModuleTests.test_module_repr_builtin',
            'ModuleTests.test_module_repr_source',
        ],
        'test_pydoc': ['PydocImportTest.test_importfile'],
    },
    'test logic unexpected builtins': {
        'test_rlcompleter': ['TestRlcompleter.test_global_matches']
    },
    'missing os.__cached__': {'test_pydoc': ['PydocDocTest.test_synopsis_sourceless']},
    'needs rpmbuild': {'distutils.tests.test_bdist_rpm': ['BuildRpmTestCase']},
    'needs clang': {
        'distutils.tests.test_build_ext': [
            'BuildExtTestCase.test_build_ext',
            'ParallelBuildExtTestCase.test_build_ext',
        ],
        'distutils.tests.test_install': ['InstallTestCase.test_record_extensions'],
    },
    # sysconfig.get_config_var("platlibdir") empty
    'platlibdir empty': {'test_sysconfig': ['TestSysConfig.test_user_similar']},
    # sysconfig.get_makefile_filename() is 'lib/python3.7/config-3.7m-x86_64-linux-gnu/Makefile' not present
    'get_makefile_filename not present': {'test_sysconfig': ['MakefileTests.test_get_makefile_filename']},
    'get_config_h not present': {
        'test_sysconfig': ['TestSysConfig.test_get_config_h_filename'],
        'distutils.tests.test_sysconfig': ['SysconfigTestCase.test_get_config_h_filename'],
    },
    'srcdir not present': {
        'test_sysconfig': ['TestSysConfig.test_srcdir'],
        'distutils.tests.test_sysconfig': ['SysconfigTestCase.test_srcdir'],
    },
    '__hello__ not implemented': {'test_frozen': ['TestFrozen.test_frozen']},
    'removed functions': func_delete,
    'forced skip functions': func_skip,
    "traceback style": {
        'test_concurrent_futures': ['ProcessPoolExecutorTest.test_traceback'],
        'test_pydoc': ['TestDescriptions.test_typing_pydoc'],
        'test_traceback': [
            'PyExcReportingTests.test_cause',
            'PyExcReportingTests.test_cause_and_context',
            'PyExcReportingTests.test_cause_and_context',
            'PyExcReportingTests.test_context',
            'PyExcReportingTests.test_context_suppression',
            'PyExcReportingTests.test_simple',
            'TestFrame.test_basics',
            'TestFrame.test_lazy_lines',
            'TestFrame.test_extract_stack_lookup_lines',
            'TestFrame.test_extract_stackup_deferred_lookup_lines',
            'TestTracebackException.test_lookup_lines',
            'TestStack.test_extract_stack_lookup_lines',
            'TestStack.test_extract_stackup_deferred_lookup_lines',
         ],
    },
    'timezone': {
        'test_strptime': [
            'CacheTests.test_TimeRE_recreation_timezone',
            'StrptimeTests.test_bad_timezone',
        ],
        'test_xmlrpc': ['DateTimeTestCase.test_default'],
    },
}

def noop(*args, **kwargs):
    pass

def raise_skip(reason):
    raise SkipTest(reason)

force_skip = lambda *args, **kwargs: raise_skip('see autotest.py')

def doctor_module(name, module):
    #print("doctor_module", name, module)
    test_module = get_test_module(name)

    if test_module == 'test_gc':
        cls = getattr(module, 'GCCallbackTests')
        setattr(cls, 'test_collect_garbage', teardown_fixup)

    for message, test_skips in test_skip_sets.items():
        skip_data = test_skips.get(test_module, [])
        for item in skip_data:
            attr, _, meth = item.partition('.')
            if test_skips == func_empty_suite:
                setattr(module, attr, unittest.TestSuite())
                continue

            if test_skips == func_skip:
                setattr(module, attr, force_skip)
                continue
            if test_skips == func_delete:
                setattr(module, attr, noop)
                continue
            cls = getattr(module, attr)
            # print('doctoring %s %s %s' % (test_module, attr, meth))
            if meth:
                setattr(cls, meth, skip(message))
            else:
                setattr(module, attr, skip(message)(cls))

#test_skip_dicts = 
test_skip_set_modules = [
    module
    for d in test_skip_sets.values()
    for module in d.keys()
]
test_skip_set_modules = [
    'test.' + name if name.startswith('test_') else name
    for name in test_skip_set_modules
]

import_hooks.add_after_import_hook(test_skip_set_modules, doctor_module)

import_hooks.ignore_del_missing_modules(['spam'])

import test.support
test.support.check_sizeof = lambda *args, **kwargs: raise_skip('testcapi missing')
test.support.run_in_subinterp = lambda *args, **kwargs: raise_skip('testcapi missing')


# sys.executable isnt compatible with python CLI
import test.support.script_helper
test.support.script_helper.assert_python_failure = lambda *args, **kwargs: raise_skip('exec sys.executable')
test.support.script_helper.assert_python_ok = lambda *args, **kwargs: raise_skip('exec sys.executable')
test.support.script_helper.run_python_until_end = lambda *args, **kwargs: raise_skip('exec sys.executable')

from test.libregrtest import main

try:
    main(
        #['test_importlib'],  #, 'test_multiprocessing_forkserver', 'test_json', 'test_lib2to3', 'test_tools'],  #, 'test_idle', 'test_import', 'test_importlib'],
        #["ctypes.test"],
        #["lib2to3.tests"],
        verbose2=True,
        #exclude=True,
   )
except SystemExit:
   pass
