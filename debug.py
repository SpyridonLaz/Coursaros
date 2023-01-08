#!/usr/bin/env python3 
from inspect import currentframe, getframeinfo
from pathlib import Path
class debugger():
    increment = 0
    

    def __call__(self,message,*args):
        self.increment +=1

        s = "{filename} #:{increment}, Line #{line} :{message}".format(filename= Path(getframeinfo(currentframe()).filename).name,line = getframeinfo(currentframe()).lineno,message=message,increment=self.increment)

        return print(s )
