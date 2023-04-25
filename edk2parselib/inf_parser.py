from lark import Lark, Tree, Transformer, Visitor, Token
from os import PathLike
import copy

PHASES = ["SEC", "PEIM", "PEI_CORE", "DXE_DRIVER", "DXE_CORE", "DXE_RUNTIME_DRIVER", "UEFI_DRIVER",
          "SMM_CORE", "DXE_SMM_DRIVER", "UEFI_APPLICATION"]
PCDS = ["featurepcd", "fixedpcd", "patchpcd", "pcd", "pcdex"]
class Entry:
    def __init__(self, data):
        self.value = data[0].strip()
        self.options = [item.strip() for item in data[1:]]
    
    def __repr__(self) -> str:
        return f'{self.value}{"|" if self.options else ""}{"|".join(self.options)}'

class Define:
    def __init__(self, data):
        self.variable = data[0].strip()
        self.value = data[1].strip()
        self.options = [item.strip() for item in data[2:]]

        self.options = data[2:]
    
    def __repr__(self) -> str:
        return f'{self.variable} = {self.value}{"|" if self.options else ""}{"|".join(self.options)}'

class BuildOption:
    def __init__(self, data):
        self.family = ""
        self.flags = ""
        self.variable = ""

        for d in data:
            if d.type == 'edk2__WORD':
                self.family = str(d).strip()
            elif d.type == 'edk2__VARIABLE':
                self.variable = str(d).strip()
            elif d.type == 'edk2__FLAGS':
                self.flags = str(d).strip()     
    
    def __repr__(self) -> str:
        return f'{self.family}{":" if self.family else ""}{self.variable} = {self.flags}'

class InfVisitor(Visitor):

    def start(self, tree:Tree):
        """Separate sections that contain multiple scopes into their own section.
        
        Example: [Sources.IA32, Sources.X64] -> [Sources.IA32],[Sources.X64]
        """
        for section in filter(lambda section: "," in section.children[0], tree.children):
            section_name = section.children[0]
            for single_name in section_name.split(","):
                tmp = copy.deepcopy(section)
                tmp.children[0] = single_name.strip()
                tree.children.append(tmp)
            tree.children.remove(section)

class InfTransformer(Transformer):
        
    base__define = Define
    base__entry = Entry
    base__build_option = BuildOption

    base__SECTION_NAME = str
    base__VALUE = str
    base__OPTION = str
    
    def start(self, data):
        d = {}
        for section in data:
            d.update(section)
        return d
            
    def section(self, data):
        section_name = data[0]
        return {section_name: data[1:]}



class InfParser():
    """An INF Parser."""
    _GRAMMER = r"""
start: section+

%import .base.section

%import common.WS_INLINE
%ignore WS_INLINE

%import common.SH_COMMENT
%ignore SH_COMMENT

%import common.WS
%ignore WS
"""
    def __init__(self, env = {}, pathobj = None):
        self._env = env
        self._pathobj = pathobj
        self._parser = Lark(self._GRAMMER)
        self.raw_data = {}

    def get_library_class(self) -> str:
        """Returns the library class of the INF or None if not a library."""
        for define in self.raw_data['Defines']:
            if define.variable == 'LIBRARY_CLASS':
                return define.value
        return None
    
    def get_phases(self) -> list[str]:
        """Returns a list of supported phases"""
        for define in self.raw_data['Defines']:
            if define.variable == 'LIBRARY_CLASS':
                if not define.options:
                    return PHASES
                return define.options[0].strip().split(" ")
        return None

    def _get_section(self, section: str) -> list[str]:
        ret_list = []

        for item in self.raw_data:
            if item.lower().startswith(section):
                ret_list.extend([entry.value for entry in self.raw_data[item]])
        return list(set(ret_list))

    def get_packages(self, arch: str = None) -> list[str]:
        section = f'packages.{arch}' if arch else 'packages'
        return self._get_section(section)

    def get_libraries(self, arch: str = None) -> list[str]:
        section = f'libraryclasses.{arch}' if arch else 'libraryclasses'
        return self._get_section(section)
    
    def get_protocols(self, arch: str = None) -> list[str]:
        section = f'protocols.{arch}' if arch else f'protocols'
        return self._get_section(section)
    
    def get_guids(self, arch: str = None) -> list[str]:
        section = f'guids.{arch}' if arch else 'guids'
        return self._get_section(section)

    def get_ppis(self, arch: str = None) -> list[str]:
        section = f'ppis.{arch}' if arch else 'ppis'
        return self._get_section(section)

    def get_pcds(self, types: list[str] = PCDS, arch: str = None) -> list[str]:
        ret_list = []
        for pcd in types:
            if pcd.lower() not in PCDS:
                raise ValueError(f'{pcd} is not a valid pcd. Valid pcds: {PCDS}')
            section = f'{pcd}.{arch}' if arch else pcd
            ret_list.extend(self._get_section(section))
        return ret_list
    
    def get_sources(self, arch: str = None) -> list[str]:
        section = f'sources.{arch}' if arch else 'sources'
        return self._get_section(section)
    
    def get_binaries(self, arch: str = None) -> list[str]:
        section = f'binaries.{arch}' if arch else 'binaries'
        return self._get_section(section)

    def parse(self, path: PathLike):
        file_data = open(path)
        tree = self._parser.parse(file_data.read())
        tree = InfVisitor().visit(tree)
        self.raw_data = InfTransformer().transform(tree)
    

import pathlib
import time
if __name__ == "__main__":
    t = time.time()
    for file in pathlib.Path("/Library/src/edk2_parser/mu_basecore").rglob("*.inf"):
        inf = InfParser()
        inf.parse(file)
        print(inf.get_sources())
    print(time.time()-t)
