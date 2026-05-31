; Indentation rules: any statement that introduces a block (colon + block)
; should trigger increased indentation for its children.

(label_statement) @indent
(init_statement) @indent
(python_statement) @indent
(screen_statement) @indent
(show_statement) @indent
(scene_statement) @indent
(show_layer_statement) @indent
(camera_statement) @indent
(transform_statement) @indent
(style_statement) @indent
(image_statement) @indent
(if_statement) @indent
(while_statement) @indent
(for_statement) @indent
(menu_statement) @indent
(testcase_statement) @indent
(translate_statement) @indent

; Statements that end a block and should decrease indentation
; (return, jump, call are typically at the indentation level of the block they're in)
; Note: Zed's indent system auto-handles dedent on non-indent lines, so we only
; need explicit @outdent for exceptional cases. Uncomment if needed:
; (return_statement) @outdent