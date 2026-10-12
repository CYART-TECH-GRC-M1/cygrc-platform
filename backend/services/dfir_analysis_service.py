import subprocess
from pathlib import Path
from typing import Any

from backend.core.config import settings


class DfirAnalysisError(Exception):
    """Raised when forensic analysis cannot safely run."""


# Only explicitly approved plugins can be requested through this adapter.
APPROVED_VOLATILITY_PLUGINS = {
    "windows.info",
    "windows.pslist",
    "windows.pstree",
    "windows.cmdline",
    "windows.netscan",
    "linux.pslist",
    "mac.pslist",
}


def run_volatility_analysis(
    evidence_path: str,
    plugin: str,
) -> dict[str, Any]:
    """Run an approved Volatility plugin without modifying the source file.

    The evidence must be a regular file within DFIR_EVIDENCE_ROOT.
    The executable must be explicitly configured. No shell is used.
    """

    if plugin not in APPROVED_VOLATILITY_PLUGINS:
        raise DfirAnalysisError("Volatility plugin is not approved.")

    if not settings.DFIR_EVIDENCE_ROOT:
        raise DfirAnalysisError("DFIR evidence root is not configured.")

    if not settings.VOLATILITY3_EXECUTABLE:
        raise DfirAnalysisError("Volatility 3 executable is not configured.")

    root = Path(settings.DFIR_EVIDENCE_ROOT).resolve()
    source = Path(evidence_path).resolve()
    executable = Path(settings.VOLATILITY3_EXECUTABLE).resolve()

    if not root.is_dir():
        raise DfirAnalysisError("Configured evidence root does not exist.")

    if not source.is_relative_to(root):
        raise DfirAnalysisError(
            "Evidence file must be inside the configured evidence root."
        )

    if not source.is_file():
        raise DfirAnalysisError("Evidence file does not exist.")

    if source.stat().st_size == 0:
        raise DfirAnalysisError("Evidence file is empty.")

    if not executable.is_file():
        raise DfirAnalysisError(
            "Configured Volatility 3 executable was not found."
        )

    timeout = settings.DFIR_ANALYSIS_TIMEOUT_SECONDS
    if timeout <= 0:
        raise DfirAnalysisError("Analysis timeout must be positive.")

    try:
        completed = subprocess.run(
            [
                str(executable),
                "-f",
                str(source),
                plugin,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise DfirAnalysisError(
            "Volatility analysis timed out."
        ) from exc
    except OSError as exc:
        raise DfirAnalysisError(
            "Volatility could not be started."
        ) from exc

    if completed.returncode != 0:
        raise DfirAnalysisError(
            "Volatility analysis failed. Review the tool's diagnostic output."
        )

    return {
        "status": "COMPLETED",
        "tool": "VOLATILITY3",
        "plugin": plugin,
        "source_path": str(source),
        "return_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }