from dataclasses import dataclass
from enum import Enum, auto
from time import sleep as wait
wait(1)

if __name__ == "__main__":
	from lexer import Run, Token
else:
	from src.lexer import Run, Token

class Color:
	RESET = "\033[0m"

	RED = "\033[31m"
	YELLOW = "\033[33m"
	CYAN = "\033[36m"
	BOLD = "\033[1m"

class Severity(Enum):
	ERROR = auto()
	WARNING = auto()

class ParserErrorCode(Enum):
	UNEXPECTED_TOKEN = auto()
	UNEXPECTED_EOF = auto()
	EXPECTED_TOKEN = auto()
	INVALID_SYNTAX = auto()
	INVALID_EXPRESSION = auto()
	INVALID_STATEMENT = auto()
	INVALID_INCLUDE = auto()

@dataclass
class Diagnostic:
	severity: Severity
	code: str
	message: str
	row: int
	col: int
	source_line: str = ""
	highlight_length: int = 1

	def format(self):
		colour = Color.RED if self.severity == Severity.ERROR else Color.YELLOW

		severity = self.severity.name

		out = []

		out.append(
			f"{colour}{severity}{Color.RESET} "
			f"[{self.code}] "
			f"at {self.row}:{self.col + 1}"
		)

		out.append(self.message)

		if self.source_line:
			out.append("")

			line_prefix = f"{self.row:>4} | "

			out.append(f"{line_prefix}{self.source_line}")

			out.append(
				" " * len(line_prefix)
				+ " " * self.col
				+ "^" * max(self.highlight_length, 1)
			)

		return "\n".join(out)

@dataclass
class ParserDiagnostic:
	code: ParserErrorCode
	severity: Severity
	message: str
	row: int
	col: int
	source_line: str = ""
	highlight_length: int = 1

	def format(self):
		diagnostic = Diagnostic(
			severity=self.severity,
			code=self.code.name,
			message=self.message,
			row=self.row,
			col=self.col,
			source_line=self.source_line,
			highlight_length=self.highlight_length,
		)

		return diagnostic.format()

class ParserError(Exception):
	def __init__(self, diagnostic):
		self.diagnostic = diagnostic
		super().__init__(diagnostic.message)

	def __str__(self):
		return self.diagnostic.format()

class Node:
	def __init__(self):
		self.parent = None

	def __repr__(self):
		return self._tree()

	def _tree(self, prefix="", last=True):
		branch = "└── " if last else "├── "

		out = prefix + branch + self.__class__.__name__

		attrs = []

		for name, value in self.__dict__.items():
			if name == "parent":
				continue

			if isinstance(value, Node):
				continue

			if isinstance(value, list):
				if value and all(isinstance(val, Node) for val in value):
					continue

			attrs.append(f"{name}={value!r}")

		if attrs:
			out += " [" + ", ".join(attrs) + "]"

		next_prefix = prefix + ("	" if last else "│   ")

		children = []

		for value in self.__dict__.values():
			if isinstance(value, Node):
				children.append(value)

			elif isinstance(value, list):
				children.extend(val for val in value if isinstance(val, Node))

		for idx, child in enumerate(children):
			out += "\n"

			out += child._tree(next_prefix, idx == len(children) - 1)

		return out

class StatementNode(Node):
	pass

class ExpressionNode(Node):
	pass

class ProgramNode(Node):
	def __init__(self):
		super().__init__()
		self.statements = []

class BlockNode(Node):
	def __init__(self):
		super().__init__()
		self.statements = []

class IdentNode(ExpressionNode):
	def __init__(self, token):
		super().__init__()
		self.token = token

class LiteralNode(ExpressionNode):
	def __init__(self, token):
		super().__init__()
		self.token = token

class BinaryNode(ExpressionNode):
	def __init__(
		self,
		lvalue: ExpressionNode,
		operation,
		rvalue: ExpressionNode,
	):
		super().__init__()

		self.lvalue = lvalue
		self.operation = operation
		self.rvalue = rvalue

class UnaryNode(ExpressionNode):
	def __init__(self, operation, value: ExpressionNode):
		super().__init__()

		self.operation = operation
		self.value = value

class TypeNode(Node):
	def __init__(self, token):
		super().__init__()
		self.token = token

class AssignNode(ExpressionNode):
	def __init__(
		self,
		type: TypeNode | None,
		name: IdentNode | None,
		operation,
		value: ExpressionNode,
		target: ExpressionNode = None,
		is_const: bool = False,
	):
		super().__init__()

		self.target = target
		self.operation = operation
		self.value = value
		self.type = type
		self.name = name
		self.is_const = is_const

class CallNode(ExpressionNode):
	def __init__(self, function: ExpressionNode, arguments: list):
		super().__init__()

		self.function = function
		self.arguments = arguments

class MemberNode(ExpressionNode):
	def __init__(self, object: ExpressionNode, member):
		super().__init__()

		self.object = object
		self.member = member

class IndexNode(ExpressionNode):
	def __init__(self, object: ExpressionNode, index: ExpressionNode):
		super().__init__()

		self.object = object
		self.index = index

class SliceNode(ExpressionNode):
	def __init__(self, object: ExpressionNode, start, stop, step):
		super().__init__()

		self.object = object
		self.start = start
		self.stop = stop
		self.step = step

class CastNode(ExpressionNode):
	def __init__(self, type_token, value: ExpressionNode):
		super().__init__()

		self.type = type_token
		self.value = value

class ConditionalNode(ExpressionNode):
	def __init__(
		self,
		condition: ExpressionNode,
		true_expr: ExpressionNode,
		false_expr: ExpressionNode,
	):
		super().__init__()

		self.condition = condition
		self.true_expr = true_expr
		self.false_expr = false_expr

class ReturnNode(StatementNode):
	def __init__(self, value=None):
		super().__init__()
		self.value = value

class BreakNode(StatementNode):
	def __init__(self):
		super().__init__()

class ContinueNode(StatementNode):
	def __init__(self):
		super().__init__()

class IfNode(StatementNode):
	def __init__(
		self,
		condition: ExpressionNode,
		body: BlockNode,
	):
		super().__init__()

		self.condition = condition
		self.body = body
		self.elifs = []
		self.else_body = None

class WhileNode(StatementNode):
	def __init__(
		self,
		condition: ExpressionNode,
		body: BlockNode,
	):
		super().__init__()

		self.condition = condition
		self.body = body

class ForNode(StatementNode):
	def __init__(self, variable, iterable, body):
		super().__init__()

		self.variable = variable
		self.iterable = iterable
		self.body = body

class ParameterNode(Node):
	def __init__(
		self,
		name,
		type=None,
		default=None,
	):
		super().__init__()

		self.name = name
		self.type = type
		self.default = default

class FunctionNode(StatementNode):
	def __init__(
		self,
		name,
		parameters,
		body,
		return_type=None,
		decleators=None
	):
		super().__init__()

		self.name = name
		self.parameters = parameters
		self.body = body
		self.return_type = return_type
		self.decleators = decleators

class ClassNode(StatementNode):
	def __init__(self, name, parent, body):
		super().__init__()

		self.name = name
		self.parent = parent
		self.body = body

class ExpressionList(Node):
	def __init__(self, elements):
		super().__init__()

		if elements == None:
			self.elements = []
		else:
			self.elements = elements

class IncludeNode(StatementNode):
	def __init__(
		self,
		source_file,
		alias=None,
		imports=None,
	):
		super().__init__()

		self.source = source_file

		if alias == None:
			filename = source_file.split("/")[-1]

			if filename.endswith(".GOS"):
				filename = filename[:-4]

			self.alias = [filename]

		else:
			self.alias = alias

		if imports == None:
			self.imports = ["*"]
		else:
			self.imports = imports

class ParameterNode(Node):
	def __init__(self, name, type=None, default=None):
		super().__init__()
		self.name = name
		self.type = type
		self.default = default

class FStringNode(ExpressionNode):
	def __init__(self, parts):
		super().__init__()
		self.parts = parts

class FStringTextNode(Node):
	def __init__(self, text):
		super().__init__()
		self.text = text

class FStringExprNode(Node):
	def __init__(self, expression):
		super().__init__()
		self.expression = expression

class VargsIdentNode(IdentNode):
	def __init__(self, token):
		super().__init__(token)

class KargsIdentNode(IdentNode):
	def __init__(self, token):
		super().__init__(token)

class Parser:
	def __init__(self, tokens, source="", types=None):
		self.AST = ProgramNode()

		self.current_block = self.AST.statements

		self.tok_to_process = tokens

		self.curtok = 0

		self.source = source
		self.lines = source.splitlines()

		self.errors = []
		self.warnings = []

		# Built-in types
		self.types = {
			"int",
			"float",
			"str",
			"char",
			"bool",
			"none",
		}

		# Imported/user-defined types
		if types:
			self.types.update(types)

	def _source_line(self, row):
		if 1 <= row <= len(self.lines):
			return self.lines[row - 1]

		return ""

	def _token_length(self, token):
		if token == None or token.raw == None:
			return 1

		raw = str(token.raw)

		if not raw:
			return 1

		return len(raw)

	def error(
		self,
		message,
		token=None,
		code=ParserErrorCode.INVALID_SYNTAX,
		length=None,
	):
		if token == None:
			token = self.peek()

		if token == None or token.kind == "EOF":
			if self.lines:
				row = len(self.lines)
				col = len(self.lines[-1])
				source_line = self.lines[-1]
			else:
				row = 1
				col = 0
				source_line = ""

			if length == None:
				length = 1

		else:
			row = token.row
			col = token.col

			source_line = self._source_line(row)

			if length == None:
				length = self._token_length(token)

		diagnostic = ParserDiagnostic(
			code=code,
			severity=Severity.ERROR,
			message=message,
			row=row,
			col=col,
			source_line=source_line,
			highlight_length=length,
		)

		self.errors.append(diagnostic)

		raise ParserError(diagnostic)

	def warning(
		self,
		message,
		token=None,
		code=ParserErrorCode.INVALID_SYNTAX,
		length=None,
	):
		if token == None:
			token = self.peek()

		if token == None or token.kind == "EOF":
			if self.lines:
				row = len(self.lines)
				col = len(self.lines[-1])
				source_line = self.lines[-1]
			else:
				row = 1
				col = 0
				source_line = ""

			if length == None:
				length = 1

		else:
			row = token.row
			col = token.col

			source_line = self._source_line(row)

			if length == None:
				length = self._token_length(token)

		diagnostic = ParserDiagnostic(
			code=code,
			severity=Severity.WARNING,
			message=message,
			row=row,
			col=col,
			source_line=source_line,
			highlight_length=length,
		)

		self.warnings.append(diagnostic)

		return diagnostic

	def token_display(self, kind):
		for text, token_kind in Token.TOKENS.items():
			if token_kind == kind:
				return text

		return kind

	def token_description(self, token):
		if token == None:
			return "end of file"

		if token.kind == "EOF":
			return "end of file"

		return self.token_display(token.kind)

	def parse(self):
		while self.peek().kind != "EOF":
			stmt = self.parse_stmt()

			if stmt != None:
				self.current_block.append(stmt)

		print(self.AST)

		return self.AST

	def token_to_node(self, token):
		if token.kind == "IDENT":
			return IdentNode(token)

		if token.kind in (
			"INT",
			"FLOAT",
			"STR",
			"BOOL",
			"NONE",
		):
			return LiteralNode(token)

		return token

	def peek(self, no=0):
		index = self.curtok + no

		if index >= len(self.tok_to_process):
			return self.tok_to_process[-1]

		return self.tok_to_process[index]

	def consume(self):
		out = self.peek()

		self.curtok += 1

		return out

	def expect(self, *kinds):
		tok = self.peek()

		if tok.kind not in kinds:

			expected = [self.token_display(kind) for kind in kinds]

			got = self.token_description(tok)

			if tok.kind == "EOF":
				self.error(
					f"Expected "
					f"{' or '.join(repr(x) for x in expected)}, "
					f"got end of file",
					token=tok,
					code=ParserErrorCode.UNEXPECTED_EOF,
				)

			self.error(
				f"Expected "
				f"{' or '.join(repr(x) for x in expected)}, "
				f"got {got!r}",
				token=tok,
				code=ParserErrorCode.EXPECTED_TOKEN,
			)

		return self.consume()

	def parse_stmt(self):
		tok = self.peek()

		if tok.kind == "INCLUDE":
			return self.parse_include_stmt()

		elif tok.kind == "AT":
			decorators = []

			while self.peek().kind == "AT":
				self.expect("AT")
				decorators.append(self.expect("IDENT"))
				self.expect("EOL")

			if self.peek().kind == "DEF":
				return self.parse_function_def(decorators)

			self.error(
				"Decorator must be followed by a function definition",
				token=self.peek(),
			)

		elif tok.kind == "CLASS":
			return self.parse_class_def()

		elif tok.kind == "DEF":
			return self.parse_function_def()

		elif tok.kind == "IF":
			return self.parse_if_stmt()

		elif tok.kind == "WHILE":
			return self.parse_while_stmt()

		elif tok.kind == "FOR":
			return self.parse_for_stmt()

		elif tok.kind == "BREAK":
			self.expect("BREAK")
			self.expect("EOL")
			return BreakNode()

		elif tok.kind == "CONTINUE":
			self.expect("CONTINUE")
			self.expect("EOL")
			return ContinueNode()

		elif tok.kind == "RETURN":
			self.expect("RETURN")

			if self.peek().kind == "EOL":
				self.expect("EOL")
				return ReturnNode(None)

			value = self.parse_expression()

			self.expect("EOL")

			return ReturnNode(value)

		elif tok.kind in ("TYPE", "CONST"):
			return self.parse_assignment_expr()

		elif (
			tok.kind == "IDENT"
			and tok.raw in self.types
			and self.peek(1).kind == "IDENT"
		):
			return self.parse_assignment_expr()

		else:
			stmt = self.parse_expression()

			self.expect("EOL")

			return stmt

	def parse_class_def(self):
		self.expect("CLASS")

		parent = None

		if self.peek().kind == "LNORPAREN":
			self.expect("LNORPAREN")
			parent = self.expect("IDENT")
			self.expect("RNORPAREN")

		name = self.expect("IDENT")

		# Register immediately for code appearing after this class
		self.types.add(name.raw)

		block = self.parse_class_block()

		return ClassNode(
			name=name,
			parent=parent,
			body=block,
		)

	def parse_type(self):
		tok = self.peek()

		if tok.kind == "TYPE":
			return TypeNode(self.consume())

		if tok.kind == "IDENT" and tok.raw in self.types:
			return TypeNode(self.consume())

		self.error(
			f"Expected type, got {tok.raw!r}",
			token=tok,
			code=ParserErrorCode.EXPECTED_TOKEN,
		)

	def parse_class_block(self):
		self.expect("LCRBPAREN")
		while self.peek().kind != "RCRBPAREN":
			inside = self.parse_class_member()
		self.expect("RCRBPAREN")
		print(inside)
		return inside

	def parse_class_member(self):
		tok = self.peek()

		if tok.kind in ("TYPE", "CONST"):
			return self.parse_variable_decl()

		if (
			tok.kind == "IDENT"
			and tok.raw in self.types
			and self.peek(1).kind == "IDENT"
		):
			return self.parse_variable_decl()

		if tok.kind == "DEF":
			return self.parse_method_def()

		if tok.kind == "AT":
			decorators = []

			while self.peek().kind == "AT":
				self.expect("AT")
				decorators.append(self.expect("IDENT"))
				self.expect("EOL")

			if self.peek().kind == "DEF":
				return self.parse_function_def(decorators)

			self.error(
				"Decorator must be followed by a function definition",
				token=self.peek(),
			)

		self.error(
			f"Unexpected token {tok.raw!r} in class body",
			token=tok,
			code=ParserErrorCode.UNEXPECTED_TOKEN,
		)

	def parse_method_def(self, declerators=None):
		typ = None
		self.expect("DEF")
		if self.peek().kind == "TYPE":
			typ = self.expect("TYPE")
		ident = self.expect("IDENT")
		parems = self.parse_parameter_list()
		block = self.parse_block()
		return FunctionNode(ident, parems, block, typ if typ else None, declerators)

	def parse_function_def(self, decerators=None):
		self.expect("DEF")
		if self.peek().kind == "TYPE":
			return_type = TypeNode(self.expect("TYPE"))
		else:
			return_type = TypeNode("any")
		func_name = IdentNode(self.expect("IDENT"))
		parameters = self.parse_parameter_list()
		block = self.parse_block()
		return FunctionNode(
			func_name,
			parameters,
			block,
			return_type,
			decerators
		)

	def parse_parameter_list(self):
		self.expect("LNORPAREN")
		parameters = []
		if self.peek().kind == "RNORPAREN":
			self.expect("RNORPAREN")
			return parameters

		while True:
			if self.peek().kind == "TYPE":
				typ = TypeNode(self.expect("TYPE"))
			else:
				typ = None
			if self.peek().kind == "ASTERISK":
				self.expect("ASTERISK")
				if self.peek().kind == "ASTERISK":
					pass
			name = IdentNode(self.parse_unary_expr())

			default = None

			if self.peek().kind == "ASSIGN":
				self.expect("ASSIGN")
				default = self.parse_expression()

			parameters.append(
				ParameterNode(
					name=name,
					type=typ,
					default=default,
				)
			)

			if self.peek().kind != "COMMA":
				break

			self.expect("COMMA")

		self.expect("RNORPAREN")

		return parameters

	def parse_include_stmt(self):
		"""
		* this is a bit complex so let me outline this
		* there are % forms for the include statement
		* form 1: #include "file.GOS";
		* form 2: #include module from "file.GOS";
		* form 3: #include module from "file.GOS" as alias;
		* form 4: #include module1, module2 from "file.GOS";
		* form 5: #include module1, module2 from "file.GOS" as alias1, alias2;
		"""
		# in all forms it starts with include
		self.expect("INCLUDE")

		# for no of alias == no of modules imported
		modules = 0

		# form 1
		if self.peek().kind == "STR":
			include_path = self.expect("STR")
			self.expect("EOL")
			return IncludeNode(include_path.raw)
		# form 2-5
		else:
			module = [self.expect("IDENT")]
			modules += 1
			# import more than 1 module form 4-5
			while self.peek().kind == "COMMA":
				self.expect("COMMA")
				module.append(self.expect("IDENT"))
				modules += 1
			# form 2-5
			self.expect("FROM")
			# in all forms will hv the src file here
			include_path = self.expect("STR")
			# form 2,4
			if self.peek().kind == "EOL":
				self.expect("EOL")
				return IncludeNode(include_path.raw, None, module)
			# form 3,5
			else:
				self.expect("AS")
				alias = [self.expect("IDENT")]
				modules -= 1
				while self.peek().kind == "COMMA":
					self.expect("COMMA")
					alias.append(self.expect("IDENT"))
					modules -= 1
				self.expect("EOL")
				if modules > 0:
					self.error("Number of aliases must match number of modules imported(Not enough aliases)")
				elif modules < 0:
					self.error("Number of aliases must match number of modules imported(Too many aliases)")
				else:
					return IncludeNode(include_path.raw, alias, module)

	def parse_for_stmt(self):
		self.expect("FOR")

		self.expect("LNORPAREN")

		ident = self.expect("IDENT")

		self.expect("IN")

		expr = self.parse_expression()

		self.expect("RNORPAREN")

		body = self.parse_block()

		return ForNode(
			ident,
			expr,
			body,
		)

	def parse_if_stmt(self):
		self.expect("IF")

		self.expect("LNORPAREN")

		condition = self.parse_expression()

		self.expect("RNORPAREN")

		node = IfNode(
			condition,
			self.parse_block(),
		)

		while self.peek().kind == "ELIF":
			self.consume()

			self.expect("LNORPAREN")

			cond = self.parse_expression()

			self.expect("RNORPAREN")

			node.elifs.append(
				IfNode(
					cond,
					self.parse_block(),
				)
			)

		if self.peek().kind == "ELSE":
			self.consume()

			node.else_body = self.parse_block()

		return node

	def parse_while_stmt(self):
		self.expect("WHILE")

		self.expect("LNORPAREN")

		cond = self.parse_expression()

		self.expect("RNORPAREN")

		body = self.parse_block()

		return WhileNode(
			cond,
			body,
		)

	def parse_block(self):
		self.expect("LCRBPAREN")

		block = BlockNode()

		while self.peek().kind not in (
			"RCRBPAREN",
			"EOF",
		):
			stmt = self.parse_stmt()

			if stmt != None:
				block.statements.append(stmt)

		if self.peek().kind == "EOF":
			self.error(
				"Expected '}' before end of file",
				token=self.peek(),
				code=ParserErrorCode.UNEXPECTED_EOF,
			)
		self.expect("RCRBPAREN")

		return block

	def parse_expression(self):
		return self.parse_assignment_expr()

	def _parse_valid_EQ_tok_combo(self):
		tok = self.peek()

		if tok.kind == "ASSIGN":
			self.expect("ASSIGN")
			return "="
		elif tok.raw in "+-/%":
			self.expect("PLUS", "MINUS", "DIVIDE", "MOD", "COLON")
			self.expect("ASSIGN")
			return f"{tok.raw}="
		elif tok.raw == "*":
			self.expect("ASTERISK")
			if self.peek().raw == "*":
				self.expect("ASTERISK")
				self.expect("ASSIGN")
				return "**="
			else:
				self.expect("ASSIGN")
				return "*="

	def parse_assignment_expr(self):
		"""
		* there are 4 cases
		* case 1: ident "vaild_tok" expr
		* case 2: const ident "valid_tok" expr
		* case 3: type ident "valid_tok" expr
		* case 4: const type ident "valid_tok" expr
		"""

		typ = "any"
		is_const = False

		tok = self.peek()
		if tok.kind == "CONST":
			# * case 2, 4
			is_const = True
			self.expect("CONST")
			if (
				self.peek(1).kind == "TYPE"
				or (self.peek(1).kind == "IDENT"
				and self.peek(1).raw in self.types)
			):
				# * case 4
				typ = self.expect("TYPE", "IDENT")
				var_name = self.expect("IDENT")
				op = self._parse_valid_EQ_tok_combo()
				val = self.parse_conditional_expr()
			else:
				# * case 2
				var_name = self.expect("IDENT")
				op = self._parse_valid_EQ_tok_combo()
				val = self.parse_conditional_expr()
		elif (
			tok.kind == "TYPE"
			or (tok.raw in self.types
			and self.peek(1).kind == "IDENT")
		):
			# * case 3
			typ = self.expect("TYPE", "IDENT")
			var_name = self.expect("IDENT")
			op = self._parse_valid_EQ_tok_combo()
			val = self.parse_conditional_expr()
		else:
			tok = self.peek()

			if tok.kind != "IDENT":
				out = self.parse_conditional_expr()
				return out

			save_pos = self.curtok
			var_name = self.expect("IDENT")

			tok = self.peek()
			if tok.kind == "LSQRPAREN":
				return self.parse_index_suffix(var_name)
			else:
				op = self._parse_valid_EQ_tok_combo()

			if op == None:
				self.curtok = save_pos
				out = self.parse_conditional_expr()
				return out

			val = self.parse_conditional_expr()

		if op == None:
			tok = self.peek()
			raise self.error(f"Expected assignment operator, got {tok.kind}", tok)
		else:
			self.expect("EOL")
			return AssignNode(TypeNode(typ) , IdentNode(var_name), value=val, is_const=is_const, operation=op)

	def parse_conditional_expr(self):
		condition = self.parse_logical_or_expr()

		if self.peek().kind == "TIF":
			self.expect("TIF")

			true = self.parse_expression()

			self.expect("COLON")

			false = self.parse_conditional_expr()

			return ConditionalNode(
				condition,
				true,
				false,
			)

		return condition

	def parse_logical_or_expr(self):
		node = self.parse_logical_and_expr()

		while self.peek().kind == "OR":
			op = self.expect("OR")

			right = self.parse_logical_and_expr()

			node = BinaryNode(
				node,
				op,
				right,
			)

		return node

	def parse_logical_and_expr(self):
		node = self.parse_equality_expr()

		while self.peek().kind == "AND":
			op = self.expect("AND")

			right = self.parse_equality_expr()

			node = BinaryNode(
				node,
				op,
				right,
			)

		return node

	def parse_equality_expr(self):
		node = self.parse_comparison_expr()

		while self.peek().kind in (
			"EQ",
			"NE",
		):
			op = self.expect(
				"EQ",
				"NE",
			)

			right = self.parse_comparison_expr()

			node = BinaryNode(
				node,
				op,
				right,
			)

		return node

	def parse_comparison_expr(self):
		node = self.parse_additive_expr()

		while self.peek().kind in (
			"LT",
			"GT",
			"LE",
			"GE",
			"IN",
			"IS",
		):
			op = self.expect(
				"LT",
				"GT",
				"LE",
				"GE",
				"IN",
				"IS",
			)

			right = self.parse_additive_expr()

			node = BinaryNode(
				node,
				op,
				right,
			)

		return node

	def parse_additive_expr(self):
		node = self.parse_multiplicative_expr()

		while (
			self.peek().kind
			in (
				"PLUS",
				"MINUS",
			)
			and self.peek(1).kind != "ASSIGN"
		):
			op = self.expect(
				"PLUS",
				"MINUS",
			)

			right = self.parse_multiplicative_expr()

			node = BinaryNode(
				node,
				op,
				right,
			)

		return node

	def parse_multiplicative_expr(self):
		node = self.parse_unary_expr()

		while (
			self.peek().kind
			in (
				"ASTERISK",
				"DIVIDE",
				"MOD",
			)
			and self.peek(1).kind != "ASSIGN"
		):
			op = self.expect(
				"ASTERISK",
				"DIVIDE",
				"MOD",
			)

			right = self.parse_unary_expr()

			node = BinaryNode(
				node,
				op,
				right,
			)
		return node

	def parse_unary_expr(self):
		if self.peek().kind in (
			"PLUS",
			"MINUS",
			"NOT",
			"AMPERSAND",
			"BITAND",
			"ASTERISK",
		):
			op = self.expect(
				"PLUS",
				"MINUS",
				"NOT",
				"AMPERSAND",
				"BITAND",
				"ASTERISK",
			)

			value = self.parse_unary_expr()

			return UnaryNode(
				op,
				value,
			)

		if (
			self.peek().kind == "LNORPAREN"
			and self.peek(1).kind == "TYPE"
			and self.peek(2).kind == "RNORPAREN"
		):
			self.expect("LNORPAREN")

			typ = self.expect("TYPE")

			self.expect("RNORPAREN")

			value = self.parse_unary_expr()

			return CastNode(
				typ,
				value,
			)

		return self.parse_postfix_expr()

	def parse_postfix_expr(self):
		node = self.parse_primary_expr()

		while True:

			if self.peek().kind == "LNORPAREN":
				node = self.parse_call_suffix(node)

			elif self.peek().kind == "DOT":
				node = self.parse_member_suffix(node)

			elif self.peek().kind == "LSQRPAREN":
				node = self.parse_index_suffix(node)

			else:
				break

		return node

	def parse_member_suffix(self, object):
		self.expect("DOT")

		member = self.expect("IDENT")

		return MemberNode(
			object,
			member,
		)

	def parse_call_suffix(self, function):
		self.expect("LNORPAREN")

		args = []

		if self.peek().kind != "RNORPAREN":

			args.append(self.parse_expression())

			while self.peek().kind == "COMMA":
				self.consume()

				args.append(self.parse_expression())

		self.expect("RNORPAREN")

		return CallNode(
			function,
			args,
		)

	def parse_index_suffix(self, object):
		self.expect("LSQRPAREN")

		start = None
		stop = None
		step = None
		is_slice = False

		if self.peek().kind != "COLON":
			start = self.parse_expression()

		if self.peek().kind == "COLON":
			is_slice = True
			self.expect("COLON")

			if self.peek().kind not in ("RSQRPAREN", "COLON"):
				stop = self.parse_expression()

			if self.peek().kind == "COLON":
				self.expect("COLON")
				if self.peek().kind != "RSQRPAREN":
					step = self.parse_expression()

		self.expect("RSQRPAREN")

		if is_slice:
			return SliceNode(object, start, stop, step)

		return IndexNode(object, start)

	def parse_primary_expr(self):
		tok = self.peek()

		if tok.kind == "IDENT" and tok.raw == "f" and self.peek(1).kind == "STR":
			return self.parse_fstring()

		elif tok.kind in (
			"INT",
			"FLOAT",
			"STR",
			"BOOL",
			"NONE",
			"TYPE",
		):
			return LiteralNode(self.consume())

		elif tok.kind == "IDENT":
			return IdentNode(self.consume())

		elif tok.kind == "LNORPAREN":
			self.expect("LNORPAREN")

			node = self.parse_expression()

			self.expect("RNORPAREN")

			return node

		elif tok.kind == "LSQRPAREN":
			return self.parse_list_literal()

		else:
			self.error(
				f"Unexpected token {tok.raw!r}",
				token=tok,
				code=ParserErrorCode.UNEXPECTED_TOKEN,
			)

	def parse_fstring(self):
		# ima forget so this is for the f in f"" or f''
		self.expect("IDENT")
		string_token = self.expect("STR")

		text = string_token.raw
		parts = []

		pos = 0

		while pos < len(text):
			start = text.find("{", pos)

			if start == -1:
				if pos < len(text):
					parts.append(
						FStringTextNode(text[pos:])
					)
				break

			# Text before {
			if start > pos:
				parts.append(
					FStringTextNode(text[pos:start])
				)

			end = text.find("}", start + 1)

			if end == -1:
				raise SyntaxError(
					f"Unclosed '{{' in f-string "
					f"at {string_token.row}:{string_token.col}"
				)

			expression_text = text[start + 1:end]

			parts.append(
				FStringExprNode(expression_text)
			)

			pos = end + 1

		return FStringNode(parts)

	def parse_list_literal(self):
		self.expect("LSQRPAREN")

		out = self.parse_expression_list()

		self.expect("RSQRPAREN")

		return out

	def parse_expression_list(self):
		out = []

		if self.peek().kind in (
			"RSQRPAREN",
			"RNORPAREN",
		):
			return ExpressionList(out)

		out.append(self.parse_expression())

		while self.peek().kind == "COMMA":
			self.consume()

			if self.peek().kind in (
				"RSQRPAREN",
				"RNORPAREN",
			):
				break

			out.append(self.parse_expression())

		return ExpressionList(out)

if __name__ == "__main__":

	with open(
		"/home/god_spud/STUFFS/GS/example/28_varargs_kwargs_combo.GOS",
		"r",
	) as FILE:
		code = FILE.read()

	tokens = Run().run_lexer(code)

#	for token in tokens:
#		print(token)

	print()

	parser = Parser(
		tokens,
		source=code,
	)

#	try:
	parser.parse()

#	except ParserError as error:
#		print(error)

	if parser.warnings:
		for warning in parser.warnings:
			raise ValueError(warning.format())
