font_sizes = [96, 64, 48, 24, 18]

fonts = {}
characters_per_line_for_font = {
    96 : 14,
    64 : 22,
    48 : 32,
    24 : 14,
    18 : 14,
}

def break_message(message, font=0):
    font_size = font_sizes[font]
    max_length = characters_per_line_for_font[font_size]
    broken = ''
    lines = 0
    index = 0
    if ' ' not in message:
        return (message, font_size)
    while index < len(message) - max_length:
        next_index = message.rindex(' ', index, index+max_length)
        if index == next_index:
            next_index = message.index(' ', index+max_length)
        line = message[index:next_index].strip()
        broken += (line+'\n')
        lines += 1
        index = next_index
        if 3 < lines:
            return break_message(message, font+1)
    broken += message[index:]
    return (broken, font_size)

print(break_message('does harold smush?'))
print(break_message('does harold se sdf sdf?'))
print(break_message('does harold asdf sdkfa sdfj askdjf asdfas?'))
print(break_message('does harold asdf?'))
print(break_message('does?'))
print(break_message('Ok why did kiss Ross just punch Chris Ross in the penis'))
print(break_message('It\'s not conventional, but no sex'))
print(break_message('Please, Wallace...call me "Toddy" (a British slang term for an attractive, high society dame)'))