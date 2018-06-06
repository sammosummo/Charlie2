class Test(object):

    def __init__(self):
        self.attrib = 'hello'

    def _decorator(foo):
        def magic(self) :
            print("start magic", self.attrib)
            self.attrib = 'bye'
            foo(self)
            print("end magic")
        return magic

    @_decorator
    def bar(self):
        print("normal call", self.attrib)


if __name__ == '__main__':

    test = Test()
    test.bar()
