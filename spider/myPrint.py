def myPrint(x,indent = 2,recursion_times=0):
    '''以比较直观、漂亮的形式输出 x ，目前 x 可以是列表、字典、元组
        indent 是一个整数，是每个自结构的括号距离最左边的距离
    '''

    LineBreak = r'\r\n'
    if isinstance(x,dict):
        print((indent*recursion_times) * ' ' + '{')
        for key,value in x.items():
            if isinstance(value,(dict,list,tuple)):
                print(' ' * (indent*(recursion_times+1)) + repr(key),':')
                myPrint(value,indent,recursion_times+1)
            else:
                if not isinstance(value,bytes):
                    print(' ' * (indent*(recursion_times+1)) + repr(key),':',repr(value),',')
                else:
                    print(' ' * (indent*(recursion_times+1)) + repr(key),':','bytes-content!',',')          
        print((indent*recursion_times) * ' ' + '},')
    elif isinstance(x,list):
        print((indent*recursion_times) * ' ' + '[')
        for item in x:
            if isinstance(item,(dict,list,tuple)):
                myPrint(item,indent,recursion_times+1)
            else:
                if not isinstance(item,bytes):
                    print(' ' * (indent*(recursion_times+1)) + repr(item),',')
                else:
                    print(' ' * (indent*(recursion_times+1)) + 'bytes-content!',',')
        print(' ' * (indent*recursion_times) + '],')
    elif isinstance(x,tuple):
        print((indent*recursion_times) * ' ' + '(')
        for item in x:
            if isinstance(item,(dict,list,tuple)):
                myPrint(item,indent,recursion_times+1)
            else:
                if not isinstance(item,bytes):
                    print(' ' * (indent*(recursion_times+1)) + repr(item),',')
                else:
                    print(' ' * (indent*(recursion_times+1)) + 'bytes-content!',',')
        print(' ' * (indent*recursion_times) + '),')
    else:
        print("error! %s found!"%type(x))