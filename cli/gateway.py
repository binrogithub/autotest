#
# Copyright 2024
#
"""Gateway CLI helpers for policy/approval enforcement."""

import argparse
import json
import sys
import traceback


EXIT_TOOL_ERROR = 2
EXIT_POLICY_BLOCK = 3
EXIT_UNEXPECTED_EXCEPTION = 4


class StructuredError(Exception):

    code = 'structured_error'
    exit_code = EXIT_UNEXPECTED_EXCEPTION

    def __init__(self, message, details=None):
        super(StructuredError, self).__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self):
        return {
            'type': 'StructuredError',
            'code': self.code,
            'message': self.message,
            'details': self.details,
        }


class ToolError(StructuredError):

    code = 'tool_error'
    exit_code = EXIT_TOOL_ERROR


class PolicyBlock(StructuredError):

    code = 'policy_block'
    exit_code = EXIT_POLICY_BLOCK


class RunSummary(object):

    def __init__(self, run_id, status, message=None, metadata=None):
        self.run_id = run_id
        self.status = status
        self.message = message
        self.metadata = metadata or {}

    def to_dict(self):
        payload = {
            'type': 'RunSummary',
            'run_id': self.run_id,
            'status': self.status,
        }
        if self.message:
            payload['message'] = self.message
        if self.metadata:
            payload['metadata'] = self.metadata
        return payload


class RunnerEnvelope(object):

    def __init__(self, summary=None, error=None):
        self.summary = summary
        self.error = error

    def to_dict(self):
        payload = {
            'type': 'RunnerEnvelope',
        }
        if self.summary is not None:
            payload['summary'] = self.summary.to_dict()
        if self.error is not None:
            payload['error'] = self.error
        return payload


def enforce_policy(policy):
    """Raise structured errors when a policy payload blocks execution."""
    if policy is None:
        return

    if isinstance(policy, dict):
        if policy.get('tool_error') or policy.get('error'):
            message = policy.get('message') or policy.get('error')
            raise ToolError(message or 'Tool error', details=policy)
        if policy.get('blocked') or policy.get('allowed') is False:
            message = policy.get('message') or 'Policy blocked'
            raise PolicyBlock(message, details=policy)
        status = policy.get('status')
        if status in ('blocked', 'denied'):
            message = policy.get('message') or 'Policy blocked'
            raise PolicyBlock(message, details=policy)
        return

    if isinstance(policy, (list, tuple, set)):
        if policy:
            raise PolicyBlock('Policy blocked',
                              details={'violations': list(policy)})
        return

    if isinstance(policy, basestring):
        raise PolicyBlock(policy)

    if policy is False:
        raise PolicyBlock('Policy blocked')


def enforce_approvals(run_id=None, approve_token=None, safety_ack=None,
                      approvals=None):
    """Validate required approvals, raising ToolError when missing."""
    if approvals is None and isinstance(run_id, dict):
        approvals = run_id
        run_id = approvals.get('run_id')
        approve_token = approvals.get('approve_token')
        safety_ack = approvals.get('safety_ack')
    elif approvals is not None:
        run_id = approvals.get('run_id', run_id)
        approve_token = approvals.get('approve_token', approve_token)
        safety_ack = approvals.get('safety_ack', safety_ack)

    missing = []
    if not run_id:
        missing.append('run_id')
    if not approve_token:
        missing.append('approve_token')
    if not safety_ack:
        missing.append('safety_ack')

    if missing:
        raise ToolError('Missing required approvals',
                        details={'missing': missing})


class _GatewayArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        raise ToolError(message)


def _emit_json(envelope):
    sys.stdout.write(json.dumps(envelope.to_dict()))
    sys.stdout.write('\n')


def _emit_text(summary=None, error=None):
    if error is not None:
        sys.stderr.write('%s\n' % error['message'])
        return
    if summary is not None:
        sys.stdout.write('Run %s: %s\n' % (summary.run_id, summary.status))


def apply_command(args):
    enforce_approvals(args.run_id, args.approve_token, args.safety_ack)
    if args.policy:
        enforce_policy(_load_policy(args.policy))
    summary = RunSummary(run_id=args.run_id, status='applied')
    return summary


def _load_policy(raw_policy):
    try:
        return json.loads(raw_policy)
    except ValueError:
        raise ToolError('Invalid policy JSON')


def build_parser():
    parser = _GatewayArgumentParser(prog='gateway')
    parser.add_argument('--json', action='store_true', default=False)

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    apply_parser = subparsers.add_parser('apply')
    apply_parser.add_argument('--run-id', required=True)
    apply_parser.add_argument('--approve-token', required=True)
    apply_parser.add_argument('--safety-ack', action='store_true')
    apply_parser.add_argument('--policy', default=None)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == 'apply':
            summary = apply_command(args)
        else:
            raise ToolError('Unknown command %s' % args.command)
        envelope = RunnerEnvelope(summary=summary)
        if args.json:
            _emit_json(envelope)
        else:
            _emit_text(summary=summary)
        return 0
    except StructuredError as exc:
        envelope = RunnerEnvelope(error=exc.to_dict())
        if args.json:
            _emit_json(envelope)
        else:
            _emit_text(error=exc.to_dict())
        return exc.exit_code
    except Exception as exc:
        error = {
            'type': 'StructuredError',
            'code': 'unexpected_exception',
            'message': 'Unexpected exception: %s' % exc,
            'details': {'traceback': traceback.format_exc()},
        }
        envelope = RunnerEnvelope(error=error)
        if args.json:
            _emit_json(envelope)
        else:
            _emit_text(error=error)
        return EXIT_UNEXPECTED_EXCEPTION


if __name__ == '__main__':
    sys.exit(main())
