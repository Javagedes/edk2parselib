from lark import Lark, Tree

inf_grammer = r"""

start: section+

section: NL? define_section
       | NL? source_section
       | NL? package_section
       | NL? library_section
       | NL? protocol_section
       | NL? pcd_section
       | NL? depex_section
       | NL? extension_section
       | NL? guid_section
       | NL? ppi_section
       | NL? binary_section
       | NL? buildoption_section

%import .edk2.NL
%import .edk2.define_section
%import .edk2.source_section
%import .edk2.package_section
%import .edk2.library_section
%import .edk2.protocol_section
%import .edk2.pcd_section
%import .edk2.depex_section
%import .edk2.extension_section
%import .edk2.guid_section
%import .edk2.ppi_section
%import .edk2.binary_section
%import .edk2.buildoption_section

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
            parse_tree = parser.parse(f.read())
        
    print(time.time()-t)
