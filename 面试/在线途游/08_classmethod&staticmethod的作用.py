'''
静态方法：staticmethod:一个不依托于类 也不依托于实例的函数，类与实例都可以调用
类方法：可以操作类属性，且不用实例多个对象直接能用类调用的方法，也可实例对象调用
'''
# 类外有个函数，在类内被调用了, 也可以将此方法写成静态方法 在类内部用实例或者类调用
def out_fun():
    print("我是定义在类外部的函数")

class A(object):
    a = 0
    # 静态方法 统计类方法被调用的次数
    @classmethod
    def get_a(cls):
        A.a +=1
        print(A.a)

    def call_out_fun(self):
        out_fun()
        self.out_fun()  # 实例调用方式
        A.out_fun()  # 类调用方式

    @staticmethod
    def out_fun():
        print("我是定义在类内部的静态方法")

A.get_a()  # 类调用类方法
A().get_a()  # 实例调用类方法
A().call_out_fun()  # 调用静态方法

