//! Zed runs this crate as WASI Preview 2; the native server speaks stdio LSP.
use zed::settings::LspSettings;
use zed_extension_api::{self as zed, LanguageServerId, Result};

const SERVER: &str = "renpy-language-server";
struct RenpyExtension;

fn server_command(settings: LspSettings, on_path: Option<String>) -> Result<zed::Command> {
    let binary = settings.binary.unwrap_or(zed::settings::CommandSettings {
        path: None,
        arguments: None,
        env: None,
    });
    let command = binary.path.or(on_path).filter(|path| !path.is_empty()).ok_or_else(|| {
        "renpy-language-server not found. Run `python3 scripts/build.py` in the extension checkout, \
         then merge target/zed-settings.json into Zed's settings, or put the built server on PATH. \
         Set lsp.renpy-language-server.binary.path to override its location.".to_owned()
    })?;
    Ok(zed::Command {
        command,
        args: binary.arguments.unwrap_or_default(),
        env: binary.env.unwrap_or_default().into_iter().collect(),
    })
}

impl zed::Extension for RenpyExtension {
    fn new() -> Self {
        Self
    }

    fn language_server_command(
        &mut self,
        _: &LanguageServerId,
        worktree: &zed::Worktree,
    ) -> Result<zed::Command> {
        // Use the worktree's environment, not std::env/PATH inside WASM.
        // Do not hide malformed settings by silently falling back to PATH.
        let settings = LspSettings::for_worktree(SERVER, worktree)?;
        server_command(settings, worktree.which(SERVER))
    }

    fn language_server_initialization_options(
        &mut self,
        _: &LanguageServerId,
        worktree: &zed::Worktree,
    ) -> Result<Option<zed::serde_json::Value>> {
        Ok(LspSettings::for_worktree(SERVER, worktree)?.initialization_options)
    }

    fn language_server_workspace_configuration(
        &mut self,
        _: &LanguageServerId,
        worktree: &zed::Worktree,
    ) -> Result<Option<zed::serde_json::Value>> {
        Ok(LspSettings::for_worktree(SERVER, worktree)?.settings)
    }
}

zed::register_extension!(RenpyExtension);

#[cfg(test)]
mod tests {
    use super::*;
    use zed::serde_json::{from_value, json};

    #[test]
    fn explicit_command_arguments_and_environment_win() {
        let settings = from_value(json!({"binary": {
            "path": "/custom/server", "arguments": ["--stdio"], "env": {"RUST_LOG": "debug"}
        }}))
        .unwrap();
        let command = server_command(settings, Some("/path/server".into())).unwrap();
        assert_eq!(command.command, "/custom/server");
        assert_eq!(command.args, ["--stdio"]);
        assert!(command.env.contains(&("RUST_LOG".into(), "debug".into())));
    }

    #[test]
    fn path_lookup_defaults_to_stdio_without_extra_arguments() {
        let command = server_command(LspSettings::default(), Some("/path/server".into())).unwrap();
        assert_eq!(command.command, "/path/server");
        assert!(command.args.is_empty());
        assert!(command.env.is_empty());
    }

    #[test]
    fn missing_server_is_actionable() {
        let error = server_command(LspSettings::default(), None).err().unwrap();
        assert!(error.contains("scripts/build.py"));
        assert!(error.contains("binary.path"));
    }

    #[test]
    fn configured_arguments_survive_path_lookup() {
        let settings = from_value(json!({"binary": {"arguments": ["--stdio"]}})).unwrap();
        assert_eq!(
            server_command(settings, Some("server".into()))
                .unwrap()
                .args,
            ["--stdio"]
        );
    }
}
