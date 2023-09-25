# -*- encoding: utf-8 -*-
from datetime import datetime
class Log():
    def __init__(self, fname: str):
        self.fname = fname
        self.buffer = ''

    def log(self, text: str):
        msg = f'{datetime.now().strftime("%m/%d/%Y, %H:%M:%S.%f")} {text}\n'
        if self.fname != '':
            with open(self.fname,mode='w') as logFile:
                logFile.write(msg)
        print(msg)



