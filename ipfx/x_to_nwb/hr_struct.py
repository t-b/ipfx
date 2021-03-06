import re
import struct
import collections


class Struct():
    """High-level wrapper around struct.Struct that makes it a bit easier to
    unpack large, nested structures.

    * Unpacks to dictionary allowing fields to be retrieved by name
    * Optionally massages field data on read
    * Handles arrays and nested structures

    *fields* must be a list of tuples like (name, format) or (name, format,
    function) where *format* must be a simple struct format string like 'i',
    'd', '32s', or '4d'; or another Struct instance.

    *function* may be either a function that filters the data for that field or
    None to exclude the field altogether.

    If *size* is given, then an exception will be raised if the final struct
    size does not match the given size.

    Example::

        class MyStruct(Struct):
            field_info = [
                ('char_field', 'c'),            # single char
                ('char_array', '8c'),           # list of 8 chars
                ('str_field',  '8s', cstr),     # C string of len 8
                ('sub_struct', MyOtherStruct),  # dict generated by s2.unpack
                ('filler', '32s', None),        # ignored field
            ]
            required_size = 300

        fh = open(fname, 'rb')
        data = MyStruct(fh)

    """

    field_info = None
    required_size = None
    _fields_parsed = None

    def __init__(self, data, endian='<'):
        """Read the structure from *data* and return an ordered dictionary of
        fields.

        *data* may be a string or file.
        *endian* may be '<' or '>'
        """
        field_info = self._field_info()
        if not isinstance(data, (str, bytes)):
            data = data.read(self._le_struct.size)
        if endian == '<':
            items = self._le_struct.unpack(data)
        elif endian == '>':
            items = self._be_struct.unpack(data)
        else:
            raise ValueError('Invalid endian: %s' % endian)

        fields = collections.OrderedDict()

        i = 0
        for name, fmt, func in field_info:
            # pull item(s) out of the list based on format string
            if len(fmt) == 1 or fmt[-1] == 's':
                item = items[i]
                i += 1
            else:
                n = int(fmt[:-1])
                item = items[i:i+n]
                i += n

            # try unpacking sub-structure
            if isinstance(func, tuple):
                substr, func = func
                item = substr(item, endian)

            # None here means the field should be omitted
            if func is None:
                continue
            # handle custom massaging function
            if func is not True:
                item = func(item)
            fields[name] = item
            setattr(self, name, item)

        self.fields = fields

    @classmethod
    def _field_info(cls):
        if cls._fields_parsed is not None:
            return cls._fields_parsed

        fmt = ''
        fields = []
        for items in cls.field_info:
            if len(items) == 3:
                name, ifmt, func = items
            else:
                name, ifmt = items
                func = True

            if isinstance(ifmt, type) and issubclass(ifmt, Struct):
                # instructs to unpack with sub-struct before calling function
                func = (ifmt, func)
                ifmt = '%ds' % ifmt.size()
            elif re.match(r'\d*[xcbB?hHiIlLqQfdspP]', ifmt) is None:
                raise TypeError('Unsupported format string "%s"' % ifmt)

            fields.append((name, ifmt, func))
            fmt += ifmt
        cls._le_struct = struct.Struct('<' + fmt)
        cls._be_struct = struct.Struct('>' + fmt)
        cls._fields_parsed = fields
        if cls.required_size is not None:
            assert cls._le_struct.size == cls.required_size, \
                "{} expected vs. {}".format(
                    cls.required_size, cls._le_struct.size)
        return fields

    @classmethod
    def size(cls):
        cls._field_info()
        return cls._le_struct.size

    @classmethod
    def array(cls, x):
        """Return a new StructArray class of length *x* and using this struct
        as the array item type.
        """
        return type(cls.__name__+'[%d]' % x, (StructArray,),
                    {'item_struct': cls, 'array_size': x})

    def __str__(self, indent=0):
        indent_str = '    '*indent
        r = indent_str + '%s(\n' % self.__class__.__name__
        if not hasattr(self, 'fields'):
            r = r[:-1] + '<initializing>)'
            return r
        for k, v in self.fields.items():
            if isinstance(v, Struct):
                r += indent_str + '    %s = %s\n' % \
                    (k, v.__str__(indent=indent+1).lstrip())
            else:
                r += indent_str + '    %s = %r\n' % (k, v)
        r += indent_str + ')'
        return r

    def get_fields(self):
        """Recursively convert struct fields+values to nested dictionaries.
        """
        fields = self.fields.copy()
        for k, v in fields.items():
            if isinstance(v, StructArray):
                fields[k] = [x.get_fields() for x in v.array]
            elif isinstance(v, Struct):
                fields[k] = v.get_fields()
        return fields


class StructArray(Struct):
    item_struct = None
    array_size = None

    def __init__(self, data, endian='<'):
        if not isinstance(data, (str, bytes)):
            data = data.read(self.size())
        items = []
        isize = self.item_struct.size()
        for i in range(self.array_size):
            d = data[:isize]
            data = data[isize:]
            items.append(self.item_struct(d, endian))
        self.array = items

    def __getitem__(self, i):
        return self.array[i]

    @classmethod
    def size(self):
        return self.item_struct.size() * self.array_size

    def __str__(self, indent=0):
        r = '    '*indent + '%s(\n' % self.__class__.__name__
        for item in self.array:
            r += item.__str__(indent=indent+1) + ',\n'
        r += '    '*indent + ')'
        return r
