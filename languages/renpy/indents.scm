; Capture the body as the indent range and move its start back to the colon.
; Capturing a body as @end would stop at its first line, losing nested indentation.
(_ ":" @start
   [(block) (indented_block) (element_block) (atl_block) (translate_strings_block)] @indent)

; Menus have inline children rather than a separate body node.
(menu_statement) @indent
