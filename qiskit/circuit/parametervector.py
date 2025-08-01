# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Parameter Vector Class to simplify management of parameter lists."""

from uuid import uuid4, UUID

from qiskit._accelerate.circuit import ParameterVectorElement


class ParameterVector:
    """A container of many related :class:`Parameter` objects.

    This class is faster to construct than constructing many :class:`Parameter` objects
    individually, and the individual names of the parameters will all share a common stem (the name
    of the vector).  For a vector called ``v`` with length 3, the individual elements will have
    names ``v[0]``, ``v[1]`` and ``v[2]``.

    The elements of a vector are sorted by the name of the vector, then the numeric value of their
    index.

    This class fulfill the :class:`collections.abc.Sequence` interface.
    """

    __slots__ = ("_name", "_params", "_root_uuid")

    def __init__(self, name, length=0):
        self._name = name
        self._root_uuid = uuid4()
        root_uuid_int = self._root_uuid.int
        self._params = [
            ParameterVectorElement(self, i, UUID(int=root_uuid_int + i)) for i in range(length)
        ]

    @property
    def name(self):
        """The name of the :class:`ParameterVector`."""
        return self._name

    @property
    def params(self):
        """A list of the contained :class:`ParameterVectorElement` instances.

        It is not safe to mutate this list."""
        return self._params

    def index(self, value):
        """Find the index of a :class:`ParameterVectorElement` within the list.

        It is typically much faster to use the :attr:`ParameterVectorElement.index` property."""
        return self._params.index(value)

    def __getitem__(self, key):
        return self.params[key]

    def __iter__(self):
        return iter(self.params)

    def __len__(self):
        return len(self._params)

    def __str__(self):
        return f"{self.name}, {[str(item) for item in self.params]}"

    def __repr__(self):
        return f"{self.__class__.__name__}(name={repr(self.name)}, length={len(self)})"

    def __getnewargs__(self):
        return (self._name, len(self._params))

    def __getstate__(self):
        params = [p.__getstate__() for p in self._params]
        return (self._name, params, self._root_uuid)

    def __setstate__(self, state):
        self._name, params, self._root_uuid = state
        self._params = [ParameterVectorElement(*p) for p in params]

    def resize(self, length):
        """Resize the parameter vector.  If necessary, new elements are generated.

        Note that the UUID of each :class:`.Parameter` element will be generated
        deterministically given the root UUID of the ``ParameterVector`` and the index
        of the element.  In particular, if a ``ParameterVector`` is resized to
        be smaller and then later resized to be larger, the UUID of the later
        generated element at a given index will be the same as the UUID of the
        previous element at that index.
        This is to ensure that the parameter instances do not change.

        >>> from qiskit.circuit import ParameterVector
        >>> pv = ParameterVector("theta", 20)
        >>> elt_19 = pv[19]
        >>> rv.resize(10)
        >>> rv.resize(20)
        >>> pv[19] == elt_19
        True
        """
        if length > len(self._params):
            root_uuid_int = self._root_uuid.int
            self._params.extend(
                [
                    ParameterVectorElement(self, i, UUID(int=root_uuid_int + i))
                    for i in range(len(self._params), length)
                ]
            )
        else:
            del self._params[length:]
