"""Optional dependency unit tests."""

import subprocess
import sys
import textwrap

import pytest

# Installed by the plot extra or the dev group, never by the base package
OPTIONAL_MODULES = ["matplotlib", "plotly", "line_profiler"]

CORE_MODULES = [
    "seabirdscientific.cal_coefficients",
    "seabirdscientific.constants",
    "seabirdscientific.contour",
    "seabirdscientific.conversion",
    "seabirdscientific.eos80_conversion",
    "seabirdscientific.eos80_processing",
    "seabirdscientific.instrument_data",
    "seabirdscientific.interpret_sbs_variable",
    "seabirdscientific.processing",
    "seabirdscientific.utils",
]


def run_without_optional_modules(code: str) -> subprocess.CompletedProcess:
    """Runs code in a fresh interpreter where importing any of the
    optional modules raises ImportError, as if they weren't installed

    :param code: python source to run
    :return: the completed process
    """
    blocker = "import sys\n" + "".join(
        f"sys.modules[{name!r}] = None\n" for name in OPTIONAL_MODULES
    )
    return subprocess.run(
        [sys.executable, "-c", blocker + textwrap.dedent(code)],
        capture_output=True,
        text=True,
        check=False,
    )


class TestOptionalDependencies:
    @pytest.mark.parametrize("module", CORE_MODULES)
    def test_core_module_imports_without_optional_dependencies(self, module):
        result = run_without_optional_modules(f"import {module}")
        assert result.returncode == 0, result.stderr

    def test_visualization_import_error_names_plot_extra(self):
        result = run_without_optional_modules("import seabirdscientific.visualization")
        assert result.returncode != 0
        assert "pip install seabirdscientific[plot]" in result.stderr

    def test_utils_plot_error_names_plot_extra(self):
        result = run_without_optional_modules(
            """
            import numpy as np
            from seabirdscientific.utils import plot
            plot(x=np.zeros(3))
            """
        )
        assert result.returncode != 0
        assert "pip install seabirdscientific[plot]" in result.stderr

    def test_utils_profile_error_names_line_profiler(self):
        result = run_without_optional_modules(
            """
            from seabirdscientific.utils import profile
            profile(print)
            """
        )
        assert result.returncode != 0
        assert "pip install line-profiler" in result.stderr
