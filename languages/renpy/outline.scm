; Outline / symbol view
; Each rule captures a named structural element. @name provides the label text,
; @item marks it as a top-level symbol in the outline panel.
; @context and @context.extra add hierarchy/detail, while @annotation carries
; doc comments for AI-assisted code mods.

((comment) @annotation
  . (label_statement name: (label_name) @name) @item)
((comment) @annotation
  . (screen_statement name: (identifier) @name) @item)
((comment) @annotation
  . (transform_statement name: (identifier) @name) @item)
((comment) @annotation
  . (style_statement name: (identifier) @name) @item)
((comment) @annotation
  . (testcase_statement name: (identifier) @name) @item)
((comment) @annotation
  . (translate_statement name: (identifier) @name) @item)
((comment) @annotation
  . (image_statement) @item)

(init_statement
  (label_statement name: (label_name) @name) @item
  @context)
(init_statement
  (screen_statement name: (identifier) @name) @item
  @context)
(init_statement
  (transform_statement name: (identifier) @name) @item
  @context)
(init_statement
  (style_statement name: (identifier) @name) @item
  @context)
(init_statement
  (testcase_statement name: (identifier) @name) @item
  @context)
(init_statement
  (translate_statement name: (identifier) @name) @item
  @context)
(init_statement
  (image_statement) @item
  @context)

(label_statement name: (label_name) @name) @item
(screen_statement name: (identifier) @name) @item
(transform_statement name: (identifier) @name) @item
(style_statement name: (identifier) @name) @item
(testcase_statement name: (identifier) @name @context.extra)
(testcase_statement name: (identifier) @name) @item
(translate_statement name: (identifier) @name) @item
(image_statement) @item
(define_statement . (identifier) @name) @item
(default_statement . (identifier) @name) @item
(init_statement) @item