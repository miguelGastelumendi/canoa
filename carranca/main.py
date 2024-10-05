

print(__name__)

from Shared import Shared
from carranca import create_app

app = create_app()



if __name__ == "__main__":
   print(__name__)
   app.run() # host=address.host, port=address.port, debug=app_config.DEBUG)

