import sys
from forwhile.lexer import lexer
from forwhile.parser import parser
from forwhile.errors import ForWhileError, ForWhileSyntaxError, ForWhileRuntimeError

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
            # ('GIVE_TRAIT', obj, attr, expr)
            obj = node[1]
            attr = node[2]
            expr = node[3]
            val = self.evaluate(expr)

            # Resolve obj
            obj_val = self.lookup(obj)
            if isinstance(obj_val, dict) and '__class__' in obj_val:
                obj_val[attr] = val
            else:
                key = f"{obj}.{attr}"
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

        elif op == 'UNTIL':
            # ('UNTIL', condition, [list_of_statements])
            cond_node = node[1]
            body = node[2]

            if cond_node[0] != 'CONDITION':
                raise ForWhileRuntimeError(f"Invalid condition node: {cond_node}")

            obj = cond_node[1]
            attr = cond_node[2]
            comp_op = cond_node[3]
            val_expr = cond_node[4]

            # Loop until condition is met (returns True)
            while True:
                left_val = self.evaluate(('ATTRIBUTE', obj, attr))
                right_val = self.evaluate(val_expr)

                if comp_op == '>':
                    cond_res = left_val > right_val
                elif comp_op == '<':
                    cond_res = left_val < right_val
                elif comp_op == '==':
                    cond_res = left_val == right_val
                elif comp_op == '!=':
                    cond_res = left_val != right_val
                else:
                    raise ForWhileRuntimeError(f"Unknown comparison operator: {comp_op}")

                if cond_res:
                    break

                for stmt in body:
                    self.execute(stmt)

        elif op == 'IF':
            # ('IF', ('CONDITION', obj, attr, op, value), [then_stmts], [else_stmts])
            cond_node = node[1]
            then_stmts = node[2]
            else_stmts = node[3]

            if cond_node[0] != 'CONDITION':
                raise ForWhileRuntimeError(f"Invalid condition node: {cond_node}")

            obj = cond_node[1]
            attr = cond_node[2]
            comp_op = cond_node[3]
            val_expr = cond_node[4]

            left_val = self.evaluate(('ATTRIBUTE', obj, attr))
            right_val = self.evaluate(val_expr)

            if comp_op == '>':
                cond_res = left_val > right_val
            elif comp_op == '<':
                cond_res = left_val < right_val
            elif comp_op == '==':
                cond_res = left_val == right_val
            elif comp_op == '!=':
                cond_res = left_val != right_val
            else:
                raise ForWhileRuntimeError(f"Unknown comparison operator: {comp_op}")

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
                # Support both new WHEN_BORN / ACTION and legacy CONSTRUCTOR / METHOD
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

            # 1. Evaluate args BEFORE creating and binding the new object to avoid resolution conflicts
            arg_vals = []
            if args_node is not None:
                if isinstance(args_node, list):
                    arg_vals = [self.evaluate(arg) for arg in args_node]
                else:
                    arg_vals = [self.evaluate(args_node)]

            # 2. Instantiate and store
            new_obj = {
                '__class__': class_name
            }
            self.env[instance_name] = new_obj

            constructor = self.find_constructor(class_name)
            if constructor:
                params = constructor[1]
                body = constructor[2]

                # Push context stack
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
            # ('ATTACH', 'PartClass', 'TargetInstance')
            part_class = node[1]
            target_instance = node[2]

            target_obj = self.lookup(target_instance)
            if not isinstance(target_obj, dict) or '__class__' not in target_obj:
                raise ForWhileRuntimeError(f"Target '{target_instance}' is not a valid creature instance")

            part_obj = {
                '__class__': part_class
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
            # ('DOES_ACTION', 'instanceName', 'actionName')
            instance_name = node[1]
            action_name = node[2]

            obj_dict = self.lookup(instance_name)
            if not isinstance(obj_dict, dict) or '__class__' not in obj_dict:
                raise ForWhileRuntimeError(f"'{instance_name}' is not a valid creature instance")

            class_name = obj_dict['__class__']
            action_body = self.find_method(class_name, action_name)
            if not action_body:
                raise ForWhileRuntimeError(f"Action '{action_name}' not found in creature '{class_name}' (or its parents)")

            # Push context stack
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
                obj_val = self.lookup(obj)
                if isinstance(obj_val, dict) and '__class__' in obj_val:
                    if attr in obj_val:
                        return obj_val[attr]
                    raise ForWhileRuntimeError(f"Trait '{attr}' not found on creature '{obj}'")
                else:
                    key = f"{obj}.{attr}"
                    val = self.lookup(key)
                    if val is not None:
                        return val
                    raise ForWhileRuntimeError(f"Trait '{obj} {attr}' is not defined")
            elif op == 'INPUT':
                return input()
            else:
                raise ForWhileRuntimeError(f"Unknown expression type: {op}")
        raise ForWhileRuntimeError(f"Invalid expression: {expr}")

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
