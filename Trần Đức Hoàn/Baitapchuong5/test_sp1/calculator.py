"""Calculator module - basic math operations."""

class Calculator:
    def __init__(self):
        self.history = []

    def add(self, a, b):
        result = a + b
        self.history.append(('add', a, b, result))
        return result

    def subtract(self, a, b):
        result = a - b
        self.history.append(('sub', a, b, result))
        return result

    def multiply(self, a, b):
        result = a * b
        self.history.append(('mul', a, b, result))
        return result

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self.history.append(('div', a, b, result))
        return result

    def get_history(self):
        return self.history

if __name__ == '__main__':
    calc = Calculator()
    print(calc.add(10, 5))
    print(calc.subtract(10, 5))
    print(calc.multiply(3, 4))
    print(calc.divide(10, 2))
    print(calc.get_history())
