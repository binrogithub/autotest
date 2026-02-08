"""Compute tool handler.

Preview example:
    >>> class Ctx:
    ...     project_id = "proj-123"
    ...     run_id = "run-456"
    >>> preview(Ctx(), {"name": "worker", "image": "ubuntu-22-04", "machine_type": "n1-standard-4"})
    RequestSpec(action='compute.instance.create', project_id='proj-123', resource_name='worker-run-456', params={'name': 'worker', 'image': 'ubuntu-22-04', 'machine_type': 'n1-standard-4'})
"""

from core.tools.errors import ToolError
from core.tools.request_spec import RequestSpec


REQUIRED_PARAMS = ("name", "image", "machine_type")


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

    resource_name = f"{params['name']}-{ctx.run_id}"
    return RequestSpec(
        action="compute.instance.create",
        project_id=ctx.project_id,
        resource_name=resource_name,
        params={
            "name": params["name"],
            "image": params["image"],
            "machine_type": params["machine_type"],
        },
    )


def preview(ctx, params):
    """Build a preview request spec for compute instance creation."""
    return _build_request_spec(ctx, params)


def apply(ctx, params):
    """Build an apply request spec for compute instance creation."""
    return _build_request_spec(ctx, params)
