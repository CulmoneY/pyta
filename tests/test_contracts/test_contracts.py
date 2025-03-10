from __future__ import annotations

import sys
from typing import Dict, Generic, List, Set, TypeVar, Union

import pytest
from nested_preconditions_example import Student, my_function

import python_ta.contracts
from python_ta.contracts import check_contracts


def test_nullary_return_int() -> None:
    """Calling a nullary function with the correct return type (int)."""

    @check_contracts
    def nullary() -> int:
        return 1

    nullary()


def test_nullary_return_float() -> None:
    """Calling a nullary function with the correct return type (float)."""

    @check_contracts
    def nullary() -> float:
        return 1.0

    nullary()


def test_nullary_return_dict() -> None:
    """Calling a nullary function with the correct return type (Dict)."""

    @check_contracts
    def nullary() -> Dict[str, int]:
        return {"one": 1}

    nullary()


def test_nullary_return_bool() -> None:
    """Calling a nullary function with the correct return type (Bool)."""

    @check_contracts
    def nullary() -> bool:
        return True

    nullary()


def test_nullary_return_none() -> None:
    """Calling a nullary function with the correct return type (None)."""

    @check_contracts
    def nullary() -> None:
        3 + 4

    nullary()


def test_nullary_return_wrong_type() -> None:
    """Calling a nullary function with the incorrect return type."""

    @check_contracts
    def nullary() -> str:
        return 1

    with pytest.raises(AssertionError):
        nullary()


def test_nullary_return_dict_wrong() -> None:
    """Calling a nullary function with the incorrect return type (Dict)."""

    @check_contracts
    def nullary() -> Dict[str, int]:
        return {1: 1}

    with pytest.raises(AssertionError):
        nullary()


def test_nullary_return_int_float_error() -> None:
    """Calling a nullary function with return type int, got float"""

    @check_contracts
    def nullary() -> int:
        return 1.5

    with pytest.raises(AssertionError):
        nullary()


def test_nullary_return_float_int_error() -> None:
    """Calling a nullary function with return type float, got int"""

    @check_contracts
    def nullary() -> float:
        return 1

    with pytest.raises(AssertionError):
        nullary()


def test_nullary_return_int_bool_error() -> None:
    """Calling a nullary function with return type int, got bool"""

    @check_contracts
    def nullary() -> int:
        return True

    with pytest.raises(AssertionError):
        nullary()


def test_nullary_return_bool_int_error() -> None:
    """Calling a nullary function with return type bool, got int"""

    @check_contracts
    def nullary() -> bool:
        return 1

    with pytest.raises(AssertionError):
        nullary()


def test_nullary_int_bool_disable_contract_checking(disable_contract_checking) -> None:
    """Calling a nullary function with incorrect return type and with ENABLE_CONTRACT_CHECKING disabled so no error
    is raised."""

    @check_contracts
    def nullary() -> int:
        return True

    nullary()


def test_nullary_no_return_type() -> None:
    """Calling a nullary function with no specified return type passes."""

    @check_contracts
    def nullary():
        return "string"

    nullary()


@check_contracts
def _my_sum(numbers: List[int]) -> int:
    return sum(numbers)


def test_my_sum_list_int_argument() -> None:
    """Calling _my_sum with a list of integers passes type check."""
    _my_sum([1, 2, 3])


def test_my_sum_float_argument() -> None:
    """Calling _my_sum with a list of floats fails type check."""
    with pytest.raises(AssertionError):
        _my_sum([1.5, 2.0])


def test_my_sum_empty_list_argument() -> None:
    """Calling _my_sum with an empty list passes type check."""
    _my_sum([])


def test_my_sum_list_mixed_argument() -> None:
    """Calling _my_sum with a list containing not just ints fails type check."""
    with pytest.raises(AssertionError):
        _my_sum([1, 2, "hello"])


def test_parameter_int() -> None:
    @check_contracts
    def parameter_int(num: int) -> None:
        return None

    parameter_int(1)


def test_parameter_float() -> None:
    @check_contracts
    def parameter_float(num: float) -> None:
        return None

    parameter_float(1.0)


def test_parameter_bool() -> None:
    @check_contracts
    def parameter_bool(result: bool) -> None:
        return None

    parameter_bool(True)


def test_parameter_int_float_error() -> None:
    @check_contracts
    def parameter_int(num: int) -> None:
        return None

    with pytest.raises(AssertionError):
        parameter_int(1.0)


def test_parameter_float_int_error() -> None:
    @check_contracts
    def parameter_float(num: float) -> None:
        return None

    with pytest.raises(AssertionError):
        parameter_float(1)


def test_parameter_int_bool_error() -> None:
    @check_contracts
    def parameter_int(num: int) -> None:
        return None

    with pytest.raises(AssertionError):
        parameter_int(True)


def test_parameter_bool_int_error() -> None:
    @check_contracts
    def parameter_bool(result: bool) -> None:
        return None

    with pytest.raises(AssertionError):
        parameter_bool(1)


def test_parameter_int_bool_disable_contract_checking(disable_contract_checking) -> None:
    @check_contracts
    def parameter_int(num: int) -> None:
        return None

    parameter_int(True)


@check_contracts
def _my_sum_one_precondition(numbers: List[int]) -> int:
    """Return the sum of a list of numbers.

    Precondition: len(numbers) > 2
    """
    return sum(numbers)


def test_my_sum_one_pre_valid() -> None:
    """Calling _my_sum_one_precondition on a valid input."""
    assert _my_sum_one_precondition([1, 2, 3]) == 6


def test_my_sum_one_wrong_type() -> None:
    """Calling _my_sum_one_precondition on a value of the wrong type."""
    with pytest.raises(AssertionError):
        _my_sum_one_precondition("hi")


def test_my_sum_one_pre_violation() -> None:
    """Calling _my_sum_one_precondition one a value of the right type,
    but that violates the docstring precondition.
    """
    with pytest.raises(AssertionError) as excinfo:
        _my_sum_one_precondition([1])

    msg = str(excinfo.value)
    assert "len(numbers) > 2" in msg


def test_my_sum_one_disable_contract_checking(disable_contract_checking) -> None:
    """Calling _my_sum_one_precondition with a value that violates the precondition but with ENABLE_CONTRACT_CHECKING
    = False so no error is raised"""
    _my_sum_one_precondition([1])


# Checking to see if functions we defined are in-scope for preconditions


def is_even(lst: list[int]) -> bool:
    return all([(not x & 1) for x in lst])


@check_contracts
def _is_even_sum(numbers: List[int]) -> int:
    """Return the sum of a list of numbers.

    Precondition: is_even(numbers)
    """
    return sum(numbers)


def test_is_even_sum_valid() -> None:
    """Calling _is_even_sum on a valid input."""
    assert _is_even_sum([2, 4, 6]) == 12


def test_is_even_sum_violation() -> None:
    """Calling _is_even_sum one a value of the right type,
    but that violates the docstring precondition.
    """
    with pytest.raises(AssertionError) as excinfo:
        _is_even_sum([1, 2])

    msg = str(excinfo.value)
    assert "is_even(numbers)" in msg


@check_contracts
def search(numbers: Set[int]) -> bool:
    """Search for a number in a set.

    Illustrates a preconditions with a double comprehension.

    Preconditions:
        - all({n + m > 0 for n in numbers for m in numbers})
    """
    return 1 in numbers


def test_search_valid() -> None:
    """Test search on a valid input."""
    assert search({1, 2})


def test_search_invalid() -> None:
    """Test search on an invalid input."""
    with pytest.raises(AssertionError) as excinfo:
        search({-1, -2})

    msg = str(excinfo.value)
    assert "all({n + m > 0 for n in numbers for m in numbers})" in msg


class Player:
    user: str


class CPU(Player):
    def __init__(self) -> None:
        self.user = "CPU"


@check_contracts
def _is_cpu(player: Player) -> bool:
    return player.user == "CPU"


def test_class_not_instance_error() -> None:
    """Test that the additional suggestion is added when the class type is passed in as the
    argument instead of its instance

    This test is coupled to the suggestion's arbitrarily chosen text, hence should be updated
    when changing the suggestion text.
    """
    with pytest.raises(AssertionError) as excinfo:
        _is_cpu(Player)

    msg = str(excinfo.value)
    assert "Did you mean Player(...) instead of Player?" in msg


def test_subclass_not_instance_error() -> None:
    """Test that the additional suggestion is added when a subclass type is passed in as an
    argument instead of its instance

    This test is coupled to the suggestion's arbitrarily chosen text, hence should be updated
    when changing the suggestion text.
    """
    with pytest.raises(AssertionError) as excinfo:
        _is_cpu(CPU)

    msg = str(excinfo.value)
    assert "Did you mean CPU(...) instead of CPU?" in msg


def test_no_suggestion_instance_as_instance() -> None:
    """Test that the additional suggestion is not added when an unrelated type is passed in.

    This test is coupled to the suggestion's arbitrarily chosen text, hence should be updated
    when changing the suggestion text.
    """
    with pytest.raises(AssertionError) as excinfo:
        _is_cpu(str)

    msg = str(excinfo.value)

    part1, part2, part3 = "Did you pass in", "instead of", "(...)?"
    assert part1 not in msg
    assert part2 not in msg
    assert part3 not in msg


def test_invalid_typing_generic_argument() -> None:
    """Test that subclass checking on a type parameter that is typing's _GenericAlias does not
    throw an error (as issubclass does not take in a _GenericAlias as its second argument).
    """

    @check_contracts
    def unary(arg: List[str]) -> None:
        return

    with pytest.raises(AssertionError):
        unary(dict)


# Test that postcondition checks regarding function return values pass and fail as expected
@check_contracts
def _get_double_valid(num: int) -> int:
    """
    Return twice the number passed as the argument.

    Postcondition: $return_value == num * 2
    """
    return num * 2


@check_contracts
def _get_double_invalid(num: int) -> int:
    """
    Return a number that is not twice the number passed as the argument.

    Postcondition: $return_value == num * 2
    """
    return (num * 2) + 1


def test_get_double_valid() -> None:
    """Test that calling the valid implementation of _get_double succeeds."""
    assert _get_double_valid(5) == 10


def test_get_double_invalid() -> None:
    """Test that calling the invalid implementation of _get_double raises an AssertionError for failing postcondition
    check.
    """
    with pytest.raises(AssertionError) as excinfo:
        _get_double_invalid(5)

    msg = str(excinfo.value)
    assert "$return_value == num * 2" in msg


def test_get_double_disabled_contract_checking(disable_contract_checking) -> None:
    """Test that calling the invalid implementation of _get_double does NOT raise an AssertionError when
    ENABLE_CONTRACT_CHECKING is False.
    """
    assert _get_double_invalid(5) == 11


# Test that postcondition checks involving function parameters pass and fail as expected
@check_contracts
def _add_to_set_valid(num_set: Set[int], new_num: int) -> None:
    """
    Add a number to the provided set if the number does not already exist in the set.

    Postconditions:
        - new_num in num_set
    """
    if new_num not in num_set:
        num_set.add(new_num)


@check_contracts
def _add_to_set_invalid(num_set: Set[int], new_num: int) -> None:
    """
    Add new_num to the num_set. This is implemented incorrectly to make the postcondition check fail.

    Postconditions:
        - new_num in num_set
    """
    if new_num in num_set:
        num_set.add(new_num)


def test_add_to_set_valid() -> None:
    """Test that there are no errors when correctly adding a number to a set."""
    sample_set = {5, 4}
    _add_to_set_valid(sample_set, 1)
    assert 1 in sample_set


def test_add_to_set_invalid() -> None:
    """Test that the attempt to add a number to a set using _add_to_set_invalid raises an AssertionError."""
    sample_set = {1, 2}

    with pytest.raises(AssertionError) as excinfo:
        _add_to_set_invalid(sample_set, 5)

    msg = str(excinfo.value)
    assert "new_num in num_set" in msg


# Test that postcondition checks that use custom functions in scope pass and fail as expected
@check_contracts
def _get_even_nums_valid(lst: List[int]) -> List[int]:
    """
    Return a list of all even numbers in the input list.

    Postcondition: is_even($return_value)
    """
    return [num for num in lst if num % 2 == 0]


@check_contracts
def _get_even_nums_invalid(lst: List[int]) -> List[int]:
    """
    Return a list of all odd numbers in the input list, which should cause the postcondition check to fail.

    Postcondition: is_even($return_value)
    """
    return [num for num in lst if num % 2 != 0]


def test_get_even_nums_valid() -> None:
    """Test that _get_even_nums_valid correctly retrieves all even numbers in a list."""
    assert is_even(_get_even_nums_valid([4, 3, 2, 5, 6, 8, 1]))


def test_get_even_nums_invalid() -> None:
    """Test that the incorrect implementation of _get_even_nums raises an AssertionError because of the failure of
    the postcondition check.
    """

    with pytest.raises(AssertionError) as excinfo:
        _get_even_nums_invalid([5, 4, 3, 2, 1, 0, 5])

    msg = str(excinfo.value)
    assert "is_even($return_value)" in msg


# Test that a function returning a custom object successfully checks for postconditions
class Rectangle:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height


@check_contracts
def _zero_rectangle_invalid() -> Rectangle:
    """
    Return a rectangle with non-zero width and height.

    Postconditions:
        - $return_value.width == 0
        - $return_value.height == 0
    """
    return Rectangle(5, 6)


@check_contracts
def _zero_rectangle_valid() -> Rectangle:
    """
    Return a rectangle with 0 width and height.

    Postconditions:
        - $return_value.width == 0
        - $return_value.height == 0
    """
    return Rectangle(0, 0)


def test_zero_rectangle_invalid() -> None:
    """Test that an error is raised when calling the incorrect implementation of _zero_rectangle."""

    with pytest.raises(AssertionError) as excinfo:
        _zero_rectangle_invalid()

    msg = str(excinfo.value)
    assert "$return_value.width == 0" in msg


def test_zero_rectangle_valid() -> None:
    """Test that postcondition checks pass for the valid implementation of _zero_rectangle."""
    rect = _zero_rectangle_valid()
    assert rect.width == 0 and rect.height == 0


# Use the legal variable name used to refer to the return value of the function by PyTA as a variable inside
# the function to ensure a new name is generated which does not cause collision.
@check_contracts
def _get_quotient(number: int) -> int:
    """
    Return the quotient obtained on dividing the number by 10.

    Postcondition: $return_value % 10 == 0
    """
    __function_return_value__ = 0

    while number > 0:
        number -= 10
        __function_return_value__ += 1

    return __function_return_value__


def test_get_quotient_valid() -> None:
    """Test that postcondition check passes when _get_quotient returns a multiple of 10."""
    assert _get_quotient(200) % 10 == 0


def test_get_quotient_invalid() -> None:
    """Test that an error is raised when _get_quotient returns a value that is not a multiple of 10."""
    with pytest.raises(AssertionError) as excinfo:
        _get_quotient(120)

    msg = str(excinfo.value)
    assert "$return_value % 10 == 0" in msg


# Test both pre and post conditions in a function
@check_contracts
def _get_quotient_with_pre_and_post(number: int) -> int:
    """
    Perform the same task as _get_quotient but this time ensure the input is a multiple of 100.

    Precondition: number % 100 == 0
    Postcondition: $return_value % 10 == 0
    """
    # Deliberately create a case in which precondition check passes but postcondition check does not
    if number == 400:
        return 4

    return _get_quotient(number)


def test_get_quotient_with_pre_and_post_valid() -> None:
    """Test the quotient on division by 10 is successfully returned for a multiple of 100."""
    assert _get_quotient_with_pre_and_post(500) % 10 == 0


def test_get_quotient_with_pre_and_post_invalid_input() -> None:
    """Test that an AssertionError is raised when a number that is not a multiple of 100 is provided as the input
    to _get_quotient_with_pre_and_post.
    """
    with pytest.raises(AssertionError) as excinfo:
        _get_quotient_with_pre_and_post(150)

    msg = str(excinfo.value)
    assert "number % 100 == 0" in msg


def test_get_quotient_with_pre_and_post_invalid_output() -> None:
    """Test that an AssertionError is raised when a number that is not a multiple of 10 is returned from
    _get_quotient_with_pre_and_post. In this case, the precondition check should pass but postcondition check should
    fail.
    """
    with pytest.raises(AssertionError) as excinfo:
        _get_quotient_with_pre_and_post(400)

    msg = str(excinfo.value)
    assert "$return_value % 10 == 0" in msg


def test_invalid_built_in_generic_argument() -> None:
    """Test that subclass checking on a type parameter that is a GenericAlias does not
    throw an error (as issubclass does not take in a GenericAlias as its second argument).
    """

    @check_contracts
    def unary(arg: list[str]) -> None:
        return

    with pytest.raises(AssertionError):
        unary(dict)


def test_check_all_contracts_module_names_argument() -> None:
    """Test that checks for classes and functions not declared as parameters to check_all_contracts
    are skipped.
    """
    from tests.fixtures.contracts.modules_not_in_arg import run

    with pytest.raises(AssertionError):
        run()


def test_enable_contract_checking_false(disable_contract_checking) -> None:
    """Test that check_contracts does nothing when ENABLE_CONTRACT_CHECKING is False."""

    @check_contracts
    def unary2(arg: int) -> int:
        return arg

    # No error should be raised even though the argument is the wrong type
    assert unary2("wrong type!") == "wrong type!"


def test_invalid_attr_type_disable_contract_checking(disable_contract_checking) -> None:
    """
    Test that a Person object is created with an attribute value that doesn't match the specified type annotation but
    with ENABLE_CONTRACT_CHECKING = False so no error is raised.
    """

    @check_contracts
    class Person:
        age: int

    my_person = Person()
    my_person.age = "John"
    assert my_person.age == "John"


def test_nested_preconditions_contract_checking() -> None:
    """
    Test that an AssertionError is correctly raised when a precondition violation occurs while
    checking the precondition for another function.
    This test is based on the code found at ./test_nested_preconditions_example.py
    """
    with pytest.raises(AssertionError) as exception_info:
        my_function(-1)

    assert (
        str(exception_info.value)
        == 'my_condition2 precondition "x > 0" was violated for arguments {x: -1}'
    )


def test_nested_method_preconditions_contract_checking() -> None:
    """
    Test that an AssertionError is correctly raised when a class method precondition violation
    occurs while checking the precondition for another class method.
    This test is based on the code found at ./test_nested_preconditions_example.py
    """
    student = Student("Bob", 1001001000, 19)

    with pytest.raises(AssertionError) as exception_info:
        student.function(-1.5)

    assert 'condition2 precondition "x > 0" was violated' in str(exception_info.value)


def test_precondition_violation_in_representation_invariant() -> None:
    """
    Test that an AssetionError is correclty raised when a representation invarinat of a class
    contains a call to a function whose precondition is being violated.
    This test is based on the code found at ./test_nested_preconditions_example.py
    """
    with pytest.raises(AssertionError) as exception_info:
        Student("Bob", 1001001000, -19)

    assert 'my_condition2 precondition "x > 0" was violated' in str(exception_info.value)


def test_parameter_int_float_without_strict(disable_strict_numeric_types) -> None:
    """Test that an AssertionError is raised when a function with an integer parameter is called
    using a float argument, while STRICT_NUMERIC_TYPES is disabled.
    """

    @check_contracts
    def parameter_int(num: int) -> None:
        return None

    with pytest.raises(AssertionError):
        parameter_int(1.0)


def test_parameter_float_int_without_strict(disable_strict_numeric_types) -> None:
    """Test that an AssertionError is not raised when a function with a float parameter is called
    using an integer argument, while STRICT_NUMERIC_TYPES is disabled.
    """

    @check_contracts
    def parameter_float(num: float) -> None:
        return None

    parameter_float(1)


def test_parameter_int_bool_without_strict(disable_strict_numeric_types) -> None:
    """Test that an AssertionError is not raised when a function with an integer parameter is called
    using a boolean argument, while STRICT_NUMERIC_TYPES is disabled.
    """

    @check_contracts
    def parameter_int(num: int) -> None:
        return None

    parameter_int(True)


def test_parameter_bool_int_without_strict(disable_strict_numeric_types) -> None:
    """Test that an AssertionError is raised when a function with a boolean parameter is called
    using an integer argument, while STRICT_NUMERIC_TYPES is disabled.
    """

    @check_contracts
    def parameter_bool(result: bool) -> None:
        return None

    with pytest.raises(AssertionError):
        parameter_bool(1)


def test_return_int_float_without_strict(disable_strict_numeric_types) -> None:
    """Test that an AssertionError is raised when a function with an integer return-type,
    returns a float, while STRICT_NUMERIC_TYPES is disabled.
    """

    @check_contracts
    def return_int() -> int:
        return 1.0

    with pytest.raises(AssertionError):
        return_int()


def test_return_float_int_without_strict(disable_strict_numeric_types) -> None:
    """Test that an AssertionError is not raised when a function with a float return-type,
    returns an integer, while STRICT_NUMERIC_TYPES is disabled.
    """

    @check_contracts
    def return_float() -> float:
        return 1

    return_float()


def test_return_int_bool_without_strict(disable_strict_numeric_types) -> None:
    """Test that an AssertionError is not raised when a function with an integer return-type,
    returns a boolean, while STRICT_NUMERIC_TYPES is disabled.
    """

    @check_contracts
    def return_int() -> int:
        return True

    return_int()


def test_return_bool_int_without_strict(disable_strict_numeric_types) -> None:
    """Test that an AssertionError is raised when a function with a boolean return-type,
    returns an integer, while STRICT_NUMERIC_TYPES is disabled.
    """

    @check_contracts
    def return_bool() -> bool:
        return 1

    with pytest.raises(AssertionError):
        return_bool()


def test_parameter_list_float_int() -> None:
    """Testing when the function expects list[float] and it receives list[int]."""

    @check_contracts
    def process_float_list(data: list[float]) -> float:
        return sum(data)

    with pytest.raises(AssertionError):
        process_float_list([1, 2, 3])


def test_parameter_dict_float_int_key() -> None:
    """Testing when the function expects dict[float, int] and it receives dict[int, int] for keys."""

    @check_contracts
    def process_float_key_dict(data: dict[float, int]) -> int:
        return sum(data.values())

    with pytest.raises(AssertionError):
        process_float_key_dict({1: 1, 2: 2})


def test_parameter_dict_float_bool_value() -> None:
    """Testing when the function expects dict[float, int] and it receives dict[float, bool] for values."""

    @check_contracts
    def process_float_key_dict(data: dict[float, int]) -> int:
        return sum(data.values())

    with pytest.raises(AssertionError):
        process_float_key_dict({1.0: True, 2.5: False})


def test_parameter_union_int_bool() -> None:
    """Testing when the function expects Union[int, float] and it receives a bool."""

    @check_contracts
    def accept_union(value: Union[int, float]) -> None:
        pass

    with pytest.raises(AssertionError):
        accept_union(True)


def test_parameter_tuple_int_float_mismatch() -> None:
    """Testing when the function expects tuple[int, float] and it receives tuple[float, int]."""

    @check_contracts
    def accept_tuple(data: tuple[int, float]) -> float:
        return data[0] + data[1]

    with pytest.raises(AssertionError):
        accept_tuple((1.0, 2))


def test_parameter_dict_str_list_float() -> None:
    """Testing when the function expects dict[str, list[int]] and it receives dict[str, list[float]]."""

    @check_contracts
    def process_complex_structure(data: dict[str, list[int]]) -> int:
        return sum(sum(lst) for lst in data.values())

    with pytest.raises(AssertionError):
        process_complex_structure({"a": [1.0, 2.5]})


def test_parameter_dict_int_list_int_key_type() -> None:
    """Testing when the function expects dict[str, list[int]] and it receives dict[int, list[int]] for keys."""

    @check_contracts
    def process_complex_structure(data: dict[str, list[int]]) -> int:
        return sum(sum(lst) for lst in data.values())

    with pytest.raises(AssertionError):
        process_complex_structure({1: [1, 2]})


def test_parameter_list_float_pass() -> None:
    """Testing when the function expects list[float] and it receives list[float]."""

    @check_contracts
    def process_float_list(data: list[float]) -> float:
        return sum(data)

    process_float_list([1.0, 2.5, 3.3])


def test_parameter_dict_float_int_pass() -> None:
    """Testing when the function expects dict[float, int] and it receives dict[float, int]."""

    @check_contracts
    def process_float_key_dict(data: dict[float, int]) -> int:
        return sum(data.values())

    process_float_key_dict({1.0: 10, 2.5: 20})


def test_parameter_union_int_float_pass() -> None:
    """Testing when the function expects Union[int, float] and it receives an int."""

    @check_contracts
    def accept_union(value: Union[int, float]) -> None:
        pass

    accept_union(10)


def test_union_with_dict_or_list() -> None:
    """Test case where the function expects Union[dict[int, str], list[int]] and receives list[int]."""

    @check_contracts
    def process_dict(value: Union[dict[int, str], list[int]]) -> str:
        return str(value)

    process_dict([1, 2, 3])


def test_union_with_tuple_or_list() -> None:
    """Test case where the function expects Union[tuple[int, str], list[int]] and receives list[int]."""

    @check_contracts
    def process_tuple(value: Union[tuple[int, str], list[int]]) -> str:
        return f"{value[0]}, {value[1]}"

    process_tuple([1, 2, 3])


def test_union_with_set_or_list() -> None:
    """Test case where the function expects Union[set[int], list[int]] and receives list[int]."""

    @check_contracts
    def process_set(value: Union[set[int], list[int]]) -> str:
        return str(value)

    process_set([1, 2, 3])


def test_parameter_list_float_int_without_strict(disable_strict_numeric_types) -> None:
    """Test that an AssertionError is not raised when a function expects list[float] but receives list[int],
    while STRICT_NUMERIC_TYPES is disabled.
    """

    @check_contracts
    def process_float_list(data: list[float]) -> float:
        return sum(data)

    process_float_list([1, 2, 3])


def test_parameter_dict_float_int_key_without_strict(disable_strict_numeric_types) -> None:
    """Test that an AssertionError is not raised when a function expects dict[float, int] but receives dict[int, int],
    while STRICT_NUMERIC_TYPES is disabled.
    """

    @check_contracts
    def process_float_key_dict(data: dict[float, int]) -> int:
        return sum(data.values())

    process_float_key_dict({1: 10, 2: 20})


def test_parameter_float_complex() -> None:
    """Testing when the function expects a float but receives a complex number.
    This should raise an AssertionError with strict type checking enabled.
    """

    @check_contracts
    def process_float(value: float) -> float:
        return value.real

    with pytest.raises(AssertionError):
        process_float(3 + 4j)


def test_parameter_float_complex_without_strict(disable_strict_numeric_types) -> None:
    """Test that an AssertionError is not raised when a function expects a float but receives a complex number,
    while STRICT_NUMERIC_TYPES is disabled.
    """

    @check_contracts
    def process_float(value: complex) -> float:
        return value.real

    process_float(3.0)


def test_tuple_fixed_length_correct_types() -> None:
    """Test when a function expects a fixed-length tuple with specific types
    (tuple[int, str]) and receives the correct types."""

    @check_contracts
    def accept_fixed_tuple(value: tuple[int, str]) -> str:
        return f"{value[0]}: {value[1]}"

    accept_fixed_tuple((5, "test"))


def test_tuple_fixed_length_extra_element() -> None:
    """Test when a function expects a fixed-length tuple (tuple[int, str]) but receives an extra element."""

    @check_contracts
    def accept_fixed_tuple(value: tuple[int, str]) -> str:
        return f"{value[0]}: {value[1]}"

    with pytest.raises(AssertionError):
        accept_fixed_tuple((5, "test", 3.5))


def test_tuple_fixed_length_type_mismatch() -> None:
    """Test when a function expects a fixed-length tuple (tuple[int, str]) but receives a type mismatch."""

    @check_contracts
    def accept_fixed_tuple(value: tuple[int, str]) -> str:
        return f"{value[0]}: {value[1]}"

    with pytest.raises(AssertionError):
        accept_fixed_tuple((5, 10))


def test_tuple_homogeneous_any_length() -> None:
    """Test when a function expects a homogeneous tuple of any length (tuple[int, ...])."""

    @check_contracts
    def accept_homogeneous_tuple(value: tuple[int, ...]) -> int:
        return sum(value)

    accept_homogeneous_tuple((1, 2, 3))


def test_tuple_homogeneous_type_mismatch() -> None:
    """Test when a function expects a homogeneous tuple (tuple[int, ...]) but receives a type mismatch."""

    @check_contracts
    def accept_homogeneous_tuple(value: tuple[int, ...]) -> int:
        return sum(value)

    with pytest.raises(AssertionError):
        accept_homogeneous_tuple((1, "two", 3))


def test_tuple_empty() -> None:
    """Test when a function expects an empty tuple (tuple[()]) and receives an empty tuple."""

    @check_contracts
    def accept_empty_tuple(value: tuple[()]) -> str:
        return "Empty tuple accepted"

    accept_empty_tuple(())


def test_tuple_empty_type_mismatch() -> None:
    """Test when a function expects an empty tuple (tuple[()]) but receives a non-empty tuple."""

    @check_contracts
    def accept_empty_tuple(value: tuple[()]) -> str:
        return "Empty tuple accepted"

    with pytest.raises(AssertionError):
        accept_empty_tuple((1,))


def test_tuple_nested_fixed_length_correct_types() -> None:
    """Test when a function expects a nested fixed-length tuple (tuple[int, tuple[str, float]])
    and receives the correct types."""

    @check_contracts
    def process_nested_tuple(value: tuple[int, tuple[str, float]]) -> str:
        return f"Outer: {value[0]}, Inner: {value[1][0]}, {value[1][1]}"

    process_nested_tuple((5, ("hello", 3.14)))


T = TypeVar("T")


class GenericClass(Generic[T]):
    def __init__(self, item: T):
        self.item = item


def test_custom_generic_class_with_parameter() -> None:
    """Test that a function expecting GenericClass[int] accepts a valid instance with an int"""

    @check_contracts
    def process_generic(value: GenericClass[int]) -> int:
        return value.item

    process_generic(GenericClass(10))
