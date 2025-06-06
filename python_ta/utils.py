from typing import ForwardRef, _GenericAlias

from astroid import nodes


def _get_name(t: type) -> str:
    """If t is associated with a class, return the name of the class; otherwise, return a string repr. of t"""
    if isinstance(t, ForwardRef):
        return t.__forward_arg__
    elif isinstance(t, type):
        return t.__name__
    elif isinstance(t, _GenericAlias):
        return "{} of {}".format(
            _get_name(t.__origin__), ", ".join(_get_name(arg) for arg in t.__args__)
        )
    else:
        return str(t)


def _is_in_main(node):
    if not hasattr(node, "parent"):
        return False

    parent = node.parent
    try:
        if (
            isinstance(parent, nodes.If)
            and parent.test.left.name == "__name__"
            and parent.test.ops[0][1].value == "__main__"
        ):
            return True
        else:
            return _is_in_main(parent)
    except (AttributeError, IndexError) as e:
        return _is_in_main(parent)
