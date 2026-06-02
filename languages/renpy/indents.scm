; Indentation rules: any statement that introduces a block (colon + block)
; should trigger increased indentation for its children.

(label_statement) @indent
(init_statement
  (python_modifier)?
) @indent
(python_statement
  (block)?
) @indent
(screen_statement) @indent
(show_statement) @indent
(scene_statement) @indent
(show_layer_statement) @indent
(camera_statement) @indent
(transform_statement) @indent
(style_statement) @indent
(image_statement) @indent
(if_statement
  (block
    (block_statement) @indent
  )?
  (elif_clause
    (block
      (block_statement) @indent
    )?
  )?
  (else_clause
    (block
      (block_statement) @indent
    )?
  )?
) @indent
(while_statement) @indent
(for_statement) @indent
(menu_statement
  (block
    (block_statement) @indent
  )?
) @indent
(testcase_statement) @indent
(translate_statement) @indent

; Dialogue with continuation should indent the following line.
(say_statement) @indent

; Screen language blocks and widgets.
(
  (screen_statement
    (screen_body
      (block
        (block_statement
          [
            (hbox_statement)
            (vbox_statement)
            (fixed_statement)
            (grid_statement)
            (frame_statement)
            (window_statement)
            (button_statement)
            (textbutton_statement)
            (imagebutton_statement)
            (viewport_statement)
            (scroll_statement)
          ] @indent
        )
      )
    )
  )
)

; ATL blocks nested inside show/scene/image statements when followed by a colon.
(
  [
    (show_statement
      (atl_block)
    )
    (scene_statement
      (atl_block)
    )
    (image_statement
      (atl_block)
    )
  ]
) @indent

; Statements that should not continue a block.
(return_statement) @outdent
(jump_statement) @outdent
(call_statement) @outdent

; Explicit end captures for block terminators where applicable.
(block) @end
(block_statement) @end
(screen_body) @end
(atl_block) @end