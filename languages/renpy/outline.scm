; Outline / symbol view
; Each rule captures a named structural element. @name provides the label text,
; @item marks it as a top-level symbol in the outline panel.

(label_statement name: (label_name) @name) @item
(screen_statement name: (identifier) @name) @item
(transform_statement name: (identifier) @name) @item
(style_statement name: (identifier) @name) @item
(testcase_statement name: (identifier) @name) @item
(translate_statement name: (identifier) @name) @item
(image_statement) @item