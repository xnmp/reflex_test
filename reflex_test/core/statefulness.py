import reflex as rx
from typing import List, Any
from copy import copy
from ordered_set import OrderedSet

import random
import string
import types

from ..utils.hasher import Hasher
# this is all actually already pre-made with rx.ComponentState


def state(func):
    func._is_state = True
    return property(func)


def state_var(cached):
    def state_var_cached(func):
        func._is_state_var = True
        func._cached = cached if isinstance(cached, bool) else False
        return func
    if isinstance(cached, bool):
        return state_var_cached
    return state_var_cached(cached)


def handler(func):
    func._is_handler = True
    return func


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
    state_class_name = stateful_obj.name + 'State' + state_id
    return state_class_name


class StateWithStateful(rx.State):
    def __getattr__(self, name: str):
        try:
            return super().__getattr__(name)
        except AttributeError:
            return object.__getattribute__(self.__class__._stateful_obj, name)


def modify_state_attrs(state_attrs, stateful_cls_instance):
    res = {}
    for attr_name, attr_value in state_attrs.items():
        if isinstance(attr_value, property) and hasattr(attr_value.fget, '_is_state'):
            res[attr_name] = attr_value.fget(stateful_cls_instance)
        elif hasattr(attr_value, '_is_handler'):
            res[attr_name] = attr_value
        elif hasattr(attr_value, '_is_state_var') and attr_value._cached:
            # res[attr_name] = rx.var(cached=attr_value._cached)(attr_value)
            res[attr_name] = rx.cached_var(attr_value)
            # res[attr_name].get_full_name = types.MethodType(lambda self: self._var_data.state, res[attr_name])
        elif hasattr(attr_value, '_is_state_var') and not attr_value._cached:
            res[attr_name] = rx.var(attr_value)
            # res[attr_name].get_full_name = types.MethodType(lambda self: self._var_data.state, res[attr_name])
    return res


def get_state_attrs(bases, stateful_cls_attrs):
    state_attrs = {}
    
    def is_state_attr(attr):
        return (isinstance(attr, property) and hasattr(attr.fget, '_is_state')) or \
               hasattr(attr, '_is_handler') or hasattr(attr, '_is_state_var')
    
    # Collect state attributes from all base classes, in reverse order
    for base in reversed(bases):
        for cls in reversed(base.__mro__):
            if cls is object:
                continue
            for attr_name, attr_value in cls.__dict__.items():
                if is_state_attr(attr_value):
                    state_attrs[attr_name] = attr_value
    
    # Add attributes from the current class, potentially overriding inherited ones
    for attr_name, attr_value in stateful_cls_attrs.items():
        if is_state_attr(attr_value):
            state_attrs[attr_name] = attr_value
    
    return state_attrs


class StatefulMeta(type):
    
    allstates = {}
    
    def __new__(meta_cls, stateful_cls_name, bases, stateful_cls_attrs):
        
        state_attrs = get_state_attrs(bases, stateful_cls_attrs)
        original_init = stateful_cls_attrs.get('__init__', bases[0].__original_init__ if bases else lambda x: None)
        
        def new_init(stateful_cls_instance, *args, **kwargs):
            
            original_init(stateful_cls_instance, *args, **kwargs)
            stateful_cls_instance.handlers = []
            stateful_cls_instance.sources = {}
            state_attrs2 = modify_state_attrs(state_attrs, stateful_cls_instance)
            
            stateful_cls_instance.State = type(get_stateful_name(stateful_cls_instance), (StateWithStateful,), state_attrs2)
            stateful_cls_instance.State._stateful_obj = stateful_cls_instance
        
        stateful_cls_attrs['__init__'] = new_init
        stateful_cls_attrs['__original_init__'] = original_init
        stateful_cls_attrs['_state_attrs'] = state_attrs

        stateful_cls = super().__new__(meta_cls, stateful_cls_name, bases, stateful_cls_attrs)
        return stateful_cls


class Stateful(metaclass=StatefulMeta):
    
    # handlers = []
    
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
    
    def get_full_name(self):
        return self.State.get_full_name()
    
    def add_deps(self, *deps, **kwargs):
        for kw, func in kwargs.items():
            setattr(self, kw, func)
        if not hasattr(self, 'deps'):
            self.deps = []
        for dep in deps:
            self.deps.append(dep)
    
    def add_sources(self, **sources):
        for source in sources.values():
            if isinstance(source, Stateful):
                source.add_handlers(self)
            elif isinstance(source, dict):
                source['state'].add_handlers(self)
        self.sources.update(sources)
        return self
    
    def add_handlers(self, *handlers):
        """
        handlers can be Stateful objects (in which case its update method will be called), or handler functions, either async or not
        """
        for handler in handlers:
            if handler not in self.handlers:
                self.handlers.append(handler)
    
    @handler
    async def get_source(self, source_name):
        if source_name in self.sources:
            source = self.sources[source_name]
            if isinstance(source, Stateful):
                return await self.get_state(source.State)
            else:
                source['state'].add_handlers(self)
                res = await self.get_state(source['state'].State)
                return source['transform'](res)
        else:
            raise AttributeError(f"Source {source_name} not found")
    
    @property
    def update_all(self):
        res = [self.update]
        if hasattr(self, 'handlers'):
            for handler in self.handlers:
                if isinstance(handler, Stateful):
                    res += handler.update_all
                else:
                    res.append(handler)
        return res
