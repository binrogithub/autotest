"""Storage tool handler.

Preview example:
    >>> class Ctx:
    ...     project_id = "proj-123"
    ...     run_id = "run-456"
    >>> preview(Ctx(), {"bucket": "artifacts", "region": "us-central1"})
    RequestSpec(action='storage.bucket.create', project_id='proj-123', resource_name='artifacts-run-456', params={'bucket': 'artifacts', 'region': 'us-central1'})
"""

from core.tools.errors import ToolError
from core.tools.request_spec import RequestSpec


REQUIRED_PARAMS = ("bucket", "region")


def _validate_required(params):
    missing = [key for key in REQUIRED_PARAMS if params.get(key) is None]
    if missing:
        raise ToolError(f"Missing required parameters: {', '.join(missing)}")


def _build_request_spec(ctx, params):
    _validate_required(params)
    if getattr(ctx, "project_id", None) is None:
        raise ToolError("Missing required context field: project_id")
    if getattr(ctx, "run_id", None) is None:
        raise ToolError("Missing required context field: run_id")

    resource_name = f"{params['bucket']}-{ctx.run_id}"
    return RequestSpec(
        action="storage.bucket.create",
        project_id=ctx.project_id,
        resource_name=resource_name,
        params={"bucket": params["bucket"], "region": params["region"]},
    )


def preview(ctx, params):
    """Build a preview request spec for storage bucket creation."""
    return _build_request_spec(ctx, params)


def apply(ctx, params):
    """Build an apply request spec for storage bucket creation."""
    return _build_request_spec(ctx, params)
