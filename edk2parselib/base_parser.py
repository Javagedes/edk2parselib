from lark import Lark, Tree, Transformer, Visitor, Token
import copy
from os import PathLike

class DefineEntry:
    def __init__(self, data):
        self.variable = data[0].strip()
        self.value = data[1].strip()
        self.options = [item.strip() for item in data[2:]]
    
    def __repr__(self) -> str:
        return f'{self.variable} = {self.value}{"|" if self.options else ""}{"|".join(self.options)}'
    
    def __eq__(self, other):
        return self.variable == other.variable
    
    def __hash__(self):
        return hash(self.variable)


class BuildOptionEntry:
    def __init__(self, data):
        self.variable = data[0].strip()
        self.value = data[1].strip()
        self.options = [item.strip() for item in data[2:]]
    
    def __repr__(self) -> str:
        return f'{self.variable}:{self.value}{" =" if self.options else ""}{"|".join(self.options)}'


class CommonEntry:
    def __init__(self, data):
        self.value = data[0].strip()
        self.options = [item.strip() for item in data[1:]]
    
    def __repr__(self) -> str:
        return f'{self.value}{"|" if self.options else ""}{"|".join(self.options)}'


class BaseTransformer(Transformer):
    """A class that transforms nodes on a tree.
    
    It performs these actions in one of two ways by passing the data to the method or attribute
    that matches the name of the node type.

    For each node in the tree, if the transformer finds a match for the node type, it calls that
    function (or __init__() of a class) and replaces that node with the returned value of that
    function (or __init__().
    
    TERMINAL: a string or regular expression that we match. returns as a Token containing the matched value
        
        example:

            lets assume we have the following terminal: `SECTION_NAME: CHARS+`
            lets assume we have the following string to match `IMALLCHARS`
            This rule terminal will match and return the following: Token('SECTION_NAME', 'IMALLCHARS')
    
    rule: an expression to search for, that when matched, generates a tree object containing any terminals or rules inside the rule.
        
        example: 
        
            Lets assume we have the following rule: `common_section: "[" SECTION_NAME "]" common_entry*`
            Lets assume we have the following string to match: ["LibraryClass"] PrintLib PcdLib
            This rule will match and return the following: Tree('common_section', [Token('SECTION_NAME', ...), Tree('common_entry', ...), Tree('common_entry', ...)])
    """
    def replace_variable(self, data):
        """Checks for, and replaces, a $(<VARIABLE>)."""
        return str(data)

    # When we detect a entry rule, transform it into the appropriate entry object
    base__define_entry = DefineEntry
    base__buildoption_entry = BuildOptionEntry
    base__common_entry = CommonEntry

    # When we detect one of these string terminals, try and replace any $(<VAR>) with the true value
    base__BUILD_OPTIONS_SECTION_NAME = replace_variable
    base__SECTION_NAME = replace_variable
    base__DEFINE_SECTION_NAME = replace_variable
    base__PATH = replace_variable
    base__STRING = replace_variable
    base__FLAG = replace_variable

    def common_section(self, data: list):
        """Returns a dict entry of sectionname: section entries."""

        return {data[0]: data[1:]}
    
    def define_section(self, data):
        """Returns a dict entry of sectionname: section entries."""
        return {data[0]: data[1:]}
    
    def buildoption_section(self, data):
        """Returns a dict entry of sectionname: section entries."""
        return {data[0]: data[1:]}
    
    def start(self, data):
        """Transforms a list of section dicts into a dict where the section name is the key."""
        d = {}
        for section in data:
            d.update(section)
        return d


class BaseVisitor(Visitor):
    """A Class that visits nodes and performs operations."""
    
    def start(self, tree: Tree):
        """Find any section that has multiple sections and creates separate cloned trees for each section
        
        [LibraryClasses.IA32, LibraryClasses.X64] -> [LibraryClasses.IA32] [LibraryClasses.X64]
        """
        for section in filter(lambda section: "," in section.children[0], tree.children):
            section_name = section.children[0]
            for single_name in section_name.split(","):
                tmp = copy.deepcopy(section)
                tmp.children[0] = single_name.strip()
                tree.children.append(tmp)
            tree.children.remove(section)

class BaseParser():
    def __init__(self, env = {}, pathobj = None):
        self._env = env
        self._pathobj = pathobj
        self.raw_data = {}
    
    def parse(self, path: PathLike): 
        file_data = open(path)
        tree = self._PARSER.parse(file_data.read())
        print(tree.pretty())
        #tree = self._VISITOR.visit(tree)
        #self.raw_data = self._TRANSFORMER.transform(tree)