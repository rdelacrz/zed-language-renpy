//! Zed extension entry point for Ren'Py language support.
//!
//! This WASM crate implements [`zed_extension_api::Extension`] to register the Ren'Py language
//! server with Zed. It resolves the `renpy-language-server` binary path from user settings or
//! `$PATH`, and forwards initialization options and workspace configuration to the LSP.

use zed::settings::LspSettings;
use zed_extension_api::{self as zed, LanguageServerId, Result};

/// Main extension struct registered with the Zed editor runtime.
struct RenpyExtension;

impl zed::Extension for RenpyExtension {
    fn new() -> Self {
        Self
    }

    /// Resolves the language server binary command, arguments, and environment.
    ///
    /// Lookup order for the binary path:
    /// 1. User-configured `lsp.renpy-language-server.binary.path` in Zed settings.
    /// 2. `renpy-language-server` found on the worktree's `$PATH`.
    fn language_server_command(
        &mut self,
        _language_server_id: &LanguageServerId,
        worktree: &zed::Worktree,
    ) -> Result<zed::Command> {
        let lsp_settings = LspSettings::for_worktree("renpy-language-server", worktree).ok();

        let command = lsp_settings
            .as_ref()
            .and_then(|s| s.binary.as_ref())
            .and_then(|b| b.path.clone())
            .or_else(|| worktree.which("renpy-language-server"))
            .ok_or_else(|| "renpy-language-server not found on PATH. Install it or set lsp.renpy-language-server.binary.path in Zed settings.".to_string())?;

        let args = lsp_settings
            .as_ref()
            .and_then(|s| s.binary.as_ref())
            .and_then(|b| b.arguments.clone())
            .unwrap_or_default();

        let env = lsp_settings
            .as_ref()
            .and_then(|s| s.binary.as_ref())
            .and_then(|b| b.env.clone())
            .unwrap_or_default()
            .into_iter()
            .collect();

        Ok(zed::Command { command, args, env })
    }

    /// Returns LSP initialization options from user settings, if configured.
    fn language_server_initialization_options(
        &mut self,
        _language_server_id: &LanguageServerId,
        worktree: &zed::Worktree,
    ) -> Result<Option<zed_extension_api::serde_json::Value>> {
        Ok(LspSettings::for_worktree("renpy-language-server", worktree)
            .ok()
            .and_then(|s| s.initialization_options))
    }

    /// Returns workspace configuration (settings) forwarded to the language server.
    fn language_server_workspace_configuration(
        &mut self,
        _language_server_id: &LanguageServerId,
        worktree: &zed::Worktree,
    ) -> Result<Option<zed_extension_api::serde_json::Value>> {
        Ok(LspSettings::for_worktree("renpy-language-server", worktree)
            .ok()
            .and_then(|s| s.settings))
    }
}

zed::register_extension!(RenpyExtension);
