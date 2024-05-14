"""
 Equipe da Canoa -- 2024

 mgd 2024-05-13
 ----------------------
 """

from flask import request


# { is_method_get =========================================
# mgd 2024.03.21
def is_method_get():
   is_get= True
   if request.method == 'POST':
      is_get= False
   elif not is_get:
      # if not is_get then is_post, there is no other possibility
      raise ValueError('Unexpected request method.')

   return is_get
# is_method_get } -----------------------------------------

# { get_input_text ========================================
def get_input_text(name: str) -> str:
    text = request.form.get(name)
    return to_str(text)

# get_input_text } ----------------------------------------

# { to_str ================================================
def to_str(s: str):
    return '' if s is None else s.strip()

# to_str } ------------------------------------------------
