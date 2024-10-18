from typing import Any, Callable, Dict, Type

class Registry:
    def __init__(self, name: str) -> None:
        """
        Инициализация реестра с заданным именем.
        """
        self.name: str = name
        self._module_dict: Dict[str, Type[Any]] = {}
        self._instance_dict: Dict[str, Any] = {}

    def __repr__(self) -> str:
        """
        Возвращает строковое представление реестра.
        """
        return f"Registry({self.name}, {list(self._module_dict.keys())})"

    def register_module(self, module: Type[Any] = None) -> Callable[[Type[Any]], None]:
        """
        Декоратор для регистрации модуля (класса или функции) в реестре.
        Если модуль не передан, возвращается декоратор.
        """
        if module is None:
            return self._register
        self._register(module)

    def _register(self, module: Type[Any]) -> None:
        """
        Внутренний метод для регистрации модуля.
        """
        module_name: str = module.__name__
        if module_name in self._module_dict:
            raise KeyError(f"{module_name} уже зарегистрирован в реестре {self.name}.")
        self._module_dict[module_name] = module

    def get(self, module_name: str) -> Type[Any]:
        """
        Получение зарегистрированного модуля по его имени.
        """
        if module_name not in self._module_dict:
            raise KeyError(f"{module_name} не найден в реестре {self.name}.")
        return self._module_dict[module_name]

    def build(self, cfg: Dict[str, Any] = None, singleton: bool = True) -> Any:
        """
        Создание или получение экземпляра класса на основе конфигурации.
        Если singleton=True, класс создаётся только один раз (синглтон).
        Конфигурация должна содержать поле 'type', указывающее на имя класса при первом создании.
        """

        if cfg is None:
            if not self._instance_dict:
                raise ValueError("Объект не создан. Необходимо передать конфигурацию при первом вызове.")
            return next(iter(self._instance_dict.values()))

        if not isinstance(cfg, dict):
            raise TypeError(f"Конфигурация должна быть словарем, но получили {type(cfg)}")
        if 'type' not in cfg:
            raise KeyError("'type' должно быть указано в конфигурации")

        module_name: str = cfg.pop('type')
        module_class: Type[Any] = self.get(module_name)

        if singleton:
            if module_name not in self._instance_dict:
                self._instance_dict[module_name] = module_class(**cfg)
            return self._instance_dict[module_name]

        return module_class(**cfg)

DB_REGISTRY = Registry('db')
EMBEDDING_REGISTRY = Registry('embedder')
GENERATIVE_MODEL_REGISTRY = Registry('generative')
