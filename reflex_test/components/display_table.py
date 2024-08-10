import reflex as rx

from typing import List, Dict, Any
from ..core.statefulness import Stateful, state, handler


class DisplayTable(Stateful):
    
    @state
    def display_data(self) -> List[List[Any]]:
        return [[]]
    
    @handler
    async def update(self):
        res = await self.get_source('data')
        if len(res) > 5:
            res = res.sample(5)
        for col in self.display_columns:
            res[col] = res[col].astype(str)
        self.display_data = res[self.display_columns].values.tolist()
    
    @property
    def display_columns(self):
        return ['CASE_RECV_S', 'CASE_SUMY_X', 'State', 'case_sumy_length']
    
    @property
    def column_defs(self) -> List[Dict[str, Any]]:
        res = []
        for col in self.display_columns:
            res0 = {'name': col, 'sort':True} #for base rx.data_table
            if col in 'CASE_SUMY_X':
                res0['width'] = 800
            res.append(res0)
        return res
    
    @property
    def element(self):
        _element = rx.data_table(
            columns=self.column_defs,
            data=self.display_data,
            # resizable=True,
        )
        return rx.box(_element, max_height="50vh", overflow='auto')

