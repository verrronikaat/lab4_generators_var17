"""
Pytest-тесты для логики ЛР4, вариант 17.
"""

import pytest

from app.generators import (
    DIGITS,
    function_values_generator,
    generator_digit_combinations,
    generator_digit_combinations_parallel,
    get_sort,
)


# ==================== Задание 1 ====================
def test_digit_combinations_count():
    """10 цифр, сочетания по 3 с повторениями -> 1000 значений."""
    result = list(generator_digit_combinations())
    assert len(result) == 1000
    assert all(isinstance(x, int) for x in result)


def test_digit_combinations_first_five():
    gen = generator_digit_combinations()
    first_five = [next(gen) for _ in range(5)]
    assert first_five == [0, 1, 2, 3, 4]


def test_digit_combinations_empty_digits():
    with pytest.raises(ValueError):
        list(generator_digit_combinations(""))


def test_digit_combinations_wrong_type():
    with pytest.raises(TypeError):
        list(generator_digit_combinations(123))


def test_digit_combinations_parallel_matches_sequential():
    seq = list(generator_digit_combinations())
    par = list(generator_digit_combinations_parallel(n_workers=2))
    assert seq == par


# ==================== Задание 2 ====================
def test_function_values_generator_count():
    gen = function_values_generator(-20, 100, lambda x: -1.5 * x + 2)
    values = list(gen)
    # 120 / 0.01 + 1 = 12001 точка
    assert len(values) == 12001


def test_function_values_generator_first_values():
    gen = function_values_generator(-20, 100, lambda x: -1.5 * x + 2)
    first = [next(gen) for _ in range(3)]
    assert first[0] == pytest.approx(32.0)
    assert first[1] == pytest.approx(31.985)
    assert first[2] == pytest.approx(31.97)


def test_function_values_generator_invalid_step():
    with pytest.raises(ValueError):
        list(function_values_generator(-20, 100, lambda x: x, step=0))


def test_function_values_generator_a_greater_b():
    with pytest.raises(ValueError):
        list(function_values_generator(100, -20, lambda x: x))


def test_function_values_generator_not_callable():
    with pytest.raises(TypeError):
        list(function_values_generator(-20, 100, "not a function"))


def test_function_values_generator_wrong_type_a():
    with pytest.raises(TypeError):
        list(function_values_generator("a", 100, lambda x: x))


# ==================== Задание 3 ====================
def test_get_sort_example():
    d = {
        "cat": "kom",
        "horse": "лошадь",
        "tree": "дерево",
        "dog": "собака",
        "book": "книга",
    }
    assert get_sort(d) == ["дерево", "лошадь", "собака", "kom", "книга"]


def test_get_sort_empty():
    assert get_sort({}) == []


def test_get_sort_single():
    assert get_sort({"a": "A"}) == ["A"]


def test_get_sort_wrong_type():
    with pytest.raises(TypeError):
        get_sort(["not", "a", "dict"])