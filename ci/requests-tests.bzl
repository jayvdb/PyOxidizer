# This file controls the PyOxidizer build configuration. See the
# pyoxidizer crate's documentation for extensive documentation
# on this file format.

# This variable defines the configuration of the
# embedded Python interpreter
embedded_python_config = EmbeddedPythonConfig(
#     bytes_warning=0,
#     dont_write_bytecode=True,
#     ignore_environment=True,
#     inspect=False,
#     interactive=False,
#     isolated=False,
#     legacy_windows_fs_encoding=False,
#     legacy_windows_stdio=False,
     no_site=False,
#     no_user_site_directory=True,
#     optimize_level=0,
#     parser_debug=False,
#     stdio_encoding=None,
#     unbuffered_stdio=False,
     filesystem_importer=True,
#     sys_frozen=False,
#     sys_meipass=False,
     sys_paths=['/usr/lib/python3.7/site-packages', '/home/jayvdb/projects/import-hooks/import-hooks'],
#     raw_allocator=None,
#     terminfo_resolution="dynamic",
#     terminfo_dirs=None,
#     use_hash_seed=False,
#     verbose=0,
#     write_modules_directory_env=None,
)

# This variable captures all packaging rules. Append to it to perform
# additional packaging at build time.
packaging_rules = []

# Package all available extension modules from the Python distribution.
# The Python interpreter will be fully featured.
packaging_rules.append(StdlibExtensionsPolicy("all"))

# Only package the minimal set of extension modules needed to initialize
# a Python interpreter. Many common packages in Python's standard
# library won't work with this setting.
#packaging_rules.append(StdlibExtensionsPolicy("minimal"))

# Only package extension modules that don't require linking against
# non-Python libraries. e.g. will exclude support for OpenSSL, SQLite3,
# other features that require external libraries.
#packaging_rules.append(StdlibExtensionsPolicy("no-libraries"))

# Package the entire Python standard library without sources.
packaging_rules.append(Stdlib(include_source=False))

# Explicit list of extension modules from the distribution to include.
#packaging_rules.append(StdlibExtensionsExplicitIncludes([
#    "binascii", "errno", "itertools", "math", "select", "_socket"
#]))

# Explicit list of extension modules from the distribution to exclude.
#packaging_rules.append(StdlibExtensionsExplicitExcludes(["_ssl"]))

# Write out license files next to the produced binary.
packaging_rules.append(WriteLicenseFiles(""))


# Package using pip, individual packages
packaging_rules.append(PipInstallSimple("requests[security,socks]"))

# Override old pytest incompatible chardet with upcoming chardet
packaging_rules.append(PipInstallSimple("git+https://github.com/chardet/chardet"))

# requests tests use httpbin, which
# uses flask, which indirectly needs built extension markupsafe
packaging_rules.append(PipInstallSimple("markupsafe"))
# uses flasgger, which needs built extension PyYAML
packaging_rules.append(PipInstallSimple("PyYAML"))
# uses brotli.  Either should be ok, but neither work out of the box
# https://github.com/indygreg/PyOxidizer/issues/167
packaging_rules.append(
    PipInstallSimple(
        "git+https://github.com/jayvdb/brotlipy@libbrotli-v1.0-support",
        extra_env={"USE_SHARED_BROTLI": "1"},
    )
)
# PySocks tests need psutil, which has built extensions
# and outdated test-server https://github.com/Anorov/PySocks/issues/117
# and on non-Linux it also requires 3proxy and patched tests
# https://github.com/jayvdb/PySocks/tree/new-test-server
# however test-server requires tornado which isnt working yet
packaging_rules.append(PipInstallSimple("psutil"))

# or use a requirements file
#packaging_rules.append(PipRequirementsFile("requirements.txt"))

# Package .py files discovered in a local directory.
#packaging_rules.append(PackageRoot(
#    path="/src/mypackage", packages=["foo", "bar"],
#))

# Package things from a populated virtualenv.
#packaging_rules.append(Virtualenv(path="/path/to/venv"))

# Filter all resources collected so far through a filter of names
# in a file.
#packaging_rules.append(FilterInclude(files=["/path/to/filter-file"]))

# How Python should run by default. This is only needed if you
# call ``run()``. For applications customizing how the embedded
# Python interpreter is invoked, this section is not relevant.

# Run an interactive Python interpreter.
python_run_mode = python_run_mode_repl()

# Import a Python module and run it.
# python_run_mode = python_run_mode_module("mypackage.__main__")

# Evaluate some Python code.
#python_run_mode = python_run_mode_eval("import scandir")
# from mypackage import main; main()")

Config(
    application_name="requests-dec1",
    embedded_python_config=embedded_python_config,
    python_distribution=default_python_distribution(),
    python_run_mode=python_run_mode,
    packaging_rules=packaging_rules,
)

# END OF COMMON USER-ADJUSTED SETTINGS.
#
# Everything below this is typically managed by PyOxidizer and doesn't need
# to be updated by people.

PYOXIDIZER_VERSION = "0.5.0"
PYOXIDIZER_COMMIT = "9c3c2f724692695a446f5ca8ac6e04a4b6dcb8cb"
