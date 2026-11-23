"""
Логика лабораторной работы №4, вариант 17.

Содержит:
- generator_digit_combinations()      — Задание 1 (сочетания из трёх цифр)
- function_values_generator()         — Задание 2 (значения f(x) на [a; b])
- get_sort()                          — Задание 3 (сортировка словаря по ключам)
- generator_digit_combinations_parallel() — параллельная версия задания 1
- benchmark()                         — замер задания 1 (1000 элементов)
- heavy_sequential / heavy_parallel / benchmark_heavy
                                       — Well-done: тяжёлая задача
                                         с реальным ускорением > 1
"""

from __future__ import annotations

import itertools
import math
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Callable, Generator, Iterable, Iterator


# ============================================================
# Задание 1. Сочетания из трёх цифр (целые числа)
# ============================================================
DIGITS = "0123456789"


def generator_digit_combinations(
    digits: str = DIGITS,
) -> Generator[int, None, None]:
    """
    Генерирует все трёхзначные комбинации цифр как целые числа.

    Используется itertools.product — комбинации с повторениями
    (всего len(digits)**3 = 1000 значений для 10 цифр).

    Исключения:
        TypeError  — если digits не строка.
        ValueError — если digits пустая.
    """
    if not isinstance(digits, str):
        raise TypeError("digits должен быть строкой")
    if not digits:
        raise ValueError("Строка digits не должна быть пустой")

    for combo in itertools.product(digits, repeat=3):
        yield int("".join(combo))


# ============================================================
# Задание 2. Значения функции f(x) на [a; b] с шагом 0.01
# ============================================================
def function_values_generator(
    a: float,
    b: float,
    f: Callable[[float], float],
    step: float = 0.01,
) -> Generator[float, None, None]:
    """
    Генерирует значения f(x) для x ∈ [a; b] с шагом step.

    Без использования коллекций: только арифметика и range.

    Исключения:
        TypeError  — если f не callable, a/b не числа.
        ValueError — если step <= 0 или a > b.
    """
    if not callable(f):
        raise TypeError("f должна быть вызываемой (callable)")
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("a и b должны быть числами")
    if step <= 0:
        raise ValueError("step должен быть > 0")
    if a > b:
        raise ValueError("Требуется a <= b")

    # чтобы избежать накопления ошибки float, идём по индексу
    n = int(math.floor((b - a) / step + 1e-9)) + 1
    for i in range(n):
        x = a + i * step
        yield f(x)


# ============================================================
# Задание 3. Сортировка словаря по убыванию ключей
# ============================================================
def get_sort(d: dict) -> list:
    """
    Возвращает список значений словаря, отсортированных
    по убыванию ключей (лексикографически).

    Пример:
        d = {'cat': 'kom', 'horse': 'лошадь', 'tree': 'дерево',
             'dog': 'собака', 'book': 'книга'}
        -> ['дерево', 'лошадь', 'собака', 'kom', 'книга']
    """
    if not isinstance(d, dict):
        raise TypeError("На вход get_sort должен подаваться dict")
    return [d[k] for k in sorted(d.keys(), reverse=True)]


# ============================================================
# Параллельная версия генератора (Задание 1, маленькая задача)
# ============================================================
def _chunk_to_ints(chunk: Iterable[str]) -> list[int]:
    """Вспомогательная функция для ProcessPoolExecutor (picklable)."""
    return [int("".join(c)) for c in chunk]


def generator_digit_combinations_parallel(
    digits: str = DIGITS,
    n_workers: int | None = None,
    chunk_size: int = 100,
) -> Iterator[int]:
    """
    Параллельная версия генератора сочетаний из трёх цифр.

    Комбинации разбиваются на чанки, каждый обрабатывается
    в отдельном процессе. Порядок сохраняется.
    """
    if not isinstance(digits, str):
        raise TypeError("digits должен быть строкой")
    if not digits:
        raise ValueError("Строка digits не должна быть пустой")

    combos = list(itertools.product(digits, repeat=3))
    chunks = [combos[i : i + chunk_size] for i in range(0, len(combos), chunk_size)]

    with ProcessPoolExecutor(max_workers=n_workers) as pool:
        for part in pool.map(_chunk_to_ints, chunks):
            yield from part


# ============================================================
# Бенчмарк задания 1 (1000 элементов)
# ============================================================
def benchmark(digits: str = DIGITS, n_workers: int | None = None) -> dict[str, float]:
    """
    Замеряет время последовательной и параллельной версий
    для 1000 комбинаций. Возвращает dict с временами и speedup.

    На маленькой задаче параллельная версия медленнее из-за
    overhead запуска процессов (spawn на Windows ~300 мс) —
    это ожидаемое поведение.
    """
    results: dict[str, float] = {}

    t0 = time.perf_counter()
    seq = list(generator_digit_combinations(digits))
    results["sequential"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    par = list(generator_digit_combinations_parallel(digits, n_workers=n_workers))
    results["parallel"] = time.perf_counter() - t0

    if seq != par:
        raise RuntimeError("Параллельная версия дала некорректный результат")

    results["speedup"] = results["sequential"] / max(results["parallel"], 1e-12)
    return results


# ============================================================
# Well-done (вариант A): тяжёлая задача с реальным speedup > 1
# ============================================================
HEAVY_DIGITS = "0123456789"   # только цифры (безопасно для int)
HEAVY_REPEAT = 5              # 10^5 = 100 000 комбинаций
HEAVY_WORK = 200              # 200 итераций над каждой → ~20 млн операций


def _heavy_compute(n: int, work: int) -> int:
    """Тяжёлое вычисление над одним числом."""
    s = 0
    for k in range(work):
        s += (n + k) ** 2 % 9973
    return s


def heavy_sequential(
    digits: str = HEAVY_DIGITS,
    repeat: int = HEAVY_REPEAT,
    work: int = HEAVY_WORK,
) -> list[int]:
    """Тяжёлая последовательная версия (эталон для бенчмарка)."""
    if not digits:
        raise ValueError("digits не должен быть пустым")
    if repeat <= 0:
        raise ValueError("repeat должен быть > 0")
    if work <= 0:
        raise ValueError("work должен быть > 0")

    out: list[int] = []
    for combo in itertools.product(digits, repeat=repeat):
        n = int("".join(combo))
        out.append(_heavy_compute(n, work))
    return out


def _heavy_chunk_worker(args: tuple[list[tuple[str, ...]], int]) -> list[int]:
    """Worker для ProcessPoolExecutor (picklable, на верхнем уровне)."""
    chunk, work = args
    out: list[int] = []
    for combo in chunk:
        n = int("".join(combo))
        out.append(_heavy_compute(n, work))
    return out


def heavy_parallel(
    digits: str = HEAVY_DIGITS,
    repeat: int = HEAVY_REPEAT,
    work: int = HEAVY_WORK,
    n_workers: int | None = None,
    chunk_size: int = 2000,
) -> Iterator[int]:
    """Тяжёлая параллельная версия с реальным ускорением."""
    if not digits:
        raise ValueError("digits не должен быть пустым")
    if repeat <= 0:
        raise ValueError("repeat должен быть > 0")
    if work <= 0:
        raise ValueError("work должен быть > 0")

    combos = list(itertools.product(digits, repeat=repeat))
    chunks = [combos[i : i + chunk_size] for i in range(0, len(combos), chunk_size)]
    args = [(chunk, work) for chunk in chunks]

    with ProcessPoolExecutor(max_workers=n_workers) as pool:
        for part in pool.map(_heavy_chunk_worker, args):
            yield from part


def benchmark_heavy(
    digits: str = HEAVY_DIGITS,
    repeat: int = HEAVY_REPEAT,
    work: int = HEAVY_WORK,
    n_workers: int | None = None,
) -> dict[str, float]:
    """
    Бенчмарк тяжёлой задачи (Well-done). Даёт speedup > 1
    на многоядерном CPU, где spawn-overhead окупается объёмом работы.
    """
    t0 = time.perf_counter()
    seq = heavy_sequential(digits, repeat, work)
    t_seq = time.perf_counter() - t0

    t0 = time.perf_counter()
    par = list(heavy_parallel(digits, repeat, work, n_workers=n_workers))
    t_par = time.perf_counter() - t0

    if seq != par:
        raise RuntimeError("parallel != sequential")

    return {
        "n_items": float(len(seq)),
        "sequential": t_seq,
        "parallel": t_par,
        "speedup": t_seq / max(t_par, 1e-12),
    }


# ============================================================
# Демонстрация заданий
# ============================================================
def demo() -> None:
    """Печатает результаты выполнения трёх заданий варианта 17."""
    print("=== Задание 1: сочетания из трёх цифр ===")
    gen1 = generator_digit_combinations()
    for _ in range(50):
        print(next(gen1), end=" ")
    print("\n")

    print("=== Задание 2: значения f(x) = -1.5x + 2 на [-20; 100] ===")
    gen2 = function_values_generator(-20, 100, lambda x: -1.5 * x + 2)
    for _ in range(20):
        print(round(next(gen2), 4), end=" ")
    print("\n")

    print("=== Задание 3: сортировка словаря ===")
    d = {
        "cat": "kom",
        "horse": "лошадь",
        "tree": "дерево",
        "dog": "собака",
        "book": "книга",
    }
    print(get_sort(d))


if __name__ == "__main__":
    demo()