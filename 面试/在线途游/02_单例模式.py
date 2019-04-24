'''
    简述单例模式的作用与应用场景，并实现单例模式
'''
# 单例模式：只有一个实例对象
# 核心作用：保证一个类只有一个实例，并且提供一个访问该实例的全局访问点
# 应用场景：1. 需要生成唯一序列的环境
#         2. 需要频繁实例化然后销毁的对象。
#         3. 创建对象时耗时过多或者耗资源过多，但又经常用到的对象。
#         4. 方便资源相互通信的环境


class Single(object):
    __isSingle = None  # 用来标志实例是否已经被创建
    # __new__方法在创建实例前被调用
    def __new__(cls, *args, **kwargs):
        # 如果实例没有被创建,则调用父类的方法, 创建当前对象的实例
        if not cls.__isSingle:
            # cls.__isSingle = super(Single, cls).__new__(cls)  # py2写法
            cls.__isSingle = super().__new__(cls)  # py3写法
            return cls.__isSingle
        # 当前对象已经创建过实例，返回这个实例对象
        else:
            return cls.__isSingle

a = Single()  # <__main__.Single object at 0x0000023FBA6D16D8>
b = Single()  # <__main__.Single object at 0x0000023FBA6D16D8>

print(a, b)