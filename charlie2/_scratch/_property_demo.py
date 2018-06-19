class Obj:
    """property demo"""
    #
    @property
    def attribute(self): # implements the get - this name is *the* name
        return self._attribute
    #
    @attribute.setter
    def attribute(self, value): # name must be the same
        self._attribute = value


value = 'x'
obj = Obj()
obj.attribute = value
the_value = obj.attribute
print(the_value)