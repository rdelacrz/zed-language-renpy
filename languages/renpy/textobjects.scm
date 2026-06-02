; Vim text objects for Ren'Py
; Group major structural blocks for ]m/[m and af/if navigation.

; Functions: label, screen, transform blocks.
(
  [
    (label_statement)
    (screen_statement)
    (transform_statement)
  ] @function.around
)

(
  [
    (label_statement
      body: (block) @function.inside
    )
    (screen_statement
      body: (block) @function.inside
    )
    (transform_statement
      body: (block) @function.inside
    )
  ]
)

; Classes: init blocks.
(init_statement) @class.around
(init_statement body: (block) @class.inside)

; Comment blocks: adjacent comment lines.
((comment)+ @comment.around)
