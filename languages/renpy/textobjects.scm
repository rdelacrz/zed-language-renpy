(label_statement (block) @function.inside) @function.around
(screen_statement body: (element_block) @class.inside) @class.around
(transform_statement body: (atl_block) @function.inside) @function.around
(python_block (indented_block) @function.inside) @function.around
(comment)+ @comment.around
