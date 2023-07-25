# Version support
- Users

# Library Consideration
## Pydantic
Pydantic is an excellent library, but I have noticed some flaws in its grand concept. For instance, in version 2, the official guide suggests overriding the `__iter__` method in the `RootModel` if you want to access it as an iterator. However, despite this recommendation, the annotation for `RootModel` remained as `[str, Any]`, leading to inconvenient type-checking errors when attempting to override `RootModel` as a sequence.
{image_here}

While it is likely that running it as is won't cause any actual issues, this is a disappointing outcome for a product concept that relies on annotations. I have concerns about maintaining consistency throughout the entire system, given its overly complex design.

Pydantic concept is type annotation for validation is great, but much tricky because annotation is add-hock for Python language itself.

### Usability of signatures
Both Pydantic `dataclass` and `BaseModel` generates initialization signatures on pyright or pylance, but not well signatured on standard python language server on VS Code.

**Sample Python Class**
```python
@dataclass
class SampleStandardDataclass:
    """Class short description.

    Class Description

    Attributes:
        Horizon (int): horizon in minutes.
        Mode (saxobank.model.common.ChartRequestMode): mode
        Count (int): num of returns

    """

    Horizon: int
    Mode: common.ChartRequestMode
    Count: Optional[int] = None
```

Standard `dataclass` (and attrs\`s `define` decorator), Pydantic `dataclass` and `BaseModel` signatures on python language server looks like this;
| Standard dataclass  and attrs`s define | Pydantic dataclass | Pydantic BaseModel |
| -- | -- | -- |
| `class SampleStandardDataclass(Horizon: int, Mode: common.ChartRequestMode, Count: Optional[int]=None)` | `class SamplePydanticDataclass()` | `class SamplePydanticModel(**data: Any)` |

Because docstrings are also shown on them all, users can know what they needed. But Pydantic behavior indicates **its not pure python way**.

**NOTE**

On pyright or pyrance, type signatures are not namespace quolified. For example, `Mode: common.ChartRequestMode` definition hinted `Mode: ChartRequestMode` like this; And this behavior same in python standard `dataclass` and attrs' `define`.

```python
class SamplePydanticDataclass(
    Horizon: int,
    Mode: ChartRequestMode,
    Count: int | None = None
)
```


## attrs
### Need validators for all fields if validate them all
That's is obvious way and good behavior and philosophy rather than Pydantic does.
```python
@define
class HeartbeatsList:
    _list: List[Heartbeats] = field(init=True, validator=validators.instance_of(list))

    @_list.validator
    def instance_of_members(self, attribute, value):
        if not all([isinstance(mem, Heartbeats) for mem in value]):
            raise ValueError('Instance mismatch')
```



### Conversions
Code attribute signature locked to type before conversion, can't be both before and after conversion.
```{doctest}
>>> def str2reference_id(x: str) -> ReferenceId:
...     return ReferenceId(x)
>>> @define(kw_only=True)
... class Heartbeats:
...     OriginatingReferenceId: ReferenceId = field(converter=str2reference_id, validator=validators.instance_of(ReferenceId))

>>> h = Heartbeats(OriginatingReferenceId='REF1')
>>> print(inspect.signature(Heartbeats))
(*, OriginatingReferenceId: str) -> None
```

### Alias
Can't use illegal name.
```{doctest}
>>> @define
... class OData:
...     odata_skip: int = field(init=True, alias='$skip')
  File "", line 1
    def __init__(self, $skip):
                       ^
SyntaxError: invalid syntax

