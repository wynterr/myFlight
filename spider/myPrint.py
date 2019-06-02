def myPrint(x,indent = 0,lineBreakForm = 'string',printWhiteSpace = True):
    '''以比较直观、漂亮的形式输出 x ，目前 x 可以是列表、字典、元组
        有三个参数：
        indent 是一个整数，是输出内容整体距离左边的距离
        lineBreakForm 确定换行符的输出形式，默认的 'string' 值表示输出反斜杠加 r 或 n ，'sign' 值表示输出换行
        printWhiteSpace 确定是否输出空白字符
    '''
    LineBreak = r'\r\n'
    if isinstance(x,dict):
        print(indent * ' ' + '{')
        for key,value in x.items():
            if isinstance(value,(dict,list)):
                print(' ' * (indent+4) + repr(key),':')
                myPrint(value,indent + 4)
            else:
                print(' ' * (indent+4) + repr(key),':',repr(value),',')
        print(indent * ' ' + '},')
    elif isinstance(x,list):
        print(indent * ' ' + '[')
        for item in x:
            if isinstance(item,(dict,list)):
                myPrint(item,indent + 4)
            else:
                print(' ' * (indent+4) + repr(item),',')
        print(' ' * indent + '],')
    elif isinstance(x,tuple):
        print(indent * ' ' + '(')
        for item in x:
            if isinstance(item,(dict,list)):
                myPrint(item,indent + 4)
            else:
                print(' ' * (indent+4) + repr(item),',')
        print(' ' * indent + '),')
    else:
        print("error! %s found!"%type(x))