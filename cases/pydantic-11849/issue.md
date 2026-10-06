# (race condition?) Subclass skipped in model instantiation

Reported by @stverhae on 2025-05-07

### Initial Checks

- [x] I confirm that I'm using Pydantic V2

### Description

After upgrading to pydantic 2.11.3 we have observed rare occurrences of a bug that seems to point to some type of race condition. We have not been able to reproduce this in a controlled setting, but 1% of our production containers shows this bug close after initial startup.

This happens on multiple models which directly or indirectly derive from `BaseModel` and we observe that the lowest class in the inheritance chain seems to have been mysteriously *skipped*. Please refer to the code example for more clarity. 

The example 1 is by far the most pure and most minimalistic one, example 2 shows an occurance where there is a chain of inheritance. I've included it to give a more detailed perspective in the behaviour where it seems to skip 1 layer of inheritance.

### Example Code

```Python
from pydantic import BaseModel
from typing import Self

class Translatable(BaseModel):   
    en: str = ""
    ...

class Direct(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str
    description: Optional[Translatable] = None
    ...

d = Direct(id="test", description=Translatable(en="ok")) # raises PydanticUserError("Pydantic models should inherit from BaseModel, BaseModel cannot be instantiated directly")
# The translatable was intantiated correctly, but `Direct` seems do BE BaseModel



# second example

class A(BaseModel):
    @model_validator(mode="after")
    def _modelAfterValidator(self, info: ValidationInfo) -> Self:
        ...
        return self

class B(A):
    id: str

class C(B):
    name: str | None = None


c1 = C.model_validate({"name": "test", "id": "ok1"}) # correctly instantiates
c2 = C.model_validate({"name": "test", "id": "ok2"}) # correctly instantiates
c3 = C.model_validate({"name": "test", "id": "ok3"}) # correctly instantiates
print(c1) # B(id="ok1")   __repr__ shows class B instead of C!!!
print(c2) # B(id="ok2")
c1.name # raises AttributeError("'B' object has no attribute 'name'"). again B instead of C
```

### Python, Pydantic & OS Version

```Text
pydantic version: 2.11.3
        pydantic-core version: 2.33.1
          pydantic-core build: profile=release pgo=false
                 install path: /opt/venv/lib/python3.13/site-packages/pydantic
               python version: 3.13.2 (main, Apr  8 2025, 08:56:23) [GCC 12.2.0]
                     platform: Linux-6.10.14-linuxkit-aarch64-with-glibc2.36
             related packages: typing_extensions-4.12.2 mypy-1.15.0
                       commit: unknown
```
