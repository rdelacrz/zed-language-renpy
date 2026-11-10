//! Load the exact packaged WASI parser in Tree-sitter's Wasmtime runtime.
use std::{env, fs, path::PathBuf};
use tree_sitter::{wasmtime::Engine, Parser, Query, WasmStore};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../..")
        .canonicalize()?;
    let engine = Engine::default();
    let mut store = WasmStore::new(&engine)?;
    let wasm = fs::read(root.join("target/renpy.wasm"))?;
    let language = store.load_language("renpy", &wasm)?;
    assert!(
        language.is_wasm(),
        "must test WASM, never a native fallback"
    );
    assert!(store.load_language("renpy", b"invalid wasm").is_err());
    let mut parser = Parser::new();
    parser.set_wasm_store(store)?;
    parser.set_language(&language)?;
    let mut paths = vec![
        root.join("examples/game/script.rpy"),
        root.join("examples/game/chapter_two.rpy"),
        root.join("tree-sitter-renpy/examples/smoke.rpy"),
    ];
    paths.extend(env::args_os().skip(1).map(PathBuf::from));
    for path in &paths {
        let source = fs::read(path)?;
        let tree = parser
            .parse(&source, None)
            .ok_or("parser returned no tree")?;
        assert!(
            !tree.root_node().has_error(),
            "{}: {}",
            path.display(),
            tree.root_node().to_sexp()
        );
        println!("WASM parse OK: {}", path.display());
    }
    let mut queries = 0;
    for entry in fs::read_dir(root.join("languages/renpy"))? {
        let path = entry?.path();
        if path.extension().is_some_and(|ext| ext == "scm") {
            Query::new(&language, &fs::read_to_string(&path)?)?;
            queries += 1;
        }
    }
    println!(
        "Verified {} actual WASM parses and {queries} Zed queries; invalid WASM rejected",
        paths.len()
    );
    Ok(())
}
