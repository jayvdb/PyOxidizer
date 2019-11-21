// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at https://mozilla.org/MPL/2.0/.

use object::{write, Object, ObjectSection, RelocationTarget, SectionKind, SymbolKind};
use slog::{info, warn};
use std::collections::HashMap;
use std::error::Error;
use std::fmt;

#[derive(Debug, Clone)]
pub struct NoRewriteError;

impl fmt::Display for NoRewriteError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "no object rewriting was performed")
    }
}

impl Error for NoRewriteError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        // Generic error, underlying cause isn't tracked.
        None
    }
}

/// Rename object syn PyInit_foo to PyInit_<full_name> to avoid clashes
pub fn rename_init(
    logger: &slog::Logger,
    name: &String,
    object_data: &[u8],
) -> Result<Vec<u8>, NoRewriteError> {
    let mut rewritten = false;

    let name_prefix = name.split('.').next().unwrap();

    let magic = [
        object_data[0],
        object_data[1],
        object_data[2],
        object_data[3],
        object_data[4],
        object_data[5],
        object_data[6],
        object_data[7],
        object_data[8],
        object_data[9],
        object_data[10],
        object_data[11],
    ];
    warn!(
        logger,
        "Parsing compiled object for {} (magic {:x?})", name, magic
    );

    let in_object = object::File::parse(object_data).unwrap();

    let mut out_object = write::Object::new(in_object.format(), in_object.architecture());
    out_object.mangling = write::Mangling::None;

    let mut out_sections = HashMap::new();
    for in_section in in_object.sections() {
        if in_section.kind() == SectionKind::Metadata {
            continue;
        }
        let section_id = out_object.add_section(
            in_section.segment_name().unwrap_or("").as_bytes().to_vec(),
            in_section.name().unwrap_or("").as_bytes().to_vec(),
            in_section.kind(),
        );
        let out_section = out_object.section_mut(section_id);
        if out_section.is_bss() {
            out_section.append_bss(in_section.size(), in_section.align());
        } else {
            out_section.set_data(in_section.uncompressed_data().into(), in_section.align());
        }
        out_sections.insert(in_section.index(), section_id);
    }

    let mut out_symbols = HashMap::new();
    for (symbol_index, in_symbol) in in_object.symbols() {
        if in_symbol.kind() == SymbolKind::Null {
            continue;
        }
        let (section, value) = match in_symbol.section_index() {
            Some(index) => (
                Some(*out_sections.get(&index).unwrap()),
                in_symbol.address() - in_object.section_by_index(index).unwrap().address(),
            ),
            None => (None, in_symbol.address()),
        };
        let in_sym_name = in_symbol.name().unwrap_or("");
        let sym_name = if in_sym_name.contains("PyInit_") && !in_sym_name.contains(name_prefix) {
            let pyinit_start = in_sym_name.find("PyInit_").unwrap();

            (in_sym_name[0..(pyinit_start + 7)].to_string() + &name.replace(".", "_"))
        } else {
            String::from(in_sym_name)
        };
        if sym_name != in_sym_name {
            warn!(
                logger,
                "rewrote object symbol name {} to {}", in_sym_name, sym_name,
            );

            rewritten = true;
        }

        let out_symbol = write::Symbol {
            name: sym_name.as_bytes().to_vec(),
            value,
            size: in_symbol.size(),
            kind: in_symbol.kind(),
            scope: in_symbol.scope(),
            weak: in_symbol.is_weak(),
            section,
        };
        let symbol_id = out_object.add_symbol(out_symbol);
        out_symbols.insert(symbol_index, symbol_id);
    }

    if !rewritten {
        info!(logger, "no symbol name rewriting occurred for {}", name,);
        return Err(NoRewriteError);
    }

    for in_section in in_object.sections() {
        if in_section.kind() == SectionKind::Metadata {
            continue;
        }
        let out_section = *out_sections.get(&in_section.index()).unwrap();
        for (offset, in_relocation) in in_section.relocations() {
            let symbol = match in_relocation.target() {
                RelocationTarget::Symbol(symbol) => *out_symbols.get(&symbol).unwrap(),
                RelocationTarget::Section(section) => {
                    out_object.section_symbol(*out_sections.get(&section).unwrap())
                }
            };
            let out_relocation = write::Relocation {
                offset,
                size: in_relocation.size(),
                kind: in_relocation.kind(),
                encoding: in_relocation.encoding(),
                symbol,
                addend: in_relocation.addend(),
            };
            out_object
                .add_relocation(out_section, out_relocation)
                .unwrap();
        }
    }

    Ok(out_object.write().unwrap())
}
