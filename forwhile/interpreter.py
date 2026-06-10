import sys
from forwhile.lexer import lexer
from forwhile.parser import parser
from forwhile.errors import ForWhileError, ForWhileSyntaxError, ForWhileRuntimeError

# RELATIONSHIP SYSTEM
# What it secretly teaches: object references, pointers, graph traversal
# Why it works: "Alice knows Bob" is the most natural thing in the world.
# A child understands this before they understand variables.

class Scope:
    """Represents a local variable and active creature scope."""
    def __init__(self, parent=None, interpreter=None):
        self.parent = parent
        self.vars = {}
        self.interpreter = interpreter

    def get_active_creature(self):
        if self.interpreter and self.interpreter.context_stack:
            return self.interpreter.context_stack[-1]['self']
        return None

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        active_obj = self.get_active_creature()
        if active_obj and isinstance(active_obj, dict) and name in active_obj:
            return active_obj[name]
        if self.parent:
            return self.parent.get(name)
        return None

    def exists(self, name):
        if name in self.vars:
            return True
        active_obj = self.get_active_creature()
        if active_obj and isinstance(active_obj, dict) and name in active_obj:
            return True
        if self.parent:
            return self.parent.exists(name)
        return False

    def set(self, name, value):
        active_obj = self.get_active_creature()
        if active_obj and isinstance(active_obj, dict) and name in active_obj:
            active_obj[name] = value
        else:
            self.vars[name] = value

class Interpreter:
    """The tree-walk interpreter for ForWhile AST."""
    def __init__(self):
        self.env = {}
        self.classes = {}
        self.current_scope = None
        self.context_stack = []  # Keeps track of {'self': instance_dict}

    def run(self, ast):
        if not ast:
            return
        for node in ast:
            self.execute(node)

    def execute(self, node):
        if not isinstance(node, tuple):
            raise ForWhileRuntimeError(f"Invalid statement node: {node}")

        op = node[0]

        # Support both legacy SET and new GIVE_TRAIT
        if op in ('GIVE_TRAIT', 'SET'):
            # ('GIVE_TRAIT', obj_path, attr, expr)
            obj_path = node[1]
            attr = node[2]
            expr = node[3]
            val = self.evaluate(expr)

            # Resolve obj_path
            if isinstance(obj_path, list):
                obj_val = self.resolve_path(obj_path)
            else:
                obj_val = self.lookup(obj_path)

            if isinstance(obj_val, dict) and '__class__' in obj_val:
                obj_val[attr] = val
            else:
                if isinstance(obj_path, list):
                    key = ".".join(obj_path) + f".{attr}"
                else:
                    key = f"{obj_path}.{attr}"
                    
                if self.current_scope:
                    self.current_scope.set(key, val)
                else:
                    self.env[key] = val

        elif op == 'SAY':
            # ('SAY', expr)
            val = self.evaluate(node[1])
            print(val)

        elif op == 'ASK':
            # ('ASK', question)
            val = self.evaluate(node[1])
            print(val)

        elif op == 'REPEAT':
            # ('REPEAT', count_int, [list_of_statements])
            count = int(self.evaluate(node[1]))
            body = node[2]
            for _ in range(count):
                for stmt in body:
                    self.execute(stmt)

        elif op == 'REPEAT_THROUGH':
            # ('REPEAT_THROUGH', collection_expr, alias_path, body)
            collection = self.evaluate(node[1])
            alias_path = node[2]
            body = node[3]

            if collection is None:
                collection = []
            elif not isinstance(collection, list):
                collection = [collection]

            alias_key = ".".join(alias_path)

            for item in collection:
                loop_scope = Scope(parent=self.current_scope, interpreter=self)
                loop_scope.set(alias_key, item)

                old_scope = self.current_scope
                self.current_scope = loop_scope
                try:
                    for stmt in body:
                        self.execute(stmt)
                finally:
                    self.current_scope = old_scope

        elif op == 'UNTIL':
            # ('UNTIL', condition, [list_of_statements])
            cond_node = node[1]
            body = node[2]

            while True:
                cond_res = self.evaluate_condition(cond_node)
                if cond_res:
                    break
                for stmt in body:
                    self.execute(stmt)

        elif op == 'IF':
            # ('IF', condition_node, [then_stmts], [else_stmts])
            cond_node = node[1]
            then_stmts = node[2]
            else_stmts = node[3]

            cond_res = self.evaluate_condition(cond_node)

            if cond_res:
                for stmt in then_stmts:
                    self.execute(stmt)
            else:
                for stmt in else_stmts:
                    self.execute(stmt)

        # Support both legacy CLASS and new CREATURE
        elif op in ('CREATURE', 'CLASS'):
            # ('CREATURE', 'ClassName', parent_or_None, [class_members])
            class_name = node[1]
            parent = node[2]
            members = node[3]

            constructor = None
            methods = {}
            for member in members:
                if member[0] in ('WHEN_BORN', 'CONSTRUCTOR'):
                    constructor = member
                elif member[0] in ('ACTION', 'METHOD'):
                    methods[member[1]] = member[2]

            self.classes[class_name] = {
                'parent': parent,
                'constructor': constructor,
                'methods': methods
            }

        # Support both legacy CREATE and new BRING_TO_LIFE
        elif op in ('BRING_TO_LIFE', 'CREATE'):
            # ('BRING_TO_LIFE', 'ClassName', 'instanceName', args)
            class_name = node[1]
            instance_name = node[2]
            args_node = node[3]

            # 1. Evaluate args first
            arg_vals = []
            if args_node is not None:
                if isinstance(args_node, list):
                    arg_vals = [self.evaluate(arg) for arg in args_node]
                else:
                    arg_vals = [self.evaluate(args_node)]

            # 2. Create and store with relationship support
            new_obj = {
                '__class__': class_name,
                '__knows__': {}
            }
            self.env[instance_name] = new_obj

            constructor = self.find_constructor(class_name)
            if constructor:
                params = constructor[1]
                body = constructor[2]

                self.context_stack.append({'self': new_obj})

                constructor_scope = Scope(parent=self.current_scope, interpreter=self)
                if params:
                    for i, param in enumerate(params):
                        if i < len(arg_vals):
                            constructor_scope.set(param, arg_vals[i])
                        else:
                            constructor_scope.set(param, None)

                constructor_scope.set('self', new_obj)
                constructor_scope.set(instance_name, new_obj)

                old_scope = self.current_scope
                self.current_scope = constructor_scope
                try:
                    for stmt in body:
                        self.execute(stmt)
                finally:
                    self.current_scope = old_scope
                    self.context_stack.pop()

        elif op == 'ATTACH':
            # ('ATTACH', part_path, target_path)
            part_path = node[1]
            target_path = node[2]

            if isinstance(target_path, list):
                target_obj = self.resolve_path(target_path)
            else:
                target_obj = self.lookup(target_path)

            if not isinstance(target_obj, dict) or '__class__' not in target_obj:
                print_name = " ".join(target_path) if isinstance(target_path, list) else target_path
                raise ForWhileRuntimeError(f"Target '{print_name}' is not a valid creature instance")

            part_class = part_path[0] if isinstance(part_path, list) else part_path

            part_obj = {
                '__class__': part_class,
                '__knows__': {}
            }

            constructor = self.find_constructor(part_class)
            if constructor:
                params = constructor[1]
                body = constructor[2]

                self.context_stack.append({'self': part_obj})
                constructor_scope = Scope(parent=self.current_scope, interpreter=self)
                if params:
                    for param in params:
                        constructor_scope.set(param, None)

                old_scope = self.current_scope
                self.current_scope = constructor_scope
                try:
                    for stmt in body:
                        self.execute(stmt)
                finally:
                    self.current_scope = old_scope
                    self.context_stack.pop()

            target_obj[part_class] = part_obj

        # Support both legacy CALL and new DOES_ACTION
        elif op in ('DOES_ACTION', 'CALL'):
            # ('DOES_ACTION', instance_path, actionName)
            instance_path = node[1]
            action_name = node[2]

            if isinstance(instance_path, list):
                obj_dict = self.resolve_path(instance_path)
            else:
                obj_dict = self.lookup(instance_path)

            if not isinstance(obj_dict, dict) or '__class__' not in obj_dict:
                print_name = " ".join(instance_path) if isinstance(instance_path, list) else instance_path
                raise ForWhileRuntimeError(f"'{print_name}' is not a valid creature instance")

            class_name = obj_dict['__class__']
            action_body = self.find_method(class_name, action_name)
            if not action_body:
                raise ForWhileRuntimeError(f"Action '{action_name}' not found in creature '{class_name}' (or its parents)")

            self.context_stack.append({'self': obj_dict})

            action_scope = Scope(parent=self.current_scope, interpreter=self)

            old_scope = self.current_scope
            self.current_scope = action_scope
            try:
                for stmt in action_body:
                    self.execute(stmt)
            finally:
                self.current_scope = old_scope
                self.context_stack.pop()

        elif op == 'KNOWS':
            # ('KNOWS', a, b, role)
            a_path = node[1]
            b_path = node[2]
            role = node[3]

            a_obj = self.resolve_path(a_path)
            b_obj = self.resolve_path(b_path)

            if not isinstance(a_obj, dict) or '__class__' not in a_obj:
                print_name = " ".join(a_path)
                raise ForWhileRuntimeError(f"'{print_name}' is not a valid creature instance")
            if not isinstance(b_obj, dict) or '__class__' not in b_obj:
                print_name = " ".join(b_path)
                raise ForWhileRuntimeError(f"'{print_name}' is not a valid creature instance")

            if role is None:
                role = b_obj['__class__'].lower()

            knows_dict = a_obj['__knows__']
            if role in knows_dict:
                existing = knows_dict[role]
                if isinstance(existing, list):
                    if b_obj not in existing:
                        existing.append(b_obj)
                else:
                    if existing != b_obj:
                        knows_dict[role] = [existing, b_obj]
            else:
                knows_dict[role] = b_obj

        elif op == 'FORGETS':
            # ('FORGETS', name_path, role)
            name_path = node[1]
            role = node[2]

            obj = self.resolve_path(name_path)
            if not isinstance(obj, dict) or '__class__' not in obj:
                print_name = " ".join(name_path)
                raise ForWhileRuntimeError(f"'{print_name}' is not a valid creature instance")

            if '__knows__' in obj and role in obj['__knows__']:
                del obj['__knows__'][role]

        else:
            raise ForWhileRuntimeError(f"Unknown node type: {op}")

    def evaluate(self, expr):
        if isinstance(expr, (int, float)):
            return expr
        if isinstance(expr, str):
            val = self.lookup(expr)
            if val is not None:
                return val
            return expr
        if isinstance(expr, list):
            # Resolve attribute path directly
            return self.resolve_path(expr)
        if isinstance(expr, tuple):
            op = expr[0]
            if op == 'ADD':
                left = self.evaluate(expr[1])
                right = self.evaluate(expr[2])
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            elif op == 'MINUS':
                left = self.evaluate(expr[1])
                right = self.evaluate(expr[2])
                return left - right
            elif op == 'ATTRIBUTE':
                obj = expr[1]
                attr = expr[2]
                return self.resolve_path([obj, attr])
            elif op == 'INPUT':
                return input()
            else:
                raise ForWhileRuntimeError(f"Unknown expression type: {op}")
        raise ForWhileRuntimeError(f"Invalid expression: {expr}")

    def resolve_path(self, path):
        if not path:
            return None

        # 1. Try flat joined key first
        joined = ".".join(path)
        val = self.lookup(joined)
        if val is not None:
            return val

        # 2. Try longest prefix matching
        val = None
        prefix_len = 0
        for i in range(len(path), 0, -1):
            prefix = ".".join(path[:i])
            val = self.lookup(prefix)
            if val is not None:
                prefix_len = i
                break

        if prefix_len == 0:
            if len(path) == 1:
                return path[0]
            raise ForWhileRuntimeError(f"Creature or variable '{path[0]}' is not defined")

        # 3. Traverse path attributes & relationships
        for attr in path[prefix_len:]:
            if isinstance(val, dict):
                if attr in val:
                    val = val[attr]
                elif '__knows__' in val:
                    knows = val['__knows__']
                    if attr in knows:
                        val = knows[attr]
                    elif attr.endswith('s') and attr[:-1] in knows:
                        val = knows[attr[:-1]]
                        if not isinstance(val, list):
                            val = [val]
                    elif attr == 'children' and 'child' in knows:
                        val = knows['child']
                        if not isinstance(val, list):
                            val = [val]
                    else:
                        raise ForWhileRuntimeError(f"Trait or relationship '{attr}' not found on creature '{val.get('name', 'creature')}'")
                else:
                    raise ForWhileRuntimeError(f"Trait '{attr}' not found on creature")
            else:
                raise ForWhileRuntimeError(f"Cannot access attribute '{attr}' on non-creature value")

        return val

    def evaluate_condition(self, cond_node):
        if cond_node[0] == 'CONDITION':
            left_path = cond_node[1]
            comp_op = cond_node[2]
            val_expr = cond_node[3]

            left_val = self.resolve_path(left_path)
            right_val = self.evaluate(val_expr)

            if comp_op == '>':
                return left_val > right_val
            elif comp_op == '<':
                return left_val < right_val
            elif comp_op == '==':
                return left_val == right_val
            elif comp_op == '!=':
                return left_val != right_val
            else:
                raise ForWhileRuntimeError(f"Unknown comparison operator: {comp_op}")

        elif cond_node[0] == 'KNOWS_COND':
            obj_path = cond_node[1]
            other_val = cond_node[2]  # Can be list representing path, or string 'anyone'
            role = cond_node[3]

            obj = self.resolve_path(obj_path)
            if not isinstance(obj, dict) or '__class__' not in obj:
                print_name = " ".join(obj_path)
                raise ForWhileRuntimeError(f"'{print_name}' is not a valid creature instance")

            knows_dict = obj.get('__knows__', {})

            if other_val == 'anyone':
                if role is None:
                    return len(knows_dict) > 0
                return role in knows_dict
            else:
                other_obj = self.resolve_path(other_val)
                if not isinstance(other_obj, dict) or '__class__' not in other_obj:
                    print_name = " ".join(other_val)
                    raise ForWhileRuntimeError(f"'{print_name}' is not a valid creature instance")

                if role is None:
                    for val in knows_dict.values():
                        if isinstance(val, list):
                            if other_obj in val:
                                return True
                        elif val == other_obj:
                            return True
                    return False
                else:
                    if role not in knows_dict:
                        return False
                    val = knows_dict[role]
                    if isinstance(val, list):
                        return other_obj in val
                    return val == other_obj

        raise ForWhileRuntimeError(f"Unknown condition type: {cond_node[0]}")

    def lookup(self, name):
        if name == 'self' and self.context_stack:
            return self.context_stack[-1]['self']
        if self.current_scope and self.current_scope.exists(name):
            return self.current_scope.get(name)
        if name in self.env:
            return self.env[name]
        return None

    def find_constructor(self, class_name):
        cls = self.classes.get(class_name)
        if not cls:
            raise ForWhileRuntimeError(f"Creature type '{class_name}' is not defined")
        if cls['constructor']:
            return cls['constructor']
        if cls['parent']:
            return self.find_constructor(cls['parent'])
        return None

    def find_method(self, class_name, method_name):
        cls = self.classes.get(class_name)
        if not cls:
            raise ForWhileRuntimeError(f"Creature type '{class_name}' is not defined")
        if method_name in cls['methods']:
            return cls['methods'][method_name]
        if cls['parent']:
            return self.find_method(cls['parent'], method_name)
        return None

def run_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"[ForWhile Error] File '{path}' not found.")
        sys.exit(1)

    try:
        ast = parser.parse(code)
        if ast is None:
            raise ForWhileSyntaxError("Failed to parse program.")
        interpreter = Interpreter()
        interpreter.run(ast)
    except ForWhileError as e:
        print(str(e))
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: forwhile <filename.fw>")
        sys.exit(1)
    run_file(sys.argv[1])

if __name__ == "__main__":
    main()
