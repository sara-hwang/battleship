class Input:
    def __init__(self, max_length=0) -> None:
        self._value = ""
        self.max_length = max_length

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, new_value: str) -> None:
        self._value = new_value

    def backspace(self) -> str:
        self._value = self._value[:-1]
        return self._value

    def input(self, value: str) -> str:
        if self.max_length != 0 and len(self.value) >= self.max_length:
            return self._value
        self._value += value
        return self._value
