import subprocess

def test_build_summary_runs():
    """Smoke test: run the build_summary script and expect it to complete successfully."""
    result = subprocess.run(["python3", "nba-player-performance/src/build_summary.py"], check=False)
    assert result.returncode == 0, f"build_summary.py exited with {result.returncode}"
