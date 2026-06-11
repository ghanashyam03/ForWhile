import sys
from forwhile.lexer import lexer
from forwhile.parser import parser
from forwhile.errors import ForWhileError, ForWhileSyntaxError, ForWhileRuntimeError

# RELATIONSHIP SYSTEM
# What it secretly teaches: object references, pointers, graph traversal
# Why it works: "Alice knows Bob" is the most natural thing in the world.
# A child understands this before they understand variables.

# EVENT SYSTEM
# What it secretly teaches: event-driven programming, the observer
# pattern, callbacks, reactive state
# Why it works: children know that the world reacts to things.
# "When the door opens, the bell rings" needs no explanation.

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

    def get_local_var(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get_local_var(name)
        return None

    def exists_local_var(self, name):
        if name in self.vars:
            return True
        if self.parent:
            return self.parent.exists_local_var(name)
        return False

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
        self.event_rules = []
        self.event_depth = 0
        self.event_context = {}
        self.world_memory = {}
        self.scenes = {}
        self.scene_depth = 0
        self.world_clock = 0
        self.tick_rules = []
        self.strictness = 'strict'

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
            if isinstance(obj_path, list) and len(obj_path) == 0:
                active_creature = self.context_stack[-1]['self'] if self.context_stack else None
                if active_creature and '__class__' in active_creature:
                    class_name = active_creature['__class__']
                    if self.find_trait_def(class_name, attr) is not None:
                        obj_val = active_creature
                    else:
                        obj_val = None
                else:
                    obj_val = None
            else:
                if isinstance(obj_path, list):
                    obj_val = self.resolve_path(obj_path)
                else:
                    obj_val = self.lookup(obj_path)

            if isinstance(obj_val, dict) and '__class__' in obj_val:
                val = self.validate_trait_value(obj_val, attr, val)
                obj_val[attr] = val
                # Fire event rule
                subject_name = self.get_instance_name(obj_val)
                if subject_name:
                    self.fire_event('TRAIT_CHANGED', subject_name, attr)
            else:
                if isinstance(obj_path, list):
                    if len(obj_path) == 0:
                        key = attr
                    else:
                        key = ".".join(obj_path) + f".{attr}"
                else:
                    key = f"{obj_path}.{attr}"
                    
                if self.current_scope:
                    self.current_scope.set(key, val)
                else:
                    self.env[key] = val

        elif op == 'SAY':
            # ('SAY', expr)
            if not self.context_stack:
                raise ForWhileRuntimeError("Speaking ('say') is only allowed inside a creature's action block. Use 'announce' to speak as the narrator.")
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
            traits_defs = {}
            computed_traits = {}
            for member in members:
                if member[0] in ('WHEN_BORN', 'CONSTRUCTOR'):
                    constructor = member
                elif member[0] in ('ACTION', 'METHOD'):
                    methods[member[1]] = member[2]
                elif member[0] == 'TRAITS_BLOCK':
                    for trait_node in member[1]:
                        if trait_node[0] == 'TRAIT_DEF':
                            traits_defs[trait_node[1]] = {
                                'kind': trait_node[2],
                                'constraints': trait_node[3]
                            }
                        elif trait_node[0] == 'COMPUTED_TRAIT':
                            computed_traits[trait_node[1]] = trait_node[2]

            self.classes[class_name] = {
                'parent': parent,
                'constructor': constructor,
                'methods': methods,
                'traits': traits_defs,
                'computed_traits': computed_traits
            }

        elif op == 'WORLD_STRICTNESS':
            self.strictness = node[1]

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
                elif isinstance(args_node, tuple) and args_node[0] == 'LIST_LITERAL':
                    arg_vals = [self.evaluate(arg) for arg in args_node[1]]
                else:
                    arg_vals = [self.evaluate(args_node)]

            # 2. Create and store with relationship support
            new_obj = {
                '__class__': class_name,
                '__knows__': {},
                '__name__': instance_name
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

            # Fire is born event
            self.fire_event('DOES_ACTION', instance_name, 'is born')

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

            # Fire event rule
            subject_name = self.get_instance_name(obj_dict)
            if subject_name:
                self.fire_event('DOES_ACTION', subject_name, action_name)

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

        elif op == 'WHENEVER':
            # ('WHENEVER', trigger_type, subject, action_or_trait, body)
            trigger_type = node[1]
            subject = node[2]
            action_or_trait = node[3]
            body = node[4]

            self.event_rules.append({
                'trigger': (trigger_type, subject, action_or_trait),
                'body': body
            })

        elif op == 'REMOVE':
            # ('REMOVE', name)
            name = node[1]
            if name in self.env:
                obj = self.env[name]
                del self.env[name]
                # Fire dies event
                self.fire_event('DOES_ACTION', name, 'dies', event_context={'the_one_who_died': obj})
            else:
                raise ForWhileRuntimeError(f"Creature or variable '{name}' not found in the world")

        elif op == 'ANNOUNCE':
            # ('ANNOUNCE', expr)
            val = self.evaluate(node[1])
            print(f"[World] {val}")

        elif op == 'WORLD_SET':
            fact_name = node[1]
            val = self.evaluate(node[2])
            self.world_memory[fact_name] = val

        elif op == 'WORLD_FORGET':
            fact_name = node[1]
            if fact_name in self.world_memory:
                del self.world_memory[fact_name]
            else:
                raise ForWhileRuntimeError(f"World memory does not contain fact '{fact_name}'")

        elif op == 'SAVE_WORLD':
            filename = self.evaluate(node[1])
            self.save_world(filename)

        elif op == 'RESTORE_WORLD':
            filename = self.evaluate(node[1])
            self.restore_world(filename)

        elif op == 'SCENE':
            name = node[1]
            params = node[2]
            body = node[3]
            self.scenes[name] = (params, body)

        elif op == 'PLAY_SCENE':
            name = node[1]
            args_exprs = node[2]
            
            if name not in self.scenes:
                raise ForWhileRuntimeError(f"Scene '{name}' is not defined")
                
            params, body = self.scenes[name]
            
            # Evaluate all argument expressions
            arg_vals = [self.evaluate(arg) for arg in args_exprs]
            
            if len(arg_vals) != len(params):
                raise ForWhileRuntimeError(f"Scene '{name}' expects {len(params)} arguments, got {len(arg_vals)}")
                
            self.scene_depth += 1
            if self.scene_depth > 20:
                raise ForWhileRuntimeError("The story is getting too complicated! (scene depth > 20)")
                
            # Bind parameters dynamic-scopingly in self.env
            old_vals = {}
            for param, val in zip(params, arg_vals):
                if param in self.env:
                    old_vals[param] = self.env[param]
                self.env[param] = val
                
            try:
                for stmt in body:
                    self.execute(stmt)
            finally:
                # Restore old parameters
                for param in params:
                    if param in old_vals:
                        self.env[param] = old_vals[param]
                    else:
                        if param in self.env:
                            del self.env[param]
                self.scene_depth -= 1

        elif op == 'TICK_LOOP':
            count = int(self.evaluate(node[1]))
            body = node[2]
            for _ in range(count):
                self.world_clock += 1
                for stmt in body:
                    self.execute(stmt)
                for rule_body in self.tick_rules:
                    for stmt in rule_body:
                        self.execute(stmt)

        elif op == 'ON_TICK':
            self.tick_rules.append(node[1])

        elif op == 'CHARACTER_SAYS':
            name = node[1]
            val = self.evaluate(node[2])
            print(f"[{name}] {val}")

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
            if len(expr) == 0:
                return []
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
            elif op == 'MULTIPLY':
                left = self.evaluate(expr[1])
                right = self.evaluate(expr[2])
                return left * right
            elif op == 'LIST_LITERAL':
                return [self.evaluate(item) for item in expr[1]]
            elif op == 'INPUT':
                return input()
            elif op == 'WORLD_GET':
                fact_name = expr[1]
                if fact_name in self.world_memory:
                    return self.world_memory[fact_name]
                raise ForWhileRuntimeError(f"World memory does not contain fact '{fact_name}'")
            elif op == 'WORLD_ROSTER':
                creature_name = expr[1]
                res = []
                for name, val in self.env.items():
                    if isinstance(val, dict) and '__class__' in val:
                        if self.is_instance_of(val['__class__'], creature_name):
                            res.append(val)
                return res
            elif op == 'WORLD_COUNTS':
                creature_name = expr[1]
                count = 0
                for name, val in self.env.items():
                    if isinstance(val, dict) and '__class__' in val:
                        if self.is_instance_of(val['__class__'], creature_name):
                            count += 1
                return count
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
                if '__class__' in val:
                    class_name = val['__class__']
                    computed_expr = self.find_computed_trait(class_name, attr)
                    if computed_expr is not None:
                        val = self.evaluate_computed_trait(val, computed_expr)
                        continue

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

            left_val = self.evaluate(left_path)
            right_val = self.evaluate(val_expr)

            if comp_op == '>':
                return left_val > right_val
            elif comp_op == '<':
                return left_val < right_val
            elif comp_op in ('==', 'is', 'IS'):
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

    def get_instance_name(self, obj_dict):
        if not isinstance(obj_dict, dict):
            return None
        for name, val in self.env.items():
            if val is obj_dict:
                return name
        return obj_dict.get('__name__', None)

    def fire_event(self, trigger_type, subject, action_or_trait, event_context=None):
        # Prevent infinite loops
        self.event_depth += 1
        if self.event_depth > 10:
            raise ForWhileRuntimeError("The world is stuck in a loop! (event chain deeper than 10)")
        
        # Save old event context
        old_context = getattr(self, 'event_context', None)
        self.event_context = event_context if event_context is not None else {}
        
        try:
            # Find and execute all matching rules
            for rule in self.event_rules:
                r_type, r_sub, r_act_or_trait = rule['trigger']
                if r_type == trigger_type:
                    # Match subject: exact match or rule's subject is 'anyone'
                    if r_sub == 'anyone' or r_sub == subject:
                        # Match action/trait:
                        if r_act_or_trait == action_or_trait:
                            # Execute rule body
                            for stmt in rule['body']:
                                self.execute(stmt)
        finally:
            self.event_context = old_context
            self.event_depth -= 1

    def lookup(self, name):
        # SCOPING
        # What it secretly teaches: local vs global scope, name resolution order
        # self.traits → local scope
        # world memory → global scope
        # The lookup order makes scope intuitive without naming it.
        if name == 'self' and self.context_stack:
            return self.context_stack[-1]['self']
        if name == 'the.one.who.died' and getattr(self, 'event_context', None) and 'the_one_who_died' in self.event_context:
            return self.event_context['the_one_who_died']
        
        # 1. Local variable scope chain (parameters, loop aliases, local variables)
        if self.current_scope and self.current_scope.exists_local_var(name):
            return self.current_scope.get_local_var(name)
            
        # 2. Active creature's traits & computed traits
        active_creature = self.context_stack[-1]['self'] if self.context_stack else None
        if active_creature and isinstance(active_creature, dict):
            if '__class__' in active_creature:
                class_name = active_creature['__class__']
                computed_expr = self.find_computed_trait(class_name, name)
                if computed_expr is not None:
                    return self.evaluate_computed_trait(active_creature, computed_expr)
                trait_def = self.find_trait_def(class_name, name)
                if trait_def is not None:
                    return active_creature.get(name)
            if name in active_creature:
                return active_creature[name]
            
        # 3. Global environment (creatures/globals)
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

    def is_instance_of(self, class_name, target_class):
        curr = class_name
        while curr:
            if curr == target_class:
                return True
            cls_info = self.classes.get(curr)
            if cls_info:
                curr = cls_info.get('parent')
            else:
                break
        return False

    def save_world(self, filename):
        serialized_creatures = {}
        serialized_variables = {}
        
        # Identify all top-level creatures in env
        creature_names = set()
        for name, val in self.env.items():
            if isinstance(val, dict) and '__class__' in val:
                creature_names.add(name)
                
        def to_jsonable(val, current_creature_name=None, trait_name=None):
            if isinstance(val, (int, float, str, bool)) or val is None:
                return val
            if isinstance(val, list):
                res = []
                for item in val:
                    try:
                        res.append(to_jsonable(item, current_creature_name, trait_name))
                    except TypeError:
                        print(f"Warning: could not save {current_creature_name or 'world'}'s {trait_name or 'list item'}")
                return res
            if isinstance(val, dict):
                # If it is a top-level creature reference
                if '__class__' in val and '__name__' in val and val['__name__'] in creature_names and self.env[val['__name__']] is val:
                    return {'__ref__': val['__name__']}
                # Otherwise, serialize the dict inline
                res = {}
                for k, v in val.items():
                    try:
                        res[k] = to_jsonable(v, current_creature_name or val.get('__name__') or val.get('__class__'), k)
                    except TypeError:
                        print(f"Warning: could not save {current_creature_name or val.get('__name__') or val.get('__class__') or 'creature'}'s {k}")
                return res
            raise TypeError(f"Type {type(val)} is not serializable")

        # Serialize top-level creatures
        for name in creature_names:
            creature_dict = self.env[name]
            res = {}
            for k, v in creature_dict.items():
                try:
                    res[k] = to_jsonable(v, name, k)
                except TypeError:
                    print(f"Warning: could not save {name}'s {k}")
            serialized_creatures[name] = res
            
        # Serialize top-level variables
        for name, val in self.env.items():
            if name not in creature_names:
                try:
                    serialized_variables[name] = to_jsonable(val, 'world', name)
                except TypeError:
                    print(f"Warning: could not save world's {name}")
                    
        data = {
            'world_memory': self.world_memory,
            'world_clock': self.world_clock,
            'strictness': self.strictness,
            'creatures': serialized_creatures,
            'variables': serialized_variables
        }
        
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def restore_world(self, filename):
        import json
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise ForWhileRuntimeError(f"World save file '{filename}' not found")
            
        # Clear current env and world memory
        self.env.clear()
        self.world_memory = data.get('world_memory', {})
        self.world_clock = data.get('world_clock', 0)
        self.strictness = data.get('strictness', 'strict')

        # Step 1: Recreate all creature dicts (without resolving references)
        creatures_data = data.get('creatures', {})
        restored_creatures = {}
        for name, c_data in creatures_data.items():
            restored_creatures[name] = {
                '__class__': c_data['__class__'],
                '__knows__': {},
                '__name__': c_data.get('__name__', name)
            }
            self.env[name] = restored_creatures[name]
            
        # Step 2: Helper to restore values and references recursively
        def from_jsonable(val):
            if isinstance(val, dict):
                if '__ref__' in val:
                    ref_name = val['__ref__']
                    if ref_name in restored_creatures:
                        return restored_creatures[ref_name]
                    return None
                res = {}
                for k, v in val.items():
                    res[k] = from_jsonable(v)
                return res
            if isinstance(val, list):
                return [from_jsonable(item) for item in val]
            return val
            
        # Step 3: Populate traits of creatures
        for name, c_data in creatures_data.items():
            creature_obj = restored_creatures[name]
            for k, v in c_data.items():
                if k not in ('__class__', '__name__'):
                    creature_obj[k] = from_jsonable(v)
                    
        # Step 4: Populate variables in env
        variables_data = data.get('variables', {})
        for name, val in variables_data.items():
            self.env[name] = from_jsonable(val)

    def evaluate_computed_trait(self, obj_dict, expr):
        self.context_stack.append({'self': obj_dict})
        try:
            return self.evaluate(expr)
        finally:
            self.context_stack.pop()

    def find_trait_def(self, class_name, trait_name):
        cls = self.classes.get(class_name)
        if not cls:
            return None
        traits = cls.get('traits', {})
        if trait_name in traits:
            return traits[trait_name]
        parent = cls.get('parent')
        if parent:
            return self.find_trait_def(parent, trait_name)
        return None

    def find_computed_trait(self, class_name, trait_name):
        cls = self.classes.get(class_name)
        if not cls:
            return None
        computed = cls.get('computed_traits', {})
        if trait_name in computed:
            return computed[trait_name]
        parent = cls.get('parent')
        if parent:
            return self.find_computed_trait(parent, trait_name)
        return None

    def validate_trait_value(self, obj_val, attr, val):
        class_name = obj_val['__class__']
        trait_def = self.find_trait_def(class_name, attr)
        if not trait_def:
            return val

        kind = trait_def['kind']
        constraints = trait_def['constraints']

        if kind == 'word':
            if not isinstance(val, str):
                if self.strictness == 'strict':
                    raise ForWhileRuntimeError(f"{class_name}s can't have a {attr} of {val} — it must be a word.")
                else:
                    print(f"[Warning] {class_name}s can't have a {attr} of {val} — it must be a word.")
        elif kind == 'number':
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                if self.strictness == 'strict':
                    raise ForWhileRuntimeError(f"{class_name}s can't have a {attr} of {val} — it must be a number.")
                else:
                    print(f"[Warning] {class_name}s can't have a {attr} of {val} — it must be a number.")
        elif kind == 'number_range':
            min_val = self.evaluate(constraints[0])
            max_val = self.evaluate(constraints[1])
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                if self.strictness == 'strict':
                    raise ForWhileRuntimeError(f"{class_name}s can't have a {attr} of {val} — it must be a number between {min_val} and {max_val}.")
                else:
                    print(f"[Warning] {class_name}s can't have a {attr} of {val} — it must be a number between {min_val} and {max_val}.")
            elif val < min_val or val > max_val:
                if self.strictness == 'strict':
                    raise ForWhileRuntimeError(f"{class_name}s can't have a {attr} of {val} — it must be between {min_val} and {max_val}.")
                else:
                    print(f"[Warning] {class_name}s can't have a {attr} of {val} — it must be between {min_val} and {max_val}.")
                    val = max(min_val, min(val, max_val))
        elif kind == 'enum':
            allowed = self.evaluate(constraints)
            if not isinstance(allowed, list):
                allowed = [allowed]
            
            matched = False
            if isinstance(val, str):
                for a in allowed:
                    if isinstance(a, str) and a.lower() == val.lower():
                        val = a
                        matched = True
                        break
            if not matched:
                matched = (val in allowed)

            if not matched:
                val_print = f"'{val}'" if isinstance(val, str) else str(val)
                plural_attr = attr + 's' if not attr.endswith('s') else attr
                if self.strictness == 'strict':
                    raise ForWhileRuntimeError(f"The {attr} {val_print} isn't one of {class_name}'s allowed {plural_attr}.")
                else:
                    print(f"[Warning] The {attr} {val_print} isn't one of {class_name}'s allowed {plural_attr}.")
        elif kind == 'boolean':
            if not isinstance(val, bool):
                if self.strictness == 'strict':
                    raise ForWhileRuntimeError(f"{class_name}s can't have a {attr} of {val} — it must be yes or no.")
                else:
                    print(f"[Warning] {class_name}s can't have a {attr} of {val} — it must be yes or no.")
                    val = bool(val)
        elif kind == 'list':
            if not isinstance(val, list):
                if self.strictness == 'strict':
                    raise ForWhileRuntimeError(f"{class_name}s can't have a {attr} of {val} — it must be a list.")
                else:
                    print(f"[Warning] {class_name}s can't have a {attr} of {val} — it must be a list.")
                    val = [val]

        return val

def repl():
    print("ForWhile Interactive REPL")
    print("Type your code. Press Enter on an empty line at the top level to exit.")
    interpreter = Interpreter()
    
    buffer = []
    nesting_level = 0
    open_keywords = {'creature', 'class', 'action', 'method', 'repeat', 'until', 'whenever', 'scene', 'when', 'if', 'on'}
    
    while True:
        try:
            prompt = "fw> " if nesting_level == 0 else "..  "
            line = input(prompt)
            if nesting_level == 0 and line.strip() == "":
                break
                
            buffer.append(line)
            tokens = line.strip().lower().split()
            if tokens:
                first = tokens[0]
                if first in open_keywords:
                    if first == 'when':
                        if len(tokens) > 1 and tokens[1] == 'born':
                            nesting_level += 1
                        else:
                            nesting_level += 1
                    elif first == 'on':
                        if len(tokens) > 2 and tokens[1] == 'each' and tokens[2] == 'tick':
                            nesting_level += 1
                    else:
                        nesting_level += 1
                elif first == 'end':
                    nesting_level = max(0, nesting_level - 1)
                    
            if nesting_level == 0:
                code = "\n".join(buffer)
                buffer.clear()
                if code.strip():
                    try:
                        ast = parser.parse(code)
                        if ast is not None:
                            interpreter.run(ast)
                        else:
                            print("[Error] Failed to parse input.")
                    except ForWhileError as e:
                        print(str(e))
                    except Exception as e:
                        print(f"[Runtime Error] {e}")
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")
            buffer.clear()
            nesting_level = 0
        except EOFError:
            print()
            break

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
        repl()
    else:
        run_file(sys.argv[1])

if __name__ == "__main__":
    main()
