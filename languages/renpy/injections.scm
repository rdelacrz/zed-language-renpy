; Inject complete Python blocks together so functions/classes retain their context.
((indented_block) @injection.content
 (#set! injection.language "python")
 (#set! injection.include-children))

; Only Python-bearing statements: a plain `init:` block remains Ren'Py.
([(python_line (python_content) @injection.content)
  (define_statement value: (python_content) @injection.content)
  (default_statement value: (python_content) @injection.content)
  (return_statement value: (python_content) @injection.content)
  (image_statement displayable: (python_content) @injection.content)]
 (#set! injection.language "python"))

((python_expression) @injection.content
 (#set! injection.language "python"))
((bracketed) @injection.content
 (#set! injection.language "python"))
