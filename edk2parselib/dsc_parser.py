from lark import Lark
from base_parser import BaseTransformer, BaseVisitor, BaseParser

class InfParser(BaseParser):
    """An INF Parser."""
    _PARSER = Lark(r"""
        start: (define_section| buildoption_section| common_section | include_statement)+

        %import .base.define_section
        %import .base.buildoption_section
        %import .base.common_section
        %import .base.include_statement

        %import common.WS_INLINE
        %ignore WS_INLINE

        %import common.SH_COMMENT
        %ignore SH_COMMENT

        %import common.WS
        %ignore WS
    """)
    _VISITOR = BaseVisitor()
    _TRANSFORMER = BaseTransformer()

import pathlib
import time
import pprint
if __name__ == "__main__":
    t = time.time()
    #for file in pathlib.Path("/Library/src/edk2_parser/mu_basecore").rglob("*.dsc"):
    file = pathlib.Path("/Library/src/edk2_parser/mu_basecore/PcAtChipsetPkg/PcAtChipsetPkg.dsc")
    print(file)
    inf = InfParser()
    inf.parse(file)
    pprint.pprint(inf.raw_data)
    print(time.time()-t)
