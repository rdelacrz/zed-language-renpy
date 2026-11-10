; Keep these node names in sync with the pinned grammar in extension.toml.
(identifier) @variable
(label_statement name: (label_name) @function)
(menu_statement name: (label_name) @function)
(jump_statement target: (label_name) @function)
(call_statement target: (label_name) @function)
(call_statement from: (label_name) @label)
(screen_statement name: (identifier) @function)
(show_screen_statement name: (identifier) @function)
(hide_screen_statement name: (identifier) @function)
(call_screen_statement name: (identifier) @function)
(transform_statement name: (dotted_name) @function)
(testcase_statement name: (identifier) @function)
(style_statement name: (identifier) @type)
(style_statement parent: (identifier) @type)
(define_statement name: (variable_name) @variable)
(default_statement name: (variable_name) @variable)
(image_name) @constant
(image_specifier) @constant
(say_attribute) @attribute
(translate_statement language: (identifier) @attribute)
(translate_statement id: (identifier) @label)
(user_statement name: (identifier) @keyword)

; Screen/ATL/style blocks expose generic elements, not opaque body lines.
(element name: (identifier) @property)
((element name: (identifier) @keyword)
 (#match? @keyword "^(add|bar|button|drag|draggroup|fixed|frame|grid|has|hbox|hotbar|hotspot|image|imagebutton|imagemap|input|key|label|mousearea|null|on|side|text|textbutton|timer|transform|vbar|vbox|viewport|vpgrid|window|use|transclude|if|elif|else|for|showif|pass|break|continue|animation|block|choice|contains|event|function|parallel|repeat|time|warp|pause|linear|ease|easein|easeout|group|attribute|always)$"))
((element (identifier) @keyword)
 (#match? @keyword "^(if|else|in|not|and|or|at|as)$"))
((identifier) @boolean
 (#match? @boolean "^(True|False)$"))
((identifier) @constant.builtin
 (#eq? @constant.builtin "None"))

["label" "menu" "jump" "call" "return" "pass" "if" "elif" "else"
 "while" "init" "python" "in" "define" "default" "image" "scene"
 "show" "hide" "with" "at" "as" "behind" "onlayer" "zorder"
 "expression" "layer" "camera" "window" "auto" "pause" "play"
 "queue" "stop" "voice" "sustain" "set" "from" "rpy" "fadein"
 "fadeout" "volume" "loop" "noloop" "if_changed" "screen" "transform"
 "style" "is" "translate" "strings" "old" "new" "layeredimage"
 "testcase" "nvl" "clear" "early" "offset" "id" "$"] @keyword
["True" "False"] @boolean
["=" "+=" "|=" "-" "@"] @operator
(operator) @operator
[":" "." ","] @punctuation.delimiter
["[" "]"] @punctuation.bracket
(string) @string
(number) @number
(comment) @comment
(interpolation) @variable.special
(text_tag) @tag
(escape_sequence) @string.escape
