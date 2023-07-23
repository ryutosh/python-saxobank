## Version support
- Users

## Why not use Pydantic?
Pydantic is an excellent library, but I have noticed some flaws in its grand concept. For instance, in version 2, the official guide suggests overriding the __iter__ method in the RootModel if you want to access it as an iterator. However, despite this recommendation, the annotation for RootModel remained as [str, Any], leading to inconvenient type-checking errors when attempting to override RootModel as a sequence.
{image_here}

While it is likely that running it as is won't cause any actual issues, this is a disappointing outcome for a product concept that relies on annotations. I have concerns about maintaining consistency throughout the entire system, given its overly complex design.

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

Pydantic concept is type annotation for validation is great, but much tricky because annotation is add-hock for Python language itself.


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

