# src/utils.py
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []
    current_width = 0

    for word in words:
        word_surface = font.render(word, True, (240, 240, 242))  # WHITE
        word_width = word_surface.get_width()

        if current_width + word_width <= max_width:
            current_line.append(word)
            current_width += word_width + font.render(' ', True, (240, 240, 242)).get_width()
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width + font.render(' ', True, (240, 240, 242)).get_width()

    if current_line:
        lines.append(' '.join(current_line))

    return lines