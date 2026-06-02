; Runnable entry points for Ren'Py projects.
; Zed shows a Run gutter icon for captures named @run.
; @_name marks the keyword token introducing the runnable declaration.
;
; Prefer conventional game entry points first.
((label_statement
  name: (label_name) @run
  (#eq? @run "start"))
  (#set! runnable))

((label_statement
  name: (label_name) @run
  (#eq? @run "main_menu"))
  (#set! runnable))

; Allow any top-level label as a runnable candidate when it is not nested in an init block.
((statement
  (label_statement
    name: (label_name) @run)
  (#set! runnable))
  @_name)
