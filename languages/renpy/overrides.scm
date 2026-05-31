; Override query — controls which syntax nodes can participate in
; completion and rename operations.

; Strings should complete word characters including - _ and .
((string) @text
  (#set! completion_query_characters "-_."))

; Also allow completion within identifiers (for rename support)
((identifier) @text
  (#set! completion_query_characters "-_"))