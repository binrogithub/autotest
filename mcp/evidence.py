"""Evidence helpers for run reporting."""


def build_evidence(preview_result, apply_result):
    """Return an evidence dictionary describing the run outcomes."""
    return {
        "preview": preview_result,
        "apply": apply_result,
    }
