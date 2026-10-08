'''
This file contains functions that work on entire documents at a time
(and not line-by-line).
'''

from markdown_compiler.util.line_functions import (
    compile_headers,
    compile_strikethrough,
    compile_bold_stars,
    compile_bold_underscore,
    compile_italic_star,
    compile_italic_underscore,
    compile_code_inline,
    compile_images,
    compile_links,
)


def compile_lines(text):
    r'''
    Apply all markdown transformations to the input text.

    NOTE:
    This function calls all of the functions you created above to convert the full markdown file into HTML.
    This function also handles multiline markdown like <p> tags and <pre> tags;
    because these are multiline commands, they cannot work with the line-by-line style of commands above.

    NOTE:
    The doctests are divided into two sets.
    The first set of doctests below show how this function adds <p> tags and calls the functions above.
    Once you implement the functions above correctly,
    then this first set of doctests will pass.

    NOTE:
    For your assignment, the most important thing to take away from these test cases is how multiline tests can be formatted.

    >>> compile_lines('This is a **bold** _italic_ `code` test.\nAnd *another line*!\n')
    '<p>\nThis is a <b>bold</b> <i>italic</i> <code>code</code> test.\nAnd <i>another line</i>!\n</p>'

    >>> compile_lines("""
    ... This is a **bold** _italic_ `code` test.
    ... And *another line*!
    ... """)
    '\n<p>\nThis is a <b>bold</b> <i>italic</i> <code>code</code> test.\nAnd <i>another line</i>!\n</p>'

    >>> print(compile_lines("""
    ... This is a **bold** _italic_ `code` test.
    ... And *another line*!
    ... """))
    <BLANKLINE>
    <p>
    This is a <b>bold</b> <i>italic</i> <code>code</code> test.
    And <i>another line</i>!
    </p>

    >>> print(compile_lines("""
    ... *paragraph1*
    ...
    ... **paragraph2**
    ...
    ... `paragraph3`
    ... """))
    <BLANKLINE>
    <p>
    <i>paragraph1</i>
    </p>
    <p>
    <b>paragraph2</b>
    </p>
    <p>
    <code>paragraph3</code>
    </p>

    NOTE:
    This second set of test cases tests multiline code blocks.

    HINT:
    In order to get some of these test cases to pass,
    you will have to both add new code and remove some of the existing code that I provide you.

    >>> print(compile_lines("""
    ... ```
    ... x = 1*2 + 3*4
    ... ```
    ... """))
    <BLANKLINE>
    <pre>
    x = 1*2 + 3*4
    </pre>
    <BLANKLINE>

    >>> print(compile_lines("""
    ... Consider the following code block:
    ... ```
    ... x = 1*2 + 3*4
    ... ```
    ... """))
    <BLANKLINE>
    <p>
    Consider the following code block:
    <pre>
    x = 1*2 + 3*4
    </pre>
    </p>

    >>> print(compile_lines("""
    ... Consider the following code block:
    ... ```
    ... x = 1*2 + 3*4
    ... print('x=', x)
    ... ```
    ... And here's another code block:
    ... ```
    ... print(this_is_a_variable)
    ... ```
    ... """))
    <BLANKLINE>
    <p>
    Consider the following code block:
    <pre>
    x = 1*2 + 3*4
    print('x=', x)
    </pre>
    And here's another code block:
    <pre>
    print(this_is_a_variable)
    </pre>
    </p>

    >>> print(compile_lines("""
    ... ```
    ... for i in range(10):
    ...     print('i=',i)
    ... ```
    ... """))
    <BLANKLINE>
    <pre>
    for i in range(10):
        print('i=',i)
    </pre>
    <BLANKLINE>

    NOTE:
    This third set of test cases is for the extra-credit ordered list feature.
    A line like "1. this" becomes one <li> entry inside an <ol> list.
    Consecutive numbered lines are grouped into a single <ol>...</ol> list.

    >>> print(compile_lines("""
    ... 1. this
    ... """))
    <BLANKLINE>
    <ol><li>this</li></ol>

    >>> print(compile_lines("""
    ... 1. this
    ... 2. is
    ... 3. a
    ... 4. list
    ... """))
    <BLANKLINE>
    <ol><li>this</li><li>is</li><li>a</li><li>list</li></ol>

    >>> print(compile_lines("""
    ... Here is a list:
    ... 1. this
    ... 2. is
    ... 3. a
    ... 4. list
    ... """))
    <BLANKLINE>
    <p>
    Here is a list:
    </p>
    <ol><li>this</li><li>is</li><li>a</li><li>list</li></ol>
    '''
    lines = text.split('\n')
    new_lines = []
    in_paragraph = False
    in_code = False
    in_list = False
    list_html = ''
    for raw_line in lines:
        stripped = raw_line.strip()

        # Fenced code blocks preserve their original indentation and
        # newlines, so they are handled before any stripping/markdown
        # transformations are applied to the rest of the line.
        if stripped.startswith('```'):
            if in_list:
                new_lines.append('<ol>' + list_html + '</ol>')
                in_list = False
                list_html = ''
            if in_code:
                in_code = False
                new_lines.append('</pre>')
            else:
                in_code = True
                new_lines.append('<pre>')
            continue
        if in_code:
            new_lines.append(raw_line)
            continue

        # a blank line ends whatever paragraph or list is currently open
        if stripped == '':
            if in_list:
                new_lines.append('<ol>' + list_html + '</ol>')
                in_list = False
                list_html = ''
                continue
            if in_paragraph:
                new_lines.append('</p>')
                in_paragraph = False
            else:
                new_lines.append('')
            continue

        # check if this line is a numbered list item, like "1. this"
        item_text = get_list_item_text(stripped)
        if item_text is not None:
            if not in_list:
                if in_paragraph:
                    new_lines.append('</p>')
                    in_paragraph = False
                in_list = True
                list_html = ''
            list_html = list_html + '<li>' + item_text + '</li>'
            continue

        # a normal line ends any list that was open
        if in_list:
            new_lines.append('<ol>' + list_html + '</ol>')
            in_list = False
            list_html = ''

        line = stripped
        if line[0] != '#' and not in_paragraph:
            in_paragraph = True
            line = '<p>\n' + line
        line = compile_headers(line)
        line = compile_strikethrough(line)
        line = compile_bold_stars(line)
        line = compile_bold_underscore(line)
        line = compile_italic_star(line)
        line = compile_italic_underscore(line)
        line = compile_code_inline(line)
        line = compile_images(line)
        line = compile_links(line)
        new_lines.append(line)

    # close a list that was never followed by a blank line
    if in_list:
        new_lines.append('<ol>' + list_html + '</ol>')

    new_text = '\n'.join(new_lines)
    return new_text


def get_list_item_text(line):
    '''
    If line looks like a numbered list item (for example "1. this"),
    return the text after the number and period.
    Otherwise, return None.
    '''
    dot_position = line.find('.')
    if dot_position == -1:
        return None

    number_part = line[:dot_position]
    if number_part == '':
        return None

    for character in number_part:
        if not character.isdigit():
            return None

    # the period must be immediately followed by a space
    after_dot = dot_position + 1
    if after_dot >= len(line) or line[after_dot] != ' ':
        return None

    return line[after_dot + 1:]


def markdown_to_html(markdown, add_css):
    '''
    Convert the input markdown into valid HTML,
    optionally adding CSS formatting.

    NOTE:
    This function is separated out from the `compile_lines` function so that the doctests are much simpler.
    In particular, by splitting these functions in two,
    there's no need to add all of the HTML boilerplate code to the doctests in `compile_lines`.

    NOTE:
    The code for this function is simple enough that we don't even have a "real" doctest.
    The only purpose of this doctest is to run the function and ensure that there are no errors.
    The `assert` statement raises AssertionError when its condition is false.
    A passing assertion produces no output.

    >>> assert(markdown_to_html('this *is* a _test_', False))
    >>> assert(markdown_to_html('this *is* a _test_', True))
    '''

    html = '''
<html>
<head>
    <style>
    ins { text-decoration: line-through; }
    </style>
    '''
    if add_css:
        html += '''
<link rel="stylesheet" href="https://izbicki.me/css/code.css" />
<link rel="stylesheet" href="https://izbicki.me/css/default.css" />
        '''
    html += '''
</head>
<body>
    ''' + compile_lines(markdown) + '''
</body>
</html>
    '''
    return html


def minify(html):
    r'''
    Collapse whitespace in a plain-text sample.
    This exercise demonstrates minification; do not apply it to a complete HTML
    page because whitespace inside <pre> elements must survive.

    NOTE:
    When we transfer HTML files over the internet,
    we'd like them to be as small as possible in order to save bandwidth and make the webpage load faster.
    Minifying html documents is an important step for webservers.
    A real HTML minifier must know which whitespace affects the page.
    Here we practice the string operation separately from the file exporter.

    >>> minify('       ')
    ''
    >>> minify('   a    ')
    'a'
    >>> minify('   a    b        c    ')
    'a b c'
    >>> minify('a b c')
    'a b c'
    >>> minify('a\nb\nc')
    'a b c'
    >>> minify('a \nb\n c')
    'a b c'
    >>> minify('a\n\n\n\n\n\n\n\n\n\n\n\n\n\nb\n\n\n\n\n\n\n\n\n\n')
    'a b'
    '''
    # split() with no arguments breaks the text into a list of words,
    # treating any run of spaces/newlines/tabs as a single separator
    words = html.split()

    result = ''
    for word in words:
        if result == '':
            result = word
        else:
            result = result + ' ' + word
    return result


def convert_file(input_file, add_css):
    '''
    Convert the input markdown file into an HTML file.
    If the input filename is `README.md`,
    then the output filename will be `README.html`.

    NOTE:
    The project's command-line check exercises file reading, compilation, and
    writing together. Inspect a generated code block as well as the helper tests.
    '''

    # validate that the input file is a markdown file
    if input_file[-3:] != '.md':
        raise ValueError('input_file does not end in .md')

    # load the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        markdown = f.read()

    # generate the HTML from the Markdown
    html = markdown_to_html(markdown, add_css)
    # Keep code-block newlines and indentation in the saved page.

    # write the output file
    with open(input_file[:-2] + 'html', 'w', encoding='utf-8') as f:
        f.write(html)
