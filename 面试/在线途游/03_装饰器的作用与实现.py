from functools import wraps
'''
简述装饰器的作用，并实现
'''

# 装饰器的作用：当想扩展一个函数的功能，但是又不想修改原函数的代码，可以写一个装饰器，打在要扩展功能的函数上


def doublewrap(f):
    '''
    a decorator decorator, allowing the decorator to be used as:
    @decorator(with, arguments, and=kwargs)
    or
    @decorator
    '''
    @wraps(f)
    def new_dec(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # actual decorated function
            return f(args[0])
        else:
            # decorator arguments
            return lambda realf: f(realf, *args, **kwargs)
        
    return new_dec


# 扩展hello函数，能提供赞美的话
@doublewrap  # 一个可是使beautiful作为函数调用 或者变量方式调用的装饰器
def beautiful(fun, k=None):  # k为装饰器接受的参数
    @wraps(fun)
    def wrapper(name):  # name为被装饰函数中的参数
        if k:
            return fun(name) + "你好漂亮" + k
        return fun(name) + "你好漂亮。"
    return wrapper

# 原函数：只有sayhello的功能
@beautiful  # 无参数的装饰器
def hello(name):
    return  "hello" + name

result = hello("皮蛋")
print(result)

@beautiful("!")  # 有参数的装饰器
def hello(name):
    return  "hello" + name

result = hello("皮蛋")
print(result)

