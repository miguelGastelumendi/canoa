"""
#main.py
   Main Module following the Application Factory Pattern

   Equipe da Canoa -- 2024
   mgd 2024-10-03
"""

print(__name__)


from carranca import create_app

app = create_app()

if __name__ == "__main__":
    print(__name__)
    address = app.shared.address
    app.run(host=address.host, port=address.port, debug=app.config.debug)
