const assert = require("assert");
const fs = require("fs");
const { execFileSync } = require("child_process");

function runGenerate() {
  return execFileSync("npx", ["tree-sitter", "generate"], {
    cwd: __dirname,
    stdio: ["ignore", "pipe", "pipe"],
    encoding: "utf8",
  });
}

function assertGeneratedArtifacts() {
  assert(
    fs.existsSync(__dirname + "/src/grammar.json"),
    "missing src/grammar.json",
  );
  assert(fs.existsSync(__dirname + "/src/scanner.c"), "missing src/scanner.c");
}

try {
  const output = runGenerate();
  assertGeneratedArtifacts();
  if (output) {
    console.log(output.trim());
  }
  console.log("tree-sitter-renpy generation smoke test passed");
} catch (error) {
  console.error(error && error.stdout ? error.stdout : "");
  console.error(error && error.stderr ? error.stderr : "");
  console.error(error && error.stack ? error.stack : String(error));
  process.exit(1);
}
