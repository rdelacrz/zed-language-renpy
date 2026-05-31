const PREC = {
  ASSIGNMENT: 0,
  CALL: 1,
  ATOM: 2,
};

module.exports = grammar({
  name: "renpy",

  // Declare conflicts between label_statement and other statement types
  // that start with an identifier so Tree-sitter can resolve ambiguities.
  extras: ($) => [/[\s\f\r\t\v]+/, $.comment],

  word: ($) => $.identifier,

  rules: {
    source_file: ($) => repeat(choice($.statement, $.blank_line)),

    blank_line: ($) => prec(1, /\r?\n/),

    line_end: ($) => /\r?\n/,

    statement: ($) =>
      choice(
        $.label_statement,
        $.init_statement,
        $.python_statement,
        $.one_line_python,
        $.scene_statement,
        $.show_statement,
        $.hide_statement,
        $.show_layer_statement,
        $.jump_statement,
        $.call_statement,
        $.menu_statement,
        $.menu_item,
        $.if_statement,
        $.while_statement,
        $.for_statement,
        $.return_statement,
        $.say_statement,
        $.assignment_statement,
        $.define_statement,
        $.default_statement,
        $.transform_statement,
        $.image_statement,
        $.camera_statement,
        $.translate_statement,
        $.testcase_statement,
        $.style_statement,
        $.screen_statement,
      ),

    // Left-associative — ensures that when parsing a block, statements
    // are grouped starting from the earliest. This avoids ambiguity with
    // adjacent blocks where the parser might otherwise try to associate
    // a statement with a later block.
    block: ($) => prec.left(repeat1(choice($.statement, $.comment, $.blank_line))),

    label_statement: ($) =>
      seq("label", field("name", $.label_name), ":", $.block),
    init_statement: ($) =>
      seq("init", optional($.number), optional("python"), ":", $.block),
    python_statement: ($) => seq("python", ":", $.block),
    one_line_python: ($) => seq("$", $.python_expression, $.line_end),
    // Python expression on one line — supports both plain expressions and
    // assignment (e.g., $ x = 5). Assignment needs to be separate from the
    // main expression rule because assignment uses prec.right with a lower
    // precedence than binary expressions.
    python_expression: ($) =>
      choice(
        seq($.identifier, "=", $.expression),
        $.expression,
      ),

    scene_statement: ($) =>
      seq(
        "scene",
        choice(
          $.identifier,
          seq("expression", $.expression),
        ),
        repeat($.say_attribute),
        optional($.at_expression),
        optional($.with_clause),
        optional($.as_clause),
        optional($.onlayer_clause),
        optional($.zorder_clause),
        optional($.behind_clause),
        choice(
          seq(":", $.block),
          $.line_end,
        ),
      ),
    show_statement: ($) =>
      seq(
        "show",
        choice(
          $.identifier,
          seq("expression", $.expression),
        ),
        repeat($.say_attribute),
        optional($.at_expression),
        optional($.with_clause),
        optional($.as_clause),
        optional($.onlayer_clause),
        optional($.zorder_clause),
        optional($.behind_clause),
        choice(
          seq(":", $.block),
          $.line_end,
        ),
      ),
    hide_statement: ($) =>
      seq("hide", $.identifier, optional(seq("with", $.expression))),
    show_layer_statement: ($) =>
      seq(
        "show",
        "layer",
        $.identifier,
        optional($.at_expression),
        optional(seq(":", $.block)),
      ),
    camera_statement: ($) =>
      seq(
        "camera",
        $.identifier,
        optional($.at_expression),
        optional(seq(":", $.block)),
      ),

    jump_statement: ($) => seq("jump", $.label_name),
    call_statement: ($) =>
      choice(
        seq("call", $.label_name, optional($.from_expression)),
        seq("call", "expression", $.expression),
      ),

    menu_statement: ($) =>
      seq("menu", optional($.label_name), optional($.arguments), ":", $.block),
    menu_item: ($) =>
      choice(
        seq(
          $.string,
          optional($.arguments),
          optional($.guard_expression),
          ":",
          $.block,
        ),
        seq("set", $.expression, $.line_end),
      ),

    if_statement: ($) =>
      prec.right(
        seq(
          "if",
          $.expression,
          ":",
          $.block,
          repeat(seq("elif", $.expression, ":", $.block)),
          optional(seq("else", ":", $.block)),
        ),
      ),
    while_statement: ($) => seq("while", $.expression, ":", $.block),
    for_statement: ($) => seq("for", $.identifier, "in", $.expression, ":", $.block),
    return_statement: ($) => "return",

    say_statement: ($) => seq(optional($.expression), optional($.say_attributes), $.string, $.line_end),
    say_attributes: ($) => prec.left(repeat1($.say_attribute)),
    say_attribute: ($) => token(prec(2, /-[A-Za-z_][A-Za-z0-9_]*/)),

    assignment_statement: ($) => prec.right(PREC.ASSIGNMENT, seq($.identifier, "=", $.expression)),
    define_statement: ($) => prec.right(seq("define", $.identifier, "=", $.expression)),
    default_statement: ($) => prec.right(seq("default", $.identifier, "=", $.expression)),

    transform_statement: ($) =>
      seq("transform", $.identifier, optional($.parameters), ":", $.block),
    image_statement: ($) =>
      prec.right(
        seq(
          "image",
          $.image_name,
          optional(seq("=", $.expression)),
          optional(seq(":", $.block)),
        ),
      ),
    style_statement: ($) => seq("style", $.identifier, ":", $.block),
    translate_statement: ($) => seq("translate", $.identifier, ":", $.block),
    testcase_statement: ($) =>
      seq("testcase", optional($.identifier), ":", $.block),
    screen_statement: ($) =>
      seq("screen", $.identifier, optional($.parameters), ":", $.block),

    at_expression: ($) => prec.left(1, seq("at", commaSep($.expression))),
    with_clause: ($) => seq("with", $.expression),
    as_clause: ($) => seq("as", $.identifier),
    onlayer_clause: ($) => seq("onlayer", $.expression),
    zorder_clause: ($) => seq("zorder", $.expression),
    behind_clause: ($) => seq("behind", commaSep($.expression)),
    image_name: ($) =>
      seq($.image_name_component, repeat(seq(".", $.image_name_component))),
    image_name_component: (_) => /[A-Za-z0-9_\-]+/,

    guard_expression: ($) => seq("if", $.expression),
    from_expression: ($) => seq("from", $.identifier),

    parameter: ($) => seq($.identifier, optional(seq("=", $.expression))),
    parameters: ($) => seq("(", optional(commaSep($.parameter)), ")"),
    argument: ($) => seq(optional(seq($.identifier, "=")), $.expression),
    arguments: ($) => seq("(", optional(commaSep($.argument)), ")"),

    expression: ($) =>
      choice(
        $.identifier,
        $.number,
        $.string,
        $.call_expression,
        $.attribute_expression,
        $.list_expression,
        $.parenthesized_expression,
        $.binary_expression,
        $.unary_expression,
        $.keyword_expression,
      ),
    keyword_expression: ($) => choice("True", "False", "None"),
    call_expression: ($) =>
      prec.left(
        PREC.CALL,
        seq(
          field("function", choice($.identifier, $.attribute_expression)),
          "(",
          optional(commaSep($.expression)),
          ")",
        ),
      ),
    attribute_expression: ($) =>
      prec.left(
        seq(
          field("value", $.identifier),
          ".",
          field("attribute", $.identifier),
        ),
      ),
    list_expression: ($) => seq("[", optional(commaSep($.expression)), "]"),
    parenthesized_expression: ($) =>
      seq("(", optional(commaSep($.expression)), ")"),
    unary_expression: ($) => prec.right(seq(choice("-", "not"), $.expression)),
    binary_expression: ($) =>
      prec.left(
        1,
        seq(
          $.expression,
          choice(
            "+",
            "-",
            "*",
            "/",
            "//",
            "%",
            "and",
            "or",
            "in",
            "is",
            "==",
            "!=",
            "<",
            ">",
            "<=",
            ">=",
          ),
          $.expression,
        ),
      ),

    label_name: ($) => seq(optional(seq($.identifier, ".")), $.identifier),
    identifier: (_) => /[A-Za-z_][A-Za-z0-9_]*/,
    number: (_) => /(?:\d+\.\d*|\d+|\.\d+)/,
    string: (_) =>
      choice(
        /"([^"\\]|\\.)*"/,
        /'([^'\\]|\\.)*'/,
        /"""([\s\S]*?)"""/,
        /'''([\s\S]*?)'''/,
      ),
    comment: (_) => token(seq("#", /[^\n]*/)),
  },
});

function commaSep(rule) {
  return seq(rule, repeat(seq(",", rule)), optional(","));
}
