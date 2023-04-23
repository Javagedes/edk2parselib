from lark import Lark, Tree

inf_grammer = r"""

start: section+

%import .edk2.section


%import common.WS_INLINE
%ignore WS_INLINE

%import common.SH_COMMENT
%ignore SH_COMMENT

%import common.WS
%ignore WS
"""

parser = Lark(inf_grammer)
import pathlib
import time
if __name__ == "__main__":
    
    t = time.time()
    for file in pathlib.Path("/Library/src/edk2_parser/mu_basecore").rglob("*.inf"):
        with open(file) as f:
            # print(file)
            parse_tree = parser.parse(f.read())
            # print(parse_tree.pretty())
        
    print(time.time()-t)
