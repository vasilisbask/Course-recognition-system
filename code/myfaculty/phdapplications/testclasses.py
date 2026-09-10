class A:

    options = {
        'line' : 'blue',
        'circle' : 'red'
    }

    def get_name(self):
        return self.__class__.__name__
    
    def __init__(self):
        a_options = self.get_ancestor_options()
        for k, v in a_options.items():
            if k not in self.options:
                self.options[k] = v


    def get_ancestor_options(self):
        base_class = self.__class__.__base__
        try:
            options = base_class.options
        except AttributeError:
            options = {}
        return options


class B(A):

    options = {
        'line' : 'green'
    }
    
class C(B):

    options = {
        'circle' : 'black'
    }
    
a = A()
b = B()
c = C()
