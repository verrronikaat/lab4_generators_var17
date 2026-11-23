"""
GUI на PySide6 для ЛР4, вариант 17.

Возможности:
- Три вкладки (QTabWidget) — по одной на задание.
- Тёмная тема, аккуратные отступы, моноширинный шрифт для вывода.
- Справка пользователя: меню «Справка» → «Руководство пользователя» (F1),
  а также кнопка «?» в правом верхнем углу каждой вкладки.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.generators import (
    DIGITS,
    function_values_generator,
    generator_digit_combinations,
    get_sort,
)

# ============================================================
# Справка пользователя
# ============================================================
HELP_HTML = """
<h2>Лабораторная работа №4 — Вариант 17</h2>
<p><b>Функции-генераторы и встроенные функции Python</b></p>

<h3>Вкладка 1. Сочетания из трёх цифр</h3>
<p>Генерирует все трёхзначные комбинации цифр из заданной строки
(по умолчанию <code>0123456789</code>) и выводит первые N значений
как целые числа. По умолчанию N = 50.</p>

<h3>Вкладка 2. Значения f(x)</h3>
<p>Генерирует значения функции <code>f(x) = -1.5x + 2</code> на отрезке
<code>[a; b]</code> с шагом 0.01. Выводит первые N значений.
Параметры <code>a</code> и <code>b</code> задаются в полях.</p>

<h3>Вкладка 3. get_sort</h3>
<p>Принимает словарь, заданный построчно в виде <code>ключ: значение</code>,
сортирует по убыванию ключей (лексикографически) и возвращает список значений.</p>

<h3>Горячие клавиши</h3>
<ul>
    <li><b>F1</b> — эта справка.</li>
    <li><b>Ctrl+Q</b> — выход.</li>
</ul>

<h3>Обработка ошибок</h3>
<p>Все исключения перехватываются и показываются в диалоговом окне
с понятным сообщением.</p>
"""


# ============================================================
# Главное окно
# ============================================================
class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Лабораторная работа №4 — Вариант 17")
        self.resize(900, 650)
        self.setMinimumSize(700, 500)

        self._build_menu()

        self.tabs = QTabWidget()
        self.tabs.addTab(self._tab_task1(), "Задание 1: сочетания")
        self.tabs.addTab(self._tab_task2(), "Задание 2: f(x)")
        self.tabs.addTab(self._tab_task3(), "Задание 3: get_sort")
        self.setCentralWidget(self.tabs)

        self._build_statusbar()
        self._apply_theme()

    # ============================================================
    # Меню
    # ============================================================
    def _build_menu(self) -> None:
        menubar = self.menuBar()

        help_menu = menubar.addMenu("&Справка")
        help_action = QAction("Руководство пользователя", self)
        help_action.setShortcut(QKeySequence("F1"))
        help_action.triggered.connect(self._show_help)
        help_menu.addAction(help_action)

        help_menu.addSeparator()

        about_action = QAction("О программе", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        help_menu.addSeparator()

        quit_action = QAction("Выход", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(self.close)
        help_menu.addAction(quit_action)

    def _show_help(self) -> None:
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Справка")
        dlg.setTextFormat(Qt.RichText)
        dlg.setText(HELP_HTML)
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.exec()

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "О программе",
            "<h3>ЛР4 — Вариант 17</h3>"
            "<p>Генераторы, map/filter/zip, параллельная версия.</p>"
            "<p>PySide6 • Python 3.13</p>",
        )

    # ============================================================
    # Статусбар
    # ============================================================
    def _build_statusbar(self) -> None:
        sb = QStatusBar()
        self.setStatusBar(sb)
        sb.showMessage("Готово. F1 — справка.")

    # ============================================================
    # Тема
    # ============================================================
    def _apply_theme(self) -> None:
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1f2b;
                color: #e6e6e6;
                font-size: 14px;
            }
            QTabWidget::pane {
                border: 1px solid #3b3f54;
                border-radius: 6px;
                background: #252735;
                padding: 8px;
            }
            QTabBar::tab {
                background: #2c2f42;
                color: #cfd2e0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: #3a3f5c;
                color: #ffffff;
            }
            QTabBar::tab:hover:!selected {
                background: #333752;
            }
            QPushButton {
                background: #4a6cf7;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover { background: #5b7cff; }
            QPushButton:pressed { background: #3b58d1; }
            QLineEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {
                background: #14151e;
                color: #e6e6e6;
                border: 1px solid #3b3f54;
                border-radius: 4px;
                padding: 4px 6px;
                selection-background-color: #4a6cf7;
            }
            QPlainTextEdit {
                font-family: "Consolas", "Courier New", monospace;
            }
            QLabel { color: #cfd2e0; }
            QMenuBar { background: #1e1f2b; }
            QMenuBar::item:selected { background: #2c2f42; }
            QMenu { background: #252735; color: #e6e6e6; }
            QMenu::item:selected { background: #3a3f5c; }
            QStatusBar { background: #191a24; color: #a9adc1; }
            QMessageBox { background: #252735; }
        """)

    # ============================================================
    # Хелпер для кнопки "?" на вкладке
    # ============================================================
    def _make_help_button(self) -> QPushButton:
        btn = QPushButton("?")
        btn.setFixedSize(32, 32)
        btn.setToolTip("Справка (F1)")
        btn.setStyleSheet(
            "QPushButton { background:#4a6cf7; border-radius:16px; font-weight:700; }"
            "QPushButton:hover { background:#5b7cff; }"
        )
        btn.clicked.connect(self._show_help)
        return btn

    # ============================================================
    # Вкладка 1
    # ============================================================
    def _tab_task1(self) -> QWidget:
        w = QWidget()
        outer = QVBoxLayout(w)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("<b>Сочетания из трёх цифр</b>")
        title.setStyleSheet("font-size: 16px;")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self._make_help_button())
        outer.addLayout(header)

        outer.addWidget(QLabel("Строка цифр:"))
        self.task1_digits = QLineEdit(DIGITS)
        outer.addWidget(self.task1_digits)

        row = QHBoxLayout()
        row.addWidget(QLabel("Сколько первых значений:"))
        self.task1_count = QSpinBox()
        self.task1_count.setRange(1, 1000)
        self.task1_count.setValue(50)
        row.addWidget(self.task1_count)
        row.addStretch()
        outer.addLayout(row)

        btn = QPushButton("Сгенерировать")
        btn.clicked.connect(self._run_task1)
        outer.addWidget(btn)

        self.task1_output = QPlainTextEdit()
        self.task1_output.setReadOnly(True)
        self.task1_output.setMinimumHeight(200)
        outer.addWidget(self.task1_output, 1)

        return w

    def _run_task1(self) -> None:
        try:
            digits = self.task1_digits.text()
            count = self.task1_count.value()

            gen = generator_digit_combinations(digits)
            values = []
            for _ in range(count):
                try:
                    values.append(next(gen))
                except StopIteration:
                    break

            self.task1_output.setPlainText(" ".join(map(str, values)))
            self.statusBar().showMessage(
                f"Задание 1: выведено {len(values)} значений", 4000
            )
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    # ============================================================
    # Вкладка 2
    # ============================================================
    def _tab_task2(self) -> QWidget:
        w = QWidget()
        outer = QVBoxLayout(w)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("<b>Значения f(x) = -1.5x + 2</b>")
        title.setStyleSheet("font-size: 16px;")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self._make_help_button())
        outer.addLayout(header)

        row_ab = QHBoxLayout()
        row_ab.addWidget(QLabel("a ="))
        self.task2_a = QDoubleSpinBox()
        self.task2_a.setRange(-1e6, 1e6)
        self.task2_a.setDecimals(2)
        self.task2_a.setValue(-20.0)
        row_ab.addWidget(self.task2_a)

        row_ab.addWidget(QLabel("b ="))
        self.task2_b = QDoubleSpinBox()
        self.task2_b.setRange(-1e6, 1e6)
        self.task2_b.setDecimals(2)
        self.task2_b.setValue(100.0)
        row_ab.addWidget(self.task2_b)

        row_ab.addWidget(QLabel("шаг = 0.01"))
        row_ab.addStretch()
        outer.addLayout(row_ab)

        row_n = QHBoxLayout()
        row_n.addWidget(QLabel("Сколько первых значений:"))
        self.task2_count = QSpinBox()
        self.task2_count.setRange(1, 12001)
        self.task2_count.setValue(20)
        row_n.addWidget(self.task2_count)
        row_n.addStretch()
        outer.addLayout(row_n)

        btn = QPushButton("Сгенерировать f(x)")
        btn.clicked.connect(self._run_task2)
        outer.addWidget(btn)

        self.task2_output = QPlainTextEdit()
        self.task2_output.setReadOnly(True)
        self.task2_output.setMinimumHeight(200)
        outer.addWidget(self.task2_output, 1)

        return w

    def _run_task2(self) -> None:
        try:
            a = self.task2_a.value()
            b = self.task2_b.value()
            count = self.task2_count.value()

            gen = function_values_generator(a, b, lambda x: -1.5 * x + 2)
            values = []
            for _ in range(count):
                try:
                    values.append(round(next(gen), 4))
                except StopIteration:
                    break

            self.task2_output.setPlainText(" ".join(str(v) for v in values))
            self.statusBar().showMessage(
                f"Задание 2: выведено {len(values)} значений", 4000
            )
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    # ============================================================
    # Вкладка 3
    # ============================================================
    def _tab_task3(self) -> QWidget:
        w = QWidget()
        outer = QVBoxLayout(w)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("<b>Сортировка словаря по убыванию ключей</b>")
        title.setStyleSheet("font-size: 16px;")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self._make_help_button())
        outer.addLayout(header)

        outer.addWidget(QLabel("Словарь (ключ: значение, по одной паре на строку):"))
        self.task3_input = QPlainTextEdit()
        self.task3_input.setPlainText(
            "cat: kom\n"
            "horse: лошадь\n"
            "tree: дерево\n"
            "dog: собака\n"
            "book: книга"
        )
        self.task3_input.setMinimumHeight(140)
        outer.addWidget(self.task3_input, 1)

        btn = QPushButton("Отсортировать")
        btn.clicked.connect(self._run_task3)
        outer.addWidget(btn)

        outer.addWidget(QLabel("Результат:"))
        self.task3_output = QPlainTextEdit()
        self.task3_output.setReadOnly(True)
        self.task3_output.setMinimumHeight(80)
        outer.addWidget(self.task3_output, 1)

        return w

    def _run_task3(self) -> None:
        try:
            raw = self.task3_input.toPlainText()
            d: dict[str, str] = {}
            for line in raw.splitlines():
                line = line.strip()
                if not line:
                    continue
                if ":" not in line:
                    raise ValueError(f"Строка без ':' -> {line!r}")
                k, v = line.split(":", 1)
                d[k.strip()] = v.strip()

            result = get_sort(d)
            self.task3_output.setPlainText(repr(result))
            self.statusBar().showMessage(
                f"Задание 3: отсортировано {len(result)} элементов", 4000
            )
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


def run() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()