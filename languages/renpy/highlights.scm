; Ren'Py syntax highlighting queries
; Verified against grammar.js node types (May 2026)

; Literals
(comment) @comment
(number) @number
(string) @string
(keyword_expression) @constant.builtin

; === Statement nodes (each captures its keyword token for styling) ===

; Declarations / blocks
(label_statement) @keyword
(init_statement) @keyword
(python_statement) @keyword
(one_line_python) @keyword

; Image and scene management
(scene_statement) @keyword
(show_statement) @keyword
(show_layer_statement) @keyword
(hide_statement) @keyword
(camera_statement) @keyword
(image_statement) @keyword

; Flow control
(if_statement) @keyword
(while_statement) @keyword
(for_statement) @keyword
(menu_statement) @keyword
(call_statement) @keyword
(jump_statement) @keyword
(return_statement) @keyword

; Definitions
(transform_statement) @keyword
(screen_statement) @keyword
(style_statement) @keyword
(testcase_statement) @keyword
(translate_statement) @keyword
(define_statement) @keyword
(default_statement) @keyword

; Assignment
(assignment_statement) @keyword

; Sub-expressions acting as keywords/operators
(guard_expression) @keyword
(from_expression) @keyword
(at_expression) @keyword
(with_clause) @keyword
(as_clause) @keyword
(onlayer_clause) @keyword
(zorder_clause) @keyword
(behind_clause) @keyword

; Say attributes (e.g., character -flag1 -flag2 "Dialogue")
(say_attribute) @keyword

; === Named identifiers ===

; Label, screen, transform, style, testcase, translate names
(label_statement name: (label_name) @name)
(screen_statement name: (identifier) @name)
(transform_statement name: (identifier) @name)
(style_statement name: (identifier) @name)
(testcase_statement name: (identifier) @name)
(translate_statement name: (identifier) @name)

; Function calls
(call_expression function: (identifier) @function)

; Attribute access (e.g., foo.bar)
(attribute_expression attribute: (identifier) @property)

; Variable definitions — the left-hand side of assignments
(assignment_statement . (identifier) @variable)
(define_statement . (identifier) @variable)
(default_statement . (identifier) @variable)

; Fallback: any bare identifier
(identifier) @variable

; Punctuation
(line_end) @punctuation.delimiter

; Blank lines (whitespace markers)
(blank_line) @comment