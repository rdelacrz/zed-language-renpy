//! Tree-sitter grammar for Ren'Py.

use tree_sitter::Language;

/// Returns a reference to the tree-sitter `Language` for Ren'Py.
pub fn language() -> Language {
    unsafe { Language::from_raw(tree_sitter_renpy() as *const _) }
}

extern "C" {
    fn tree_sitter_renpy() -> *const std::ffi::c_void;
}