from __future__ import absolute_import

import json
import sys

from policies import policy_loader


ERROR_TOOL_NOT_ALLOWED = 'tool_not_allowed'
ERROR_WRITE_NOT_ALLOWED = 'write_not_allowed'


def _error_response(code, message, details=None):
    response = {'code': code, 'message': message}
    if details is not None:
        response['details'] = details
    return response


def _check_tool_allowed(tool_name, policy):
    if policy.allowed_tools is None:
        return None
    if tool_name in policy.allowed_tools:
        return None
    return _error_response(
        ERROR_TOOL_NOT_ALLOWED,
        'Tool is not allowed by policy.',
        details={'tool': tool_name, 'allowed_tools': sorted(policy.allowed_tools)},
    )


def _check_write_allowed(tool_name, policy):
    if policy.allow_write:
        return None
    if tool_name != 'apply':
        return None
    return _error_response(
        ERROR_WRITE_NOT_ALLOWED,
        'Write operations are disabled by policy.',
        details={'tool': tool_name, 'blocked_action': 'apply', 'allowed_action': 'preview'},
    )


def validate_tool_request(tool_name, policy):
    error = _check_tool_allowed(tool_name, policy)
    if error is not None:
        return error
    return _check_write_allowed(tool_name, policy)


def handle_tool_request(tool_request, policy):
    tool_name = tool_request.get('tool')
    if not tool_name:
        return {'error': _error_response('invalid_request', 'Missing tool name.')}
    error = validate_tool_request(tool_name, policy)
    if error is not None:
        return {'error': error}
    return None


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    policy = None
    if argv:
        policy = policy_loader.load_policy(argv[0])
    else:
        policy = policy_loader.Policy()

    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            tool_request = json.loads(line)
        except ValueError:
            error = _error_response('invalid_request', 'Request is not valid JSON.')
            sys.stdout.write(json.dumps({'error': error}) + '\n')
            continue
        response = handle_tool_request(tool_request, policy)
        if response is not None:
            sys.stdout.write(json.dumps(response) + '\n')
            continue
        sys.stdout.write(json.dumps({'result': 'ok'}) + '\n')


if __name__ == '__main__':
    main()
