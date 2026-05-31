use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;
use std::path::PathBuf;
use zed_extension_api::{
    register_extension, Extension, SlashCommand, SlashCommandOutput, Worktree,
};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct NavigationIndex {
    pub name: Option<String>,
    pub version: Option<String>,
    pub labels: Vec<String>,
    pub screens: Vec<String>,
    pub transforms: Vec<String>,
    pub audio: Vec<String>,
    pub config_keys: Vec<String>,
    pub renpy_keys: Vec<String>,
    pub gui_keys: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
pub struct DefinitionLocation {
    pub kind: String,
    pub name: String,
    pub file: String,
    pub line: u32,
    pub column: u32,
}

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
pub struct DiagnosticEntry {
    pub severity: String,
    pub message: String,
    pub file: String,
    pub line: u32,
    pub column: u32,
}

pub struct RenpyExtension;

impl RenpyExtension {
    fn read_json_file(worktree: &Worktree, filename: &str) -> Result<Option<String>, String> {
        let root = worktree.root_path();
        let mut p = PathBuf::from(root.clone());
        p.push("game");
        p.push(filename);
        if !p.exists() {
            let mut alt = PathBuf::from(root);
            alt.push(filename);
            if !alt.exists() {
                return Ok(None);
            }
            let raw = std::fs::read_to_string(&alt).map_err(|e| e.to_string())?;
            return Ok(Some(raw));
        }
        let raw = std::fs::read_to_string(&p).map_err(|e| e.to_string())?;
        Ok(Some(raw))
    }

    fn read_navigation_json(worktree: &Worktree) -> Result<Option<NavigationIndex>, String> {
        let content: Option<String> = Self::read_json_file(worktree, "navigation.json")?;
        content.as_deref().map(parse_navigation_index).transpose()
    }

    fn read_definitions_json(
        worktree: &Worktree,
    ) -> Result<Option<Vec<DefinitionLocation>>, String> {
        let content: Option<String> =
            Self::read_json_file(worktree, "navigation_definitions.json")?;
        content.as_deref().map(parse_definitions_index).transpose()
    }

    fn read_diagnostics_json(worktree: &Worktree) -> Result<Option<Vec<DiagnosticEntry>>, String> {
        let content: Option<String> =
            Self::read_json_file(worktree, "navigation_diagnostics.json")?;
        content.as_deref().map(parse_diagnostics_index).transpose()
    }
}

fn parse_navigation_index(raw: &str) -> Result<NavigationIndex, String> {
    let value: serde_json::Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
    let mut index = NavigationIndex {
        name: value
            .get("name")
            .and_then(|v| v.as_str())
            .map(ToOwned::to_owned),
        version: value
            .get("version")
            .and_then(|v| v.as_str())
            .map(ToOwned::to_owned),
        labels: Vec::new(),
        screens: Vec::new(),
        transforms: Vec::new(),
        audio: Vec::new(),
        config_keys: Vec::new(),
        renpy_keys: Vec::new(),
        gui_keys: Vec::new(),
    };
    if let Some(entries) = value.get("labels").and_then(|v| v.as_array()) {
        index.labels = collect_string_values(entries);
    }
    if let Some(entries) = value.get("screens").and_then(|v| v.as_array()) {
        index.screens = collect_string_values(entries);
    }
    if let Some(entries) = value.get("transforms").and_then(|v| v.as_array()) {
        index.transforms = collect_string_values(entries);
    }
    if let Some(entries) = value.get("audio").and_then(|v| v.as_array()) {
        index.audio = collect_string_values(entries);
    }
    if let Some(entries) = value.get("config_keys").and_then(|v| v.as_array()) {
        index.config_keys = collect_string_values(entries);
    }
    if let Some(entries) = value.get("renpy_keys").and_then(|v| v.as_array()) {
        index.renpy_keys = collect_string_values(entries);
    }
    if let Some(entries) = value.get("gui_keys").and_then(|v| v.as_array()) {
        index.gui_keys = collect_string_values(entries);
    }
    Ok(index)
}

fn parse_definitions_index(raw: &str) -> Result<Vec<DefinitionLocation>, String> {
    let value: serde_json::Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
    let mut out = Vec::new();
    let Some(entries) = value.as_array() else {
        return Ok(out);
    };
    for entry in entries {
        let Some(obj) = entry.as_object() else {
            continue;
        };
        let Some(kind) = obj.get("kind").and_then(|v| v.as_str()) else {
            continue;
        };
        let Some(name) = obj.get("name").and_then(|v| v.as_str()) else {
            continue;
        };
        let Some(file) = obj.get("file").and_then(|v| v.as_str()) else {
            continue;
        };
        let line = obj.get("line").and_then(|v| v.as_u64()).unwrap_or(0) as u32;
        let column = obj.get("column").and_then(|v| v.as_u64()).unwrap_or(0) as u32;
        out.push(DefinitionLocation {
            kind: kind.to_owned(),
            name: name.to_owned(),
            file: file.to_owned(),
            line,
            column,
        });
    }
    Ok(out)
}

fn parse_diagnostics_index(raw: &str) -> Result<Vec<DiagnosticEntry>, String> {
    let value: serde_json::Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
    let mut out = Vec::new();
    let Some(entries) = value.as_array() else {
        return Ok(out);
    };
    for entry in entries {
        let Some(obj) = entry.as_object() else {
            continue;
        };
        let Some(severity) = obj.get("severity").and_then(|v| v.as_str()) else {
            continue;
        };
        let Some(message) = obj.get("message").and_then(|v| v.as_str()) else {
            continue;
        };
        let Some(file) = obj.get("file").and_then(|v| v.as_str()) else {
            continue;
        };
        let line = obj.get("line").and_then(|v| v.as_u64()).unwrap_or(0) as u32;
        let column = obj.get("column").and_then(|v| v.as_u64()).unwrap_or(0) as u32;
        out.push(DiagnosticEntry {
            severity: severity.to_owned(),
            message: message.to_owned(),
            file: file.to_owned(),
            line,
            column,
        });
    }
    Ok(out)
}

fn collect_string_values(values: &[serde_json::Value]) -> Vec<String> {
    let mut set = BTreeSet::new();
    for value in values {
        if let Some(string) = value.as_str() {
            set.insert(string.to_owned());
        }
    }
    set.into_iter().collect()
}

/// Refreshes the navigation index by reading `navigation.json` from the worktree and writing a compact copy to `.internal/navigation_index.json`.
///
/// This only refreshes the navigation index file. Definition and diagnostics files (`navigation_definitions.json`, `navigation_diagnostics.json`) are read directly from their source files and are not refreshed by this command.
pub fn refresh_navigation_index(worktree: &Worktree) -> Result<Option<NavigationIndex>, String> {
    let maybe_idx = RenpyExtension::read_navigation_json(worktree)?;
    if let Some(idx) = maybe_idx.clone() {
        let manifest_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        let mut out = manifest_dir.clone();
        out.push(".internal");
        std::fs::create_dir_all(&out).map_err(|e| e.to_string())?;
        out.push("navigation_index.json");
        let compact = serde_json::to_vec(&idx).map_err(|e| e.to_string())?;
        std::fs::write(&out, &compact).map_err(|e| e.to_string())?;
        return Ok(Some(idx));
    }
    Ok(None)
}

fn completion_candidates(index: &NavigationIndex, prefix: &str) -> Vec<String> {
    let pool = [
        index.labels.as_slice(),
        index.screens.as_slice(),
        index.transforms.as_slice(),
        index.audio.as_slice(),
        index.config_keys.as_slice(),
        index.renpy_keys.as_slice(),
        index.gui_keys.as_slice(),
    ]
    .into_iter()
    .flatten()
    .cloned();
    let mut out = BTreeSet::new();
    for item in pool {
        if item.starts_with(prefix) {
            out.insert(item);
        }
    }
    out.into_iter().collect()
}

fn definition_candidates(
    definitions: &[DefinitionLocation],
    query: &str,
) -> Vec<DefinitionLocation> {
    definitions
        .iter()
        .filter(|item| item.name == query || item.name.ends_with(&format!(".{query}")))
        .cloned()
        .collect()
}

fn diagnose_candidates(entries: &[DiagnosticEntry], query: &str) -> Vec<DiagnosticEntry> {
    entries
        .iter()
        .filter(|entry| {
            query.is_empty() || entry.file.contains(query) || entry.message.contains(query)
        })
        .cloned()
        .collect()
}

fn wt_or_err(worktree: Option<&Worktree>) -> Result<&Worktree, String> {
    worktree.ok_or_else(|| "worktree required".to_string())
}

impl Extension for RenpyExtension {
    fn new() -> Self {
        RenpyExtension
    }

    fn language_server_command(
        &mut self,
        _language_server_id: &zed_extension_api::LanguageServerId,
        _worktree: &Worktree,
    ) -> Result<zed_extension_api::process::Command, String> {
        Err("no language server".to_string())
    }

    fn run_slash_command(
        &self,
        command: SlashCommand,
        args: Vec<String>,
        worktree: Option<&Worktree>,
    ) -> Result<SlashCommandOutput, String> {
        match command.name.as_str() {
            "renpy.refresh_index" => {
                let wt = wt_or_err(worktree)?;
                match refresh_navigation_index(wt) {
                    Ok(Some(idx)) => Ok(SlashCommandOutput {
                        text: serde_json::to_string(&idx).map_err(|e| e.to_string())?,
                        sections: Vec::new(),
                    }),
                    Ok(None) => Ok(SlashCommandOutput {
                        text: "no navigation index found".to_string(),
                        sections: Vec::new(),
                    }),
                    Err(error) => Err(error),
                }
            }
            "renpy.completions" => {
                let wt = wt_or_err(worktree)?;
                let prefix = args.first().map(String::as_str).unwrap_or("");
                let maybe_idx = RenpyExtension::read_navigation_json(wt)?;
                let Some(idx) = maybe_idx else {
                    return Ok(SlashCommandOutput {
                        text: "[]".to_string(),
                        sections: Vec::new(),
                    });
                };
                let items = completion_candidates(&idx, prefix);
                Ok(SlashCommandOutput {
                    text: serde_json::to_string(&items).map_err(|e| e.to_string())?,
                    sections: Vec::new(),
                })
            }
            "renpy.definition" => {
                let wt = wt_or_err(worktree)?;
                let query = args.first().map(String::as_str).unwrap_or("");
                let maybe_defs = RenpyExtension::read_definitions_json(wt)?;
                let Some(defs) = maybe_defs else {
                    return Ok(SlashCommandOutput {
                        text: "[]".to_string(),
                        sections: Vec::new(),
                    });
                };
                let items = definition_candidates(&defs, query);
                Ok(SlashCommandOutput {
                    text: serde_json::to_string(&items).map_err(|e| e.to_string())?,
                    sections: Vec::new(),
                })
            }
            "renpy.diagnostics" => {
                let wt = wt_or_err(worktree)?;
                let query = args.first().map(String::as_str).unwrap_or("");
                let maybe_entries = RenpyExtension::read_diagnostics_json(wt)?;
                let Some(entries) = maybe_entries else {
                    return Ok(SlashCommandOutput {
                        text: "[]".to_string(),
                        sections: Vec::new(),
                    });
                };
                let items = diagnose_candidates(&entries, query);
                Ok(SlashCommandOutput {
                    text: serde_json::to_string(&items).map_err(|e| e.to_string())?,
                    sections: Vec::new(),
                })
            }
            _ => Err("unhandled slash command".to_string()),
        }
    }
}

register_extension!(RenpyExtension);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_navigation_index_collects_unique_sorted_values() {
        let parsed = parse_navigation_index(
            r#"{"name":"demo","version":"1","labels":["start","start","intro"],"screens":["prefs"],"transforms":[],"audio":["music"],"config_keys":["config.name"],"renpy_keys":["renpy.version"],"gui_keys":["gui.text_color"]}"#,
        )
        .expect("parse index");
        assert_eq!(parsed.name.as_deref(), Some("demo"));
        assert_eq!(parsed.version.as_deref(), Some("1"));
        assert_eq!(parsed.labels, vec!["intro", "start"]);
        assert_eq!(parsed.screens, vec!["prefs"]);
        assert_eq!(parsed.audio, vec!["music"]);
    }

    #[test]
    fn definition_candidates_match_exact_and_dotted_suffix() {
        let defs = vec![
            DefinitionLocation {
                kind: "label".to_string(),
                name: "start".to_string(),
                file: "game/a.rpy".to_string(),
                line: 1,
                column: 0,
            },
            DefinitionLocation {
                kind: "label".to_string(),
                name: "scene.start".to_string(),
                file: "game/b.rpy".to_string(),
                line: 2,
                column: 0,
            },
        ];
        let items = definition_candidates(&defs, "start");
        assert_eq!(items.len(), 2);
    }

    #[test]
    fn diagnose_candidates_filters_by_query() {
        let entries = vec![
            DiagnosticEntry {
                severity: "warning".to_string(),
                message: "filename bad".to_string(),
                file: "game/bad.rpy".to_string(),
                line: 0,
                column: 0,
            },
            DiagnosticEntry {
                severity: "warning".to_string(),
                message: "tab bad".to_string(),
                file: "game/good.rpy".to_string(),
                line: 1,
                column: 0,
            },
        ];
        let filtered = diagnose_candidates(&entries, "bad.rpy");
        assert_eq!(filtered.len(), 1);
        assert_eq!(filtered[0].file, "game/bad.rpy");
    }

    #[test]
    fn parse_helpers_reject_malformed_json() {
        assert!(parse_navigation_index("not json").is_err());
        assert!(parse_definitions_index("not json").is_err());
        assert!(parse_diagnostics_index("not json").is_err());
    }

    #[test]
    fn parse_helpers_ignore_non_arrays_and_invalid_entries() {
        assert!(parse_navigation_index(r#"{"labels":"bad"}"#).is_ok());
        assert_eq!(
            parse_definitions_index("[]").unwrap(),
            Vec::<DefinitionLocation>::new()
        );
        assert_eq!(
            parse_diagnostics_index("[]").unwrap(),
            Vec::<DiagnosticEntry>::new()
        );

        let defs = parse_definitions_index(
            r#"[{"kind":"label","name":"ok","file":"game/a.rpy","line":2,"column":3},{"kind":1,"name":"skip","file":"game/b.rpy"}]"#,
        )
        .unwrap();
        assert_eq!(defs.len(), 1);
        assert_eq!(defs[0].line, 2);

        let diags = parse_diagnostics_index(
            r#"[{"severity":"error","message":"ok","file":"game/a.rpy","line":5,"column":7},{"severity":"error","message":9,"file":"game/b.rpy"}]"#,
        )
        .unwrap();
        assert_eq!(diags.len(), 1);
        assert_eq!(diags[0].line, 5);
        assert_eq!(diags[0].column, 7);
    }
}
