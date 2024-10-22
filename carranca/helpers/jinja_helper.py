#
#
# mgd 2024-06-21

# cSpell:ignore

#mark a string as a jinja text, a text that will be parsed before rendering
_jinja_pre_template_mark = '^'

def _jinja_pre_template(val: str) -> str:
    from ..Shared import shared
    text = val
    try:
        # Create a template from the value
        template = shared.app.jinja_env.from_string(val)
        text= template.render()

        return text
    except Exception as e:
        print(f"Error rendering template [{val}]: {e}")

    return text

def process_pre_templates(texts: dict, mark: str = _jinja_pre_template_mark):
    """
    Process the dictionary to apply _jinjaText where necessary
    Original idea by mgd

    Example:
        # A typical jinja texts to use on a template, except for `About`,
        # that starts and ends with the (default) jinja_template_mark: ^
        texts = {
            'fruit': 'lucuma'
            , 'stone': 'meteoric'
            , 'about': '^About {{ app_name() }} version {{ app_ver() }}^'
        }
        processed_texts = process_pre_templates(texts)
        print(processed_texts['about']) # -> "About Canoa version 21.8"
    """
    for key, text in texts.items():
        if len(text) > 7 and text[0] == mark and text[0] == text[-1]:
            pre_template = text.strip(mark)
            value = _jinja_pre_template(pre_template)
            texts[key] = value
    return texts

#eof