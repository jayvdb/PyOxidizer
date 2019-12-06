# This file controls the PyOxidizer build configuration. See the
# pyoxidizer crate's documentation for extensive documentation
# on this file format.

# Prep of test deps
# python3 -m venv test-deps-venv
# cd test-deps-venv
# test-deps-venv> ./bin/pip install -r /path/to/PyOxidizer/ci/pytest-test-deps.txt
# test-deps-venv> ls lib/python3.7/site-packages
# All of these need to be built in:
# test-deps-venv> find lib -name '*.so'

embedded_python_config = EmbeddedPythonConfig(
     dont_write_bytecode=True,
     ignore_environment=False,
#     no_site=True,
#     no_user_site_directory=True,
#     optimize_level=0,
#     stdio_encoding=None,
#     unbuffered_stdio=False,
     filesystem_importer=True,
#     sys_frozen=False,
#     sys_meipass=False,
     sys_paths=['/home/jayvdb/pyox/pytests-dec1/test-deps-venv/lib/python3.7/site-packages', '/home/jayvdb/projects/import-hooks/import-hooks', '.'],
#     raw_allocator=None,
#     terminfo_resolution="dynamic",
#     terminfo_dirs=None,
#     write_modules_directory_env=None,
)
#     """Defines the configuration of the embedded Python interpreter."""


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

# Needed by regex ; trying backports.test.support
#packaging_rules.append(PackageRoot(
#    path="./cpython_test_support/", packages=["test.support"], excludes=['foo'], # bug in excludes
#))

# Needed by import_hooks
packaging_rules.append(PipInstallSimple("padme"))

packaging_rules.append(
    PipRequirementsFile(
        venv_path="venv",
        requirements_path="/home/jayvdb/projects/python/PyOxidizer/ci/package-tests-special.txt",
        extra_env={
            "REQUIRE_SPEEDUPS": "1",  # used by simplejson
            "USE_SHARED_BROTLI": "1",
            "OPENSSL_EC_BIN_PT_COMP": "1",
            "CRYPTOGRAPHY_SUPPRESS_LINK_FLAGS": "1",
            "SODIUM_INSTALL": "system", # doesnt add -l ?
            "ZSTD_EXTERNAL": "1",
            # python-ldap & pycares & cchardet not possible?
        },
    )
)

packaging_rules.append(
    PipRequirementsFile(
        venv_path="venv",
        requirements_path="/home/jayvdb/projects/python/PyOxidizer/ci/package-tests-remainder.txt",
        extra_env={
            "REQUIRE_SPEEDUPS": "1",  # used by simplejson
        },
    )
)

# Override old pytest incompatible chardet with upcoming chardet
packaging_rules.append(PipInstallSimple("git+https://github.com/chardet/chardet"))

# Package .py files discovered in a local directory.
#packaging_rules.append(PackageRoot(
#    path="/home/jayvdb/projects/osc/devel:languages:python/python-mock/mock-3.0.5", packages=["mock.tests"], excludes=["mock.tests.__init__"],
#))
#
packaging_rules.append(PackageRoot(
    path="/home/jayvdb/projects/osc/devel:languages:python/python-regex/regex-2019.08.19/regex_3/", packages=["regex.test"],
))

packaging_rules.append(PackageRoot(
    path="/home/jayvdb/projects/osc/devel:languages:python/python-colorama/colorama-0.4.1/", packages=["colorama.tests"],
))

packaging_rules.append(PackageRoot(
    path="/home/jayvdb/projects/osc/devel:languages:python/python-more-itertools/more-itertools-7.2.0/", packages=["more_itertools.tests"],
))

packaging_rules.append(PackageRoot(
    path="/home/jayvdb/projects/osc/devel:languages:python/python-netaddr/netaddr-0.7.19/", packages=["netaddr.tests"],
))

packaging_rules.append(PackageRoot(
    path="/home/jayvdb/projects/osc/devel:languages:python/python-python-dateutil/python-dateutil-2.8.1/", packages=["dateutil.test"],
))

packaging_rules.append(PackageRoot(
    path="/home/jayvdb/projects/osc/devel:languages:python/python-setuptools/setuptools-41.4.0/", packages=["setuptools.tests"],
))

packaging_rules.append(PackageRoot(
    path="/home/jayvdb/projects/osc/devel:languages:python/python-pyparsing/pyparsing-2.4.5/", packages=["pyparsing.test"],
))

#packaging_rules.append(PackageRoot(
#    path="/home/jayvdb/projects/osc/devel:languages:python/python-tqdm/tqdm-4.38.0/", packages=["tqdm.tests"],
#))

#packaging_rules.append(PackageRoot(
#    path="/home/jayvdb/projects/osc/devel:languages:python/python-html5lib/html5lib-1.0.1/", packages=["html5lib.tests"],
#))

#packaging_rules.append(PackageRoot(
#    path="/home/jayvdb/projects/osc/devel:languages:python/python-pygit2/pygit2-0.28.2/", packages=["test"],
#))

#packaging_rules.append(PackageRoot(
#    path="/home/jayvdb/projects/osc/devel:languages:python/python-bson/bson-0.5.8/", packages=["test"],
#))

#packaging_rules.append(PackageRoot(
#    path="", packages=["foo.tests"],))


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
#python_run_mode = python_run_mode_eval("from mypackage import main; main()")

Config(
    application_name="package-tests",
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
