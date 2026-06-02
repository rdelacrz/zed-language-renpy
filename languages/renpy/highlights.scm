; Ren'Py syntax highlighting queries
; Verified against grammar.js node types (May 2026)

; Literals
(comment) @comment
(number) @number
(string) @string
(keyword_expression) @constant.builtin

; === Statement nodes (each captures its keyword token for styling) ===

; Declarations / blocks
(label_statement) @keyword.function
(init_statement) @keyword.function
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
(if_statement) @keyword.control
(while_statement) @keyword.control
(for_statement) @keyword.control
(menu_statement) @keyword.control
(call_statement) @keyword.control
(jump_statement) @keyword.control
(return_statement) @keyword.control

; Definitions
(transform_statement) @keyword.function
(screen_statement) @keyword.function
(style_statement) @keyword.function
(testcase_statement) @keyword.function
(translate_statement) @keyword.function
(define_statement) @keyword.function
(default_statement) @keyword.function

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
(screen_statement . (identifier) @name)
(transform_statement . (identifier) @name)
(style_statement . (identifier) @name)
(testcase_statement . (identifier) @name)
(translate_statement . (identifier) @name)

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