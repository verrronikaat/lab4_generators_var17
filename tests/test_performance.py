"""
Тесты производительности (Well-done).

- test_parallel_matches_sequential — корректность параллельной версии задания 1
- test_benchmark_reports — информационный замер задания 1 (не падает)
- test_parallel_speedup_on_heavy_task — реальное ускорение на тяжёлой задаче
"""

import pytest

from app.generators import (
    benchmark,
    benchmark_heavy,
    generator_digit_combinations,
    generator_digit_combinations_parallel,
)


def test_parallel_matches_sequential():
    """Параллельная версия обязана выдавать тот же результат."""
    seq = list(generator_digit_combinations())
    par = list(generator_digit_combinations_parallel(n_workers=2))
    assert seq == par


@pytest.mark.slow
def test_benchmark_reports(capsys):
    """
    Информационный замер (1000 комбинаций).
    На маленькой задаче параллельная версия медленнее из-за overhead
    запуска процессов (spawn на Windows ~300 мс) — это ожидаемо.
    """
    results = benchmark()
    with capsys.disabled():
        print("\n=== Benchmark (1000 комбинаций) ===")
        for k, v in results.items():
            print(f"{k}: {v:.6f}")
    assert "speedup" in results


@pytest.mark.slow
def test_parallel_speedup_on_heavy_task(capsys):
    """
    Well-done: реальное ускорение на тяжёлой задаче.
    Требуется speedup > 1.1 (мягкий порог для разных CPU).
    """
    results = benchmark_heavy()
    with capsys.disabled():
        print("\n=== Heavy benchmark (Well-done) ===")
        print(f"n_items:    {int(results['n_items'])}")
        print(f"sequential: {results['sequential']:.4f}s")
        print(f"parallel:   {results['parallel']:.4f}s")
        print(f"speedup:    {results['speedup']:.2f}x")

    assert results["speedup"] > 1.1, (
        f"Ожидался speedup > 1.1, получено {results['speedup']:.2f}x. "
        "Увеличьте work или repeat в app/generators.py."
    )