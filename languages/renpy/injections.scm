; Language injection rules
; When a Ren'Py block contains Python code, inject the Python grammar.

; Explicit "python:" block
(python_statement (block) @injection.content
  (#set! injection.language "python"))

; "init python:" block (note: plain "init:" may contain Ren'Py script, not Python)
; We only inject when the 'python' keyword is present.
(init_statement
  (block) @injection.content
  (#set! injection.language "python"))

; Screen language — the block inside a screen uses Python-like syntax
(screen_statement (block) @injection.content
  (#set! injection.language "python"))

; Transform blocks are Python
(transform_statement (block) @injection.content
  (#set! injection.language "python"))

; Style blocks
(style_statement (block) @injection.content
  (#set! injection.language "python"))

; Testcase blocks
(testcase_statement (block) @injection.content
  (#set! injection.language "python"))

; Translate blocks
(translate_statement (block) @injection.content
  (#set! injection.language "python"))