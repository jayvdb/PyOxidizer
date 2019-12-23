// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at https://mozilla.org/MPL/2.0/.

use codemap::CodeMap;
use codemap_diagnostic::Diagnostic;
use slog::Drain;
use starlark::environment::Environment;
use starlark::eval;
use starlark::values::Value;

use super::env::global_environment;
use crate::app_packaging::environment::EnvironmentContext;
use crate::logging::PrintlnDrain;

pub fn starlark_env() -> Environment {
    let logger = slog::Logger::root(
        PrintlnDrain {
            min_level: slog::Level::Info,
        }
        .fuse(),
        slog::o!(),
    );

    let build_target = crate::app_packaging::repackage::HOST;

    let cwd = std::env::current_dir().expect("unable to determine CWD");
    let config_path = cwd.join("dummy");

    let context = EnvironmentContext::new(&logger, &config_path, build_target)
        .expect("unable to create EnvironmentContext");

    global_environment(&context).expect("unable to get global environment")
}

pub fn starlark_eval_in_env(env: &mut Environment, snippet: &str) -> Result<Value, Diagnostic> {
    let map = std::sync::Arc::new(std::sync::Mutex::new(CodeMap::new()));
    eval::simple::eval(&map, "<test>", snippet, false, env)
}

pub fn starlark_eval(snippet: &str) -> Result<Value, Diagnostic> {
    let mut env = starlark_env();
    starlark_eval_in_env(&mut env, snippet)
}

pub fn starlark_ok(snippet: &str) -> Value {
    let res = starlark_eval(snippet);
    assert!(res.is_ok());

    res.unwrap()
}

pub fn starlark_nok(snippet: &str) -> Diagnostic {
    let res = starlark_eval(snippet);
    assert!(res.is_err());

    res.unwrap_err()
}
