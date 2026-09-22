import random
import re
from typing import Callable

from math_trainer.database_manager import DatabaseManager
from math_trainer.models import Question

OPERATION_TYPES = ("add", "sub", "mul", "div")
REINFORCEMENT_PROBABILITY = 0.30

LEVEL_CONFIG = {
    1: {
        "operations": OPERATION_TYPES,
        "add_range": (1, 99),
        "sub_range": (1, 99),
        "mul_range": (1, 5),
        "div_range": (1, 5),
        "add_filter": lambda a, b: (a % 10) + (b % 10) < 10,
        "sub_filter": lambda a, b: a >= b and (a % 10) >= (b % 10),
    },
    2: {
        "operations": OPERATION_TYPES,
        "add_range": (1, 99),
        "sub_range": (1, 99),
        "mul_range": (6, 8),
        "div_range": (6, 8),
        "add_filter": lambda a, b: (a % 10) + (b % 10) >= 10,
        "sub_filter": lambda a, b: a >= b and (a % 10) < (b % 10),
    },
    3: {
        "operations": OPERATION_TYPES,
        "add_range": (10, 99),
        "sub_range": (10, 99),
        "mul_range": (9, 10),
        "div_range": (9, 10),
        "add_filter": lambda a, b: True,
        "sub_filter": lambda a, b: a >= b,
    },
}


class QuestionGenerator:
    def __init__(self, db_manager: DatabaseManager, level: int = 1) -> None:
        if level not in LEVEL_CONFIG:
            raise ValueError(f"Nivel invalido: {level}. Debe ser 1, 2 o 3.")
        self.db = db_manager
        self.level = level

    def set_level(self, level: int) -> None:
        if level not in LEVEL_CONFIG:
            raise ValueError(f"Nivel invalido: {level}. Debe ser 1, 2 o 3.")
        self.level = level

    def generate(self) -> Question:
        candidates = self.db.get_reinforcement_candidates()
        if candidates and random.random() < REINFORCEMENT_PROBABILITY:
            return self._from_reinforcement(random.choice(candidates))

        config = LEVEL_CONFIG[self.level]
        operation = random.choice(config["operations"])
        generators = {
            "add": lambda: self._generate_addition(config),
            "sub": lambda: self._generate_subtraction(config),
            "mul": lambda: self._generate_multiplication(config),
            "div": lambda: self._generate_division(config),
        }
        return generators[operation]()

    def _from_reinforcement(self, question_text: str) -> Question:
        parsed = self._parse_question_text(question_text)
        if parsed is not None:
            return parsed

        config = LEVEL_CONFIG[self.level]
        return self.generate_from_operation(random.choice(config["operations"]))

    def generate_from_operation(self, operation: str) -> Question:
        config = LEVEL_CONFIG[self.level]
        generators: dict[str, Callable[[], Question]] = {
            "add": lambda: self._generate_addition(config),
            "sub": lambda: self._generate_subtraction(config),
            "mul": lambda: self._generate_multiplication(config),
            "div": lambda: self._generate_division(config),
        }
        if operation not in generators:
            raise ValueError(f"Operacion invalida: {operation}")
        return generators[operation]()

    def _generate_addition(self, config: dict) -> Question:
        low, high = config["add_range"]
        add_filter: Callable[[int, int], bool] = config["add_filter"]

        for _ in range(100):
            a = random.randint(low, high)
            b = random.randint(low, high)
            if add_filter(a, b):
                return Question(
                    operation_type="add",
                    question_text=f"{a} + {b} = ?",
                    correct_answer=a + b,
                    operand_a=a,
                    operand_b=b,
                )

        raise RuntimeError("No se pudo generar una suma valida para el nivel actual.")

    def _generate_subtraction(self, config: dict) -> Question:
        low, high = config["sub_range"]
        sub_filter: Callable[[int, int], bool] = config["sub_filter"]

        for _ in range(100):
            a = random.randint(low, high)
            b = random.randint(low, high)
            if sub_filter(a, b):
                return Question(
                    operation_type="sub",
                    question_text=f"{a} - {b} = ?",
                    correct_answer=a - b,
                    operand_a=a,
                    operand_b=b,
                )

        raise RuntimeError("No se pudo generar una resta valida para el nivel actual.")

    def _generate_multiplication(self, config: dict) -> Question:
        low, high = config["mul_range"]
        a = random.randint(low, high)
        b = random.randint(low, high)
        return Question(
            operation_type="mul",
            question_text=f"{a} × {b} = ?",
            correct_answer=a * b,
            operand_a=a,
            operand_b=b,
        )

    def _generate_division(self, config: dict) -> Question:
        low, high = config["div_range"]
        a = random.randint(low, high)
        b = random.randint(low, high)
        product = a * b
        return Question(
            operation_type="div",
            question_text=f"{product} ÷ {a} = ?",
            correct_answer=b,
            operand_a=product,
            operand_b=a,
        )

    @staticmethod
    def _parse_question_text(question_text: str) -> Question | None:
        add_match = re.fullmatch(r"(\d+) \+ (\d+) = \?", question_text)
        if add_match:
            a, b = int(add_match.group(1)), int(add_match.group(2))
            return Question("add", question_text, a + b, a, b)

        sub_match = re.fullmatch(r"(\d+) - (\d+) = \?", question_text)
        if sub_match:
            a, b = int(sub_match.group(1)), int(sub_match.group(2))
            return Question("sub", question_text, a - b, a, b)

        mul_match = re.fullmatch(r"(\d+) × (\d+) = \?", question_text)
        if mul_match:
            a, b = int(mul_match.group(1)), int(mul_match.group(2))
            return Question("mul", question_text, a * b, a, b)

        div_match = re.fullmatch(r"(\d+) ÷ (\d+) = \?", question_text)
        if div_match:
            product, divisor = int(div_match.group(1)), int(div_match.group(2))
            if divisor == 0 or product % divisor != 0:
                return None
            return Question("div", question_text, product // divisor, product, divisor)

        return None
