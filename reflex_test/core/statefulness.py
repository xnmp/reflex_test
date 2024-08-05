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


def handler(func):
    func._is_handler = True
    return func


def get_original_init(cls):
    for base in cls.__mro__:
        if '__original_init__' in base.__dict__:
            return base.__original_init__
    return lambda self: None  # Default no-op init if no other init is found


def get_stateful_name(stateful_obj):
    
    try:
        if not hasattr(stateful_obj.__class__, 'names'):
            stateful_obj.__class__.names = set()
        if stateful_obj.name in stateful_obj.__class__.names:
            raise Exception(f"Stateful class names must be unique, {stateful_obj.name} is already taken")
    except AttributeError:
        raise Exception("Stateful classes must have a name attribute")
    stateful_obj.__class__.names.add(stateful_obj.name)
    
    # IMPORTANT: the state_id must be a deterministic function of the class name - if it's different when compiling vs when running then Reflex will break
    state_id = Hasher.generate(stateful_obj.__class__.__name__ + stateful_obj.name)
    state_class_name = 'State' + state_id
    return state_class_name


class StateWithStateful(rx.State):
    def __getattr__(self, name: str):
        try:
            return super().__getattr__(name)
        except AttributeError:
            return object.__getattribute__(self.__class__._stateful_obj, name)


class StatefulMeta(type):
    
    allstates = {}
    
    def __new__(meta_cls, cls_name, bases, attrs):

        state_attrs = {}

        for attr_name, attr_value in attrs.items():
            if isinstance(attr_value, property) and hasattr(attr_value.fget, '_is_state'):
                state_attrs[attr_name] = attr_value#.fget(None)
            elif hasattr(attr_value, '_is_handler'):
                state_attrs[attr_name] = attr_value
        
        # for attr_name in state_attrs:
        #     del attrs[attr_name]

        original_init = attrs.get('__init__', get_original_init(bases[0] if bases else object))
        
        def new_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            
            state_class_name = get_stateful_name(self)
            # state_attrs['__module__'] = attrs['__module__']
            # state_attrs['__qualname__'] = state_class_name
            
            state_class_attrs = {
                name: prop.fget(self) if isinstance(prop, property) else prop
                for name, prop in state_attrs.items()
            }
            
            self.State = type(state_class_name, (StateWithStateful,), state_class_attrs)
            self.State._stateful_obj = self
        
        attrs['__init__'] = new_init
        attrs['__original_init__'] = original_init
        attrs['_state_attrs'] = state_attrs

        res = super().__new__(meta_cls, cls_name, bases, attrs)
        return res


class Stateful(metaclass=StatefulMeta):
    
    def __init__(self, name):
        self.name = name

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

