import reflex as rx
from typing import List, Any
import random
import string


# TODO: guarantee uniqueness here by using a counter
def generate_random_classname(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))


def state(func):
    func._is_state = True
    return property(func)


def state_change(func):
    func._is_state_change = True
    return func


class StateMeta(type):
    
    def __new__(cls, name, bases, attrs):

        # print("Attrs:", attrs)

        state_attrs = {}

        for attr_name, attr_value in attrs.items():
            if isinstance(attr_value, property) and hasattr(attr_value.fget, '_is_state'):
                state_attrs[attr_name] = attr_value.fget(None)
            elif hasattr(attr_value, '_is_state_change'):
                state_attrs[attr_name] = attr_value

        for attr_name in state_attrs:
            del attrs[attr_name]


        original_init = attrs.get('__init__', lambda self: None)
        def new_init(self, *args, **kwargs):
            state_class_name = generate_random_classname()
            StateClass = type(state_class_name, (rx.State,), state_attrs)
            self._state = StateClass
            original_init(self, *args, **kwargs)
        
        attrs['__init__'] = new_init
        attrs['_state_attrs'] = state_attrs

        return super().__new__(cls, name, bases, attrs)


class Stateful(metaclass=StateMeta):

    def __getattr__(self, name):
        if name in self._state_attrs:
            return getattr(self._state, name)
        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        if name in self._state_attrs:
            setattr(self._state, name, value)
        else:
            super().__setattr__(name, value)

