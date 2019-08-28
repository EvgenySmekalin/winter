import dataclasses

from ..converters import convert
from ..core import annotate_method


class _ResponseHeaderMeta(type):
    def __getitem__(self, value_type):
        assert isinstance(value_type, type), 'value_type must be a type'
        return _ResponseHeaderMeta.__new__(
            type(self),
            f'{self.__name__}[{value_type.__name__}]',
            (self, ),
            {
                '_value_type': value_type,
            },

        )


@dataclasses.dataclass
class ResponseHeaderAnnotation:
    header_name: str
    argument_name: str


def response_header(header_name: str, argument_name: str):

    def wrapper(func_or_method):
        annotation = ResponseHeaderAnnotation(header_name, argument_name)
        annotation_decorator = annotate_method(annotation)
        method = annotation_decorator(func_or_method)
        argument = method.get_argument(argument_name)
        method_name = method.func.__name__
        assert argument is not None, f'Not found argument "{argument_name}" in "{method_name}"'
        return method
    return wrapper


class ResponseHeader(metaclass=_ResponseHeaderMeta):
    _value_type = str

    def __init__(self, headers, header_name):
        self._headers = headers
        self._header_name = header_name

    def __str__(self):
        return f'{self.__class__.__name__}(headers={self._headers}, header_name={self._header_name})'

    def __repr__(self):
        return str(self)

    def set(self, value):
        self._headers[self._header_name] = convert(value, self._value_type)
