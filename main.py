import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

transformations = standard_transformations + (implicit_multiplication_application,)


def calculate(raw_input: str) -> str:
    raw_input = raw_input.strip()
    if not raw_input:
        return "Введите выражение или уравнение."

    try:
        text = raw_input.lower()
        command = "auto"
        expr_str = raw_input

        commands_map = {
            "/resh ": "solve",
            "реши ": "solve",
            "/raz ": "factor",
            "разложи ": "factor",
            "/yprost ": "simplify",
            "упрости ": "simplify",
            "раскрой ": "expand",
        }

        for prefix, action in commands_map.items():
            if text.startswith(prefix):
                command = action
                expr_str = raw_input[len(prefix) :]
                break

        expr_str = expr_str.replace("^", "**").replace(",", ".").replace(":", "/")

        if "=" in expr_str:
            left_str, right_str = expr_str.split("=", 1)
            left = parse_expr(left_str, transformations=transformations, evaluate=False)
            right = parse_expr(right_str, transformations=transformations, evaluate=False)

            symbols = list((left - right).free_symbols)
            if not symbols:
                return f"Ответ: {sp.simplify(left) == sp.simplify(right)}"
            solutions = sp.solve(sp.Eq(left, right), symbols)
            return f"Ответ ({symbols}): {solutions}"
        else:
            expr = parse_expr(expr_str, transformations=transformations, evaluate=False)

            if command == "factor":
                result = sp.factor(expr)
            elif command == "expand":
                result = sp.expand(expr)
            elif command == "solve":
                symbols = list(expr.free_symbols)
                result = sp.solve(expr, symbols) if symbols else sp.simplify(expr)
            else:
                result = sp.simplify(sp.expand(expr))

            return f"Ответ: {result}"

    except Exception as e:
        return f"Ошибка в примере:\n{e}"


class CalculatorApp(App):
    def build(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=12)

        hint_text = (
            "[b]Доступные команды:[/b]\n"
            "• [b]/resh[/b] (или [b]реши[/b]) — решить уравнение\n"
            "• [b]/raz[/b] (или [b]разложи[/b]) — разложить на множители\n"
            "• [b]/yprost[/b] (или [b]упрости[/b]) — упростить выражение\n"
            "• [b]раскрой[/b] — раскрыть скобки\n"
            "Или просто введите пример без команды:"
        )

        hint = Label(
            text=hint_text,
            markup=True,
            size_hint=(1, 0.35),
            halign="left",
            valign="middle",
        )
        # Автоматический перенос строк по ширине экрана телефона
        hint.bind(size=lambda instance, value: setattr(instance, "text_size", (value[0], None)))

        self.input_box = TextInput(
            hint_text="Например: реши x^2 - 4 = 0",
            multiline=False,
            font_size=22,
            size_hint=(1, 0.15),
        )
        btn = Button(
            text="Посчитать",
            font_size=24,
            size_hint=(1, 0.15),
            on_press=self.on_calculate,
        )
        self.output_label = Label(
            text="Здесь появится ответ",
            font_size=22,
            size_hint=(1, 0.35),
            halign="center",
            valign="middle",
        )
        self.output_label.bind(
            size=lambda instance, value: setattr(instance, "text_size", (value[0], None))
        )

        layout.add_widget(hint)
        layout.add_widget(self.input_box)
        layout.add_widget(btn)
        layout.add_widget(self.output_label)
        return layout

    def on_calculate(self, instance):
        self.output_label.text = calculate(self.input_box.text)


if __name__ == "__main__":
    CalculatorApp().run()
