import reflex as rx
from typing import List, Any
from copy import copy
import random
import string

from ..utils.hasher import Hasher
# this is all actually already pre-made with rx.ComponentState


def state(func):
    func._is_state = True
    return property(func)


def state_change(func):
    func._is_state_change = True
    return func


class StateWithStateful(rx.State):
    def __getattr__(self, name: str):
        try:
            return super().__getattr__(name)
        except AttributeError:
            return object.__getattribute__(self.__class__._stateful_obj, name)


class StatefulMeta(type):
    
    allstates = {}
    
    def __new__(cls, name, bases, attrs):

        state_attrs = {}

        for attr_name, attr_value in attrs.items():
            if isinstance(attr_value, property) and hasattr(attr_value.fget, '_is_state'):
                state_attrs[attr_name] = attr_value.fget(None)
            elif hasattr(attr_value, '_is_state_change'):
                state_attrs[attr_name] = attr_value
        
        # for attr_name in state_attrs:
        #     del attrs[attr_name]

        original_init = attrs.get('__init__', lambda self: None)
        
        def new_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            
            try:
                if not hasattr(cls, 'names'):
                    cls.names = set()
                if self.name in cls.names:
                    raise Exception(f"Stateful class names must be unique, {self.name} is already taken")
            except AttributeError:
                raise Exception("Stateful classes must have a name attribute")
            cls.names.add(self.name)
            
            # IMPORTANT: the state_id must be a deterministic function of the class name - if it's different when compiling vs when running then Reflex will break
            state_id = Hasher.generate(self.__class__.__name__ + self.name)
            
            state_class_name = 'State' + state_id
            print("State_class_name:", state_class_name)
            # state_attrs['__module__'] = attrs['__module__']
            # state_attrs['__qualname__'] = state_class_name
            self.State = type(state_class_name, (StateWithStateful,), state_attrs)
            self.State._stateful_obj = self
        
        attrs['__init__'] = new_init
        attrs['_state_attrs'] = state_attrs

        res = super().__new__(cls, name, bases, attrs)
        return res


class Stateful(metaclass=StatefulMeta):

    def __getattribute__(self, name):
        if name in ['_state_attrs', '_state']:
            return object.__getattribute__(self, name)
        if name in self._state_attrs:
            return getattr(self.State, name)
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name in self._state_attrs:
            setattr(self.State, name, value)
        else:
            super().__setattr__(name, value)

