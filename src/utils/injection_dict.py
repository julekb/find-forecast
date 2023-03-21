"""
Most of this code was take from some random, helpful guy on Reddit:
https://www.reddit.com/r/Python/comments/2cfobr/comment/cjf105l/?utm_source=share&utm_medium=web2x&context=3

A small 1-to-1 dictionary library. Shares inspiration from bidict:

    https://pypi.python.org/pypi/bidict/0.1.1

Implementation similarities are mostly coincidental. The ordered variant
was an idea stolen from

    https://bitbucket.org/jab/bidict/issue/1/ordereddict-integration

I'm not sure what you'd want one for, but it's there if you need it.


The advantage of this package is the simplicity of implementation and
usage. There are no hacks. You just get a forward view and a backwards
view. Both act just like injections, and the isomorphism is transparent.

This is also correct with initialisation and updating, although that may
come at a speed loss. Because the implementation is simplified, a lot of
internal and external magic is now gone. This is also doesn't compare
equal to non-Injections by default, much like `[] != ()` by default.

Getting the inverse of a pre-existing Injection is purposefully not
supported. If you want such a thing, build a relevant namedtuple of the
two directions and pass that around instead. If you really don't want
to do that (you're insane, perhaps), fork the code and add an inverse
property yourself.

The OrderedInjection prevents use of pair methods, because it complicates
equality. The expected behaviour for equality is unclear as it's not
obvious when order is relevant. With single-direction injections, only
forward order exists. Further, __setitem__ needs additional checking for
bidirectionally ordered variants, to prevent deletions from removing order.


Despite the copied ideas, the code is my own. Thought credit goes to
everyone on the mailing list from

    https://mail.python.org/pipermail/python-list/2009-November/558834.html

For reasons of sanity, all code is public domain. Seriously, do
anything you want with it.
"""
from collections.abc import KeysView, MutableMapping


class InjectionDict(MutableMapping):
    """
    Create an injection dict from a mapping or iterable, and keyword
    arguments. An injection is like a dictionary except that
    values must be unique.

    To use the injection in either direction, use InjectionDict.pair.

    Like with dictionaries, setting an item can remove an old pair.
    Unlike with dictionaries, this happens in both directions:

        print(inj)
        #>>> {0 → 0, 1 → 1}

        # Shares start with 0 → 0 and end with 1 → 1,
        # so both paths are collapsed into 0 → 1.
        inj[0] = 1

        print(inj)
        #>>> {0 → 1}
    """

    def __init__(self, mapping_or_iterable={}, **kwargs):
        self._forward = {}
        self._backward = {}

        # The trick in bidict wrecks the order, so don't use it.
        self.update(mapping_or_iterable, **kwargs)

    @classmethod
    def pair(cls, *args, **kwargs):
        """
        Create and return a (forward, backward) tuple of
        InjectionDicts, with backward being the inverse of
        forward.

        Mutations to either object affect both InjectionDicts.
        """
        forward = cls(*args, **kwargs)

        backward = cls()
        backward._forward = forward._backward
        backward._backward = forward._forward

        return forward, backward

    def __setitem__(self, item, complement):
        # Make sure they're hashable before
        # destroying things
        {item, complement}

        # If we point to something, there's
        # something pointing back to us. Remove it.
        if item in self._forward:
            del self._backward[self._forward[item]]

        # If our target is pointing to something,
        # we are pointing to it. Remove that.
        if complement in self._backward:
            del self._forward[self._backward[complement]]

        self._forward[item] = complement
        self._backward[complement] = item

    def __delitem__(self, item):
        del self._backward[self._forward.pop(item)]

    # Shallow wrappers

    def __getitem__(self, item):
        return self._forward[item]

    def __iter__(self):
        return iter(self._forward)

    def __len__(self):
        return len(self._forward)

    # KeysView > ValuesView, so override InjectionDict.values
    # to return a KeysView from the inverted dictionary.
    #
    # Also override `keys` to return a view directly on the
    # underlying dictionary, for prettiness and speed.

    def keys(self):
        return KeysView(self._forward)

    def values(self):
        return KeysView(self._backward)

    # Printing routines

    def __str__(self):
        if not self:
            return "{→}"

        pairstrings = ("{!r} → {!r}".format(*pair) for pair in self.items())
        return "{{{}}}".format(", ".join(pairstrings))

    def __repr__(self):
        return "{}({})".format(type(self).__name__, self._forward)

    # More type-strict than default
    def __eq__(self, other):
        if not isinstance(other, InjectionDict):
            return NotImplemented

        return self._forward == other._forward

    # Faster than default
    def clear(self):
        self._forward.clear()
        self._backward.clear()

    clear.__doc__ = MutableMapping.clear.__doc__

    # Not in ABC, but dict has it
    def copy(self):
        new = type(self)()
        new._forward = self._forward.copy()
        new._backward = self._backward.copy()
        return new

    @property
    def backward(self):
        return self._backward


def create_bijection_dict(*args, **kwargs):
    bdict, _ = InjectionDict.pair(*args, **kwargs)
    return bdict
