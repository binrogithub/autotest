from __future__ import absolute_import

import io


class Policy(object):
    def __init__(self, allowed_tools=None, allow_write=True):
        if allowed_tools is not None:
            allowed_tools = set(allowed_tools)
        self.allowed_tools = allowed_tools
        self.allow_write = bool(allow_write)

    @classmethod
    def from_mapping(cls, mapping):
        if mapping is None:
            return cls()
        allowed_tools = mapping.get('allowed_tools')
        allow_write = mapping.get('allow_write', True)
        return cls(allowed_tools=allowed_tools, allow_write=allow_write)


_TRUE_VALUES = set(['true', 'yes', 'on', '1'])
_FALSE_VALUES = set(['false', 'no', 'off', '0'])


def _strip_quotes(value):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def _parse_bool(value, path, line_number):
    normalized = value.strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    raise ValueError(
        'Invalid boolean value for allow_write at {0}:{1}'.format(
            path, line_number
        )
    )


def _parse_inline_list(value):
    value = value.strip()
    if not (value.startswith('[') and value.endswith(']')):
        return None
    inner = value[1:-1].strip()
    if not inner:
        return []
    items = [item.strip() for item in inner.split(',')]
    return [_strip_quotes(item) for item in items if item]


def parse_policy(text, path='<policy>'):
    allowed_tools = None
    allow_write = True
    current_key = None

    if isinstance(text, bytes):
        text = text.decode('utf-8')

    for line_number, line in enumerate(io.StringIO(text), start=1):
        raw_line = line.rstrip('\n')
        stripped = raw_line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        if stripped.startswith('-'):
            if current_key == 'allowed_tools':
                item = stripped[1:].strip()
                if allowed_tools is None:
                    allowed_tools = []
                if item:
                    allowed_tools.append(_strip_quotes(item))
            continue

        current_key = None
        if ':' not in raw_line:
            continue
        key, value = raw_line.split(':', 1)
        key = key.strip()
        value = value.strip()
        if not value:
            current_key = key
            if key == 'allowed_tools' and allowed_tools is None:
                allowed_tools = []
            continue
        if key == 'allowed_tools':
            inline_list = _parse_inline_list(value)
            if inline_list is not None:
                allowed_tools = inline_list
        elif key == 'allow_write':
            allow_write = _parse_bool(value, path, line_number)

    return Policy(allowed_tools=allowed_tools, allow_write=allow_write)


def load_policy(path):
    with open(path, 'rb') as handle:
        text = handle.read()
    return parse_policy(text, path=path)
