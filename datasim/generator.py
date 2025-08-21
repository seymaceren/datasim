from typing import Any, Dict, Final, Optional, Tuple, Type
from typing_extensions import Literal
from git import List
import numpy as np

from .types import Number, Value


class Sampler:
    property: str

    def __init__(
        self,
        property: str,
        min: float | None = None,
        max: float | None = None,
        scale: float = 1.0,
    ):
        self.property = property
        self.min = min
        self.max = max
        self.scale = scale
        self.first = True

    @staticmethod
    def _from_yaml(property: str, params: Dict) -> "Sampler":
        if isinstance(params, Value):
            return StaticSampler(property, params, start=params)
        elif isinstance(params, Dict):
            if "value" in params:
                return StaticSampler(
                    property,
                    params["value"],
                    params.get("sample", "independent") == "accumulate",
                    params.get("start", None),
                    params.get("min", None),
                    params.get("max", None),
                    params.get("scale", 1.0),
                )

            if "distribution" in params:
                return DistributionSampler(
                    property,
                    params["distribution"],
                    params.get("parameters", {}),
                    params.get("sample", "independent"),
                    params.get("start", None),
                    params.get("min", None),
                    params.get("max", None),
                    params.get("scale", 1.0),
                )

            return StaticSampler(property, None)

    def next(self) -> Value:
        return None


class StaticSampler(Sampler):
    value: Value
    accumulate: bool
    step: Value

    def __init__(
        self,
        property: str,
        value: Value,
        accumulate: bool = False,
        start: Value = None,
        min: float | None = None,
        max: float | None = None,
        scale: float = 1.0,
    ):
        super().__init__(property, min, max, scale)
        self.accumulate = accumulate
        self.value = start if start else 0.0 if isinstance(value, float) else 0
        self.step = value

    def next(self) -> Value:
        if self.first:
            self.first = False
        else:
            if (
                self.accumulate
                and isinstance(self.value, int | float)
                and isinstance(self.step, int | float)
            ):
                self.value += self.step
        return (
            self.value if not isinstance(self.value, float) else self.scale * self.value
        )


class DistributionSampler(Sampler):
    value: float
    accumulate: bool
    rng: np.random.Generator
    np_function: Any
    parameters: Dict

    def __init__(
        self,
        property: str,
        np_generator: str,
        parameters: Dict,
        accumulation: Literal["independent", "accumulate"],
        start: Optional[float] = None,
        min: float | None = None,
        max: float | None = None,
        scale=1.0,
    ):
        super().__init__(property, min, max, scale)
        self.accumulate = accumulation == "accumulate"
        self.rng = np.random.default_rng()
        self.np_function = getattr(self.rng, np_generator)
        self.parameters = parameters
        self.value = start if start else self.sample()

    def sample(self) -> float:
        value = self.np_function(**self.parameters)
        if self.min and value < self.min:
            return self.min
        if self.max and value > self.max:
            return self.max
        return self.scale * value

    def next(self) -> Value:
        if self.first:
            self.first = False
        else:
            sample = self.sample()
            if not self.accumulate:
                return sample

            self.value += sample
        return self.value


class Generator:
    id: Final[str]
    data_class: Final[str]
    subset_key: Final[str]
    subsets: Final[Dict]

    def __init__(
        self, world, id: str, data_class: str, subset_key: str, subsets: List[Dict]
    ):
        self.id = id
        self.data_class = data_class
        self.subset_key = subset_key
        self.subsets = {}
        for subset in subsets:
            self.subsets[subset[subset_key]] = subset

        world.add(self)

    @staticmethod
    def _from_yaml(world, params: Dict) -> "Generator":
        id = list(params.keys())
        if len(id) > 1:
            raise ValueError(f"Unable to parse yaml: Multiple keys found in {params}")

        id = id[0]
        params = params[id]

        return Generator(world, id, params["class"], params["key"], params["subsets"])

    def generate(
        self,
        type: Type,
        limits: Dict[str, Tuple[Literal["<", ">"], Number]] = {},
        counts: Dict[Tuple[str, Value], int] = {},
        sort: Optional[str] = None,
        sort_direction: Literal["asc", "desc"] = "asc",
    ) -> List:
        data = []
        id = 0

        for subset in self.subsets.values():
            samplers: Dict[str, Sampler] = {}
            for property, parameters in subset.items():
                samplers[property] = Sampler._from_yaml(property, parameters)

            count = 0
            for (key, value), max in counts.items():
                if subset.get(key, None) == value:
                    count = max
                    break

            while True:
                id += 1
                next = type()
                next.id = f"{id}"
                for property, sampler in samplers.items():
                    setattr(next, property, sampler.next())

                for key, (compare, limit) in limits.items():
                    value = getattr(next, key, None)
                    if value and (
                        (compare == ">" and value > limit)
                        or (compare == "<" and value < limit)
                    ):
                        break

                else:
                    data.append(next)

                    if count > 0:
                        count -= 1
                        if count == 0:
                            break
                    continue

                break

        if sort:
            data.sort(key=lambda o: getattr(o, sort), reverse=sort_direction == "desc")

        return data
