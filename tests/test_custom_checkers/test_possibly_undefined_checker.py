import astroid
import pylint.testutils
from astroid import nodes

from python_ta.cfg import CFGVisitor
from python_ta.checkers.possibly_undefined_checker import PossiblyUndefinedChecker
from python_ta.transforms.z3_visitor import Z3Visitor


class TestPossiblyUndefinedChecker(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = PossiblyUndefinedChecker

    def setUp(self):
        self.setup_method()

    def test_no_messages_simple(self):
        src = """
        def test(x):
            x = 10
            if True:
                return x
            return x
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        func_node = mod.body[0]
        name_node_a, name_node_b = mod.nodes_of_class(nodes.Name)

        with self.assertNoMessages():
            self.checker.visit_module(mod)
            self.checker.visit_functiondef(func_node)
            self.checker.visit_name(name_node_a)
            self.checker.visit_name(name_node_b)

    def test_no_messages_with_import(self):
        src = """
        import j

        y = 0
        if y > 10:
            j = 10
        else:
            y = 5
        print(j)
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        name_node_y, name_node_print, name_node_j = mod.nodes_of_class(nodes.Name)
        with self.assertNoMessages():
            self.checker.visit_module(mod)
            self.checker.visit_name(name_node_y)
            self.checker.visit_name(name_node_print)
            self.checker.visit_name(name_node_j)

    def test_no_messages_with_import_from(self):
        src = """
        from random import j

        y = 0
        if y > 10:
            j = 10
        else:
            y = 5
        print(j)
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        name_node_y, name_node_print, name_node_j = mod.nodes_of_class(nodes.Name)
        with self.assertNoMessages():
            self.checker.visit_module(mod)
            self.checker.visit_name(name_node_y)
            self.checker.visit_name(name_node_print)
            self.checker.visit_name(name_node_j)

    def test_no_messages_with_args(self):
        src = """
        def test(x):
            if True:
                x = 10
            print(x)
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        func_node = mod.body[0]
        _, name_node_x = mod.nodes_of_class(nodes.Name)

        with self.assertNoMessages():
            self.checker.visit_functiondef(func_node)
            self.checker.visit_name(name_node_x)

    def test_no_messages_if_else(self):
        src = """
        def test(x):
            if True:
                y = 10
            else:
                y = 20
            print(y)
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        func_node = mod.body[0]
        _, name_node_y = mod.nodes_of_class(nodes.Name)

        with self.assertNoMessages():
            self.checker.visit_functiondef(func_node)
            self.checker.visit_name(name_node_y)

    def test_no_messages_if_else_with_ann_assign(self):
        src = """
        def test(x):
            if True:
                y: int = 10
            else:
                y = 20
            print(y)
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        func_node = mod.body[0]
        _, _, name_node_y = mod.nodes_of_class(nodes.Name)

        with self.assertNoMessages():
            self.checker.visit_functiondef(func_node)
            self.checker.visit_name(name_node_y)

    def test_no_messages_complex(self):
        src = """
        def test(x):
            if True:
                y = 10
            else:
                for j in range(10):
                    if j > 10:
                        y = 10
                        break
                else:
                    y = 10
            return y
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        func_node = mod.body[0]
        _, _, name_node_y = mod.nodes_of_class(nodes.Name)

        with self.assertNoMessages():
            self.checker.visit_functiondef(func_node)
            self.checker.visit_name(name_node_y)

    def test_no_messages_with_nonlocal(self):
        src = """
        def test(x):
            x = 10
            nonlocal y
            if True:
                y = 10
            print(y)
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        func_node = mod.body[0]
        __, name_node_y = mod.nodes_of_class(nodes.Name)

        with self.assertNoMessages():
            self.checker.visit_functiondef(func_node)
            self.checker.visit_name(name_node_y)

    def test_no_messages_with_global(self):
        src = """
        def test(x):
            x = 10
            if True:
                global y
            else:
                y = 10
            print(y)
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        func_node = mod.body[0]
        _, name_node_y = mod.nodes_of_class(nodes.Name)

        with self.assertNoMessages():
            self.checker.visit_functiondef(func_node)
            self.checker.visit_name(name_node_y)

    def test_no_messages_with_class_def(self):
        """This example is a false negative due to how class definitions are
        represented in the control flow graph."""
        src = """
        class A:
            y = 10

        if True:
            x = 10
        else:
            y = 20
        print(y)
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        _, name_node_y = mod.nodes_of_class(nodes.Name)

        self.checker.visit_module(mod)
        with self.assertNoMessages():
            self.checker.visit_name(name_node_y)

    def test_message_with_func_name(self):
        src = """
        if True:
            pass
        else:
            y = lambda: 20
        y()
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        *_, name_node_y = mod.nodes_of_class(nodes.Name)

        self.checker.visit_module(mod)
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(msg_id="possibly-undefined", node=name_node_y),
            ignore_position=True,
        ):
            self.checker.visit_name(name_node_y)

    def test_message_simple(self):
        src = """
        x = 10
        if True:
            y = 10
        else:
            x = 10
        print(x and y)
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        _, name_node_x, name_node_y = mod.nodes_of_class(nodes.Name)

        self.checker.visit_module(mod)
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(msg_id="possibly-undefined", node=name_node_y),
            ignore_position=True,
        ):
            self.checker.visit_name(name_node_y)

        with self.assertNoMessages():
            self.checker.visit_name(name_node_x)

    def test_message_with_del_simple(self):
        src = """
        def test(x):
            y = 0
            del y
            print(y)
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        func_node = mod.body[0]
        _, name_node_y = mod.nodes_of_class(nodes.Name)

        self.checker.visit_functiondef(func_node)
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(msg_id="possibly-undefined", node=name_node_y),
            ignore_position=True,
        ):
            self.checker.visit_name(name_node_y)

    def test_message_with_del_complex(self):
        src = """
        def test(x):
            y = 10
            if True:
                x = 20
            else:
                del y
            print(y)
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        func_node = mod.body[0]
        _, name_node_y = mod.nodes_of_class(nodes.Name)

        self.checker.visit_functiondef(func_node)
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(msg_id="possibly-undefined", node=name_node_y),
            ignore_position=True,
        ):
            self.checker.visit_name(name_node_y)

    def test_message_complex(self):
        src = """
        def test(x):
            if True:
                y = 10
            else:
                for j in range(10):
                    if j > 10:
                        break
                else:
                    y = 10
            return y
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        func_node = mod.body[0]
        _, _, name_node_y = mod.nodes_of_class(nodes.Name)

        self.checker.visit_functiondef(func_node)
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(msg_id="possibly-undefined", node=name_node_y),
            ignore_position=True,
        ):
            self.checker.visit_name(name_node_y)

    def test_message_with_args(self):
        src = """
        def test(x):
            if True:
                del x
            print(x)
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        func_node = mod.body[0]
        _, name_node_x = mod.nodes_of_class(nodes.Name)

        self.checker.visit_functiondef(func_node)
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(msg_id="possibly-undefined", node=name_node_x),
            ignore_position=True,
        ):
            self.checker.visit_name(name_node_x)

    def test_multiple_messages_simple(self):
        src = """
        if True:
            y: int = 10
        else:
            x = 10
        print(x and y)
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        _, _, name_node_x, name_node_y = mod.nodes_of_class(nodes.Name)

        self.checker.visit_module(mod)
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(msg_id="possibly-undefined", node=name_node_y),
            pylint.testutils.MessageTest(msg_id="possibly-undefined", node=name_node_x),
            ignore_position=True,
        ):
            self.checker.visit_name(name_node_y)
            self.checker.visit_name(name_node_x)

    def test_message_with_nested_func(self):
        """This example targets the part of the checker implementation that traverses
        the ast using Node.nodes_of_class or anything equivalent."""
        src = """
        def func(x):
            if True:
                y = 10
            else:
                def func2():
                    y = 20
            print(y)
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        func_node = mod.body[0]
        _, name_node_y = mod.nodes_of_class(nodes.Name)

        self.checker.visit_functiondef(func_node)
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(msg_id="possibly-undefined", node=name_node_y),
            ignore_position=True,
        ):
            self.checker.visit_name(name_node_y)

    def test_with_comprehension(self):
        src = """
        def func(lst):
            test = [x for x in lst]
            x = 0
            print(x)
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        func_node = mod.body[0]
        # expression `x` at line `test = ...`
        name_node_x = next(func_node.nodes_of_class(nodes.Name))

        self.checker.visit_functiondef(func_node)
        with self.assertNoMessages():
            self.checker.visit_name(name_node_x)

    def test_with_dict_comprehension(self):
        src = """
        def func(lst):
            test = {key:val for key, val in lst}
            key = 0
            print(key)
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        func_node = mod.body[0]
        # expression `key` at line `test = ...`
        name_node_key = next(func_node.nodes_of_class(nodes.Name))

        self.checker.visit_functiondef(func_node)
        with self.assertNoMessages():
            self.checker.visit_name(name_node_key)

    def test_assign(self):
        src = """
        def func():
            if False:
                x = 10
            x = x + 1
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        func_node = mod.body[0]
        name_node_x = next(func_node.nodes_of_class(nodes.Name))
        print(list(func_node.nodes_of_class(nodes.Name)))

        self.checker.visit_functiondef(func_node)
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(msg_id="possibly-undefined", node=name_node_x),
            ignore_position=True,
        ):
            self.checker.visit_name(name_node_x)

    def test_prev_generator_flag(self) -> None:
        """Test that this checker no longer falsely flags a comprehension variable for being
        possibly undefined when it shadows a variable in another scope.
        """
        src = """
        def f() -> None:
            if True:
                print(x for x in range(20))
            else:
                for x in range(10):
                    pass
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        func_node = mod.body[0]

        with self.assertNoMessages():
            self.checker.visit_functiondef(func_node)

    def test_prev_incorrect_raise_handling(self) -> None:
        """Test that this checker no longer falsely flags a variable as being possibly undefined
        when it conditionally raises an exception."""
        src = """
        def g(a: int) -> int:
            if a % 3 == 0:
                result = 3
            elif a % 2 == 0:
                result = 2
            else:
                raise NotImplementedError

            return result
        """
        mod = astroid.parse(src)
        mod.accept(CFGVisitor())
        func_node = mod.body[0]

        with self.assertNoMessages():
            self.checker.visit_functiondef(func_node)


class TestPossiblyUndefinedCheckerZ3Option(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = PossiblyUndefinedChecker
    CONFIG = {"z3": True}

    def test_z3_unfeasible_branch(self) -> None:
        src = """
        def func(x: int) -> int:
            '''
            Preconditions:
                - x > 5
            '''
            if x > 3:
                a = 10
            else:
                pass
            return a
        """
        z3v = Z3Visitor()
        mod = z3v.visitor.visit(astroid.parse(src))
        mod.accept(CFGVisitor(z3_enabled=True))
        func_node = mod.body[0]
        *_, name_node = mod.nodes_of_class(nodes.Name)

        self.checker.visit_functiondef(func_node)
        with self.assertNoMessages():
            self.checker.visit_name(name_node)

    def test_z3_unfeasible_assignment(self) -> None:
        src = """
        def func(x: str) -> int:
            '''
            Preconditions:
                - x in ["a", "b", "c"]
            '''
            if x == "a":
                a = 5
            elif x == "d":
                a = 10
            return a
        """
        z3v = Z3Visitor()
        mod = z3v.visitor.visit(astroid.parse(src))
        mod.accept(CFGVisitor(z3_enabled=True))
        func_node = mod.body[0]
        *_, name_node = mod.nodes_of_class(nodes.Name)

        self.checker.visit_functiondef(func_node)
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(msg_id="possibly-undefined", node=name_node),
            ignore_position=True,
        ):
            self.checker.visit_name(name_node)

    def test_z3_unfeasible_deletion(self) -> None:
        src = """
        def func(x: int) -> int:
            '''
            Preconditions:
                - x > 5
            '''
            a = 0
            if x < 0:
                del a
            return a
        """
        z3v = Z3Visitor()
        mod = z3v.visitor.visit(astroid.parse(src))
        mod.accept(CFGVisitor(z3_enabled=True))
        func_node = mod.body[0]
        *_, name_node = mod.nodes_of_class(nodes.Name)

        self.checker.visit_functiondef(func_node)
        with self.assertNoMessages():
            self.checker.visit_name(name_node)

    def test_z3_unfeasible_variable_use(self) -> None:
        src = """
        def func(x: int, y: int) -> int:
            '''
            Preconditions:
                - x > 10
            '''
            if y > 10:
                a = 0
            if x < 10:
                return a
            return 0
        """
        z3v = Z3Visitor()
        mod = z3v.visitor.visit(astroid.parse(src))
        mod.accept(CFGVisitor(z3_enabled=True))
        func_node = mod.body[0]
        *_, name_node = mod.nodes_of_class(nodes.Name)

        self.checker.visit_functiondef(func_node)
        with self.assertNoMessages():
            self.checker.visit_name(name_node)

    def test_z3_variable_defined_by_precondition(self) -> None:
        src = """
        def func(x: int) -> int:
            '''
            Preconditions:
                - x == 0
            '''
            if x == 0:
                a = 10
            return a
        """
        z3v = Z3Visitor()
        mod = z3v.visitor.visit(astroid.parse(src))
        mod.accept(CFGVisitor(z3_enabled=True))
        func_node = mod.body[0]
        *_, name_node = mod.nodes_of_class(nodes.Name)

        self.checker.visit_functiondef(func_node)
        with self.assertNoMessages():
            self.checker.visit_name(name_node)

    def test_z3_partially_unfeasible_assignment(self) -> None:
        src = """
        def func(x: int) -> int:
            '''
            Preconditions:
                - x in {1, 2}
            '''
            if x == 3:
                a = 5
            else:
                a = 10
            return a
        """
        z3v = Z3Visitor()
        mod = z3v.visitor.visit(astroid.parse(src))
        mod.accept(CFGVisitor(z3_enabled=True))
        func_node = mod.body[0]
        *_, name_node = mod.nodes_of_class(nodes.Name)

        self.checker.visit_functiondef(func_node)
        with self.assertNoMessages():
            self.checker.visit_name(name_node)
