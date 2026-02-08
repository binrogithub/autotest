# Autotest Quickstart

This quickstart is designed for a **first-time user** who wants to run a local smoke test and see results quickly. It focuses on the Autotest **client** workflow and links to the longer server installation docs.

## Installation (local client)

1. **Clone the repository** (or use your existing checkout):

   ```bash
   git clone --recursive https://github.com/autotest/autotest.git
   cd autotest
   ```

2. **Confirm Python is available**. Autotest is a legacy codebase that targets Python 2.x in many environments. If you are on a modern system, consider using a container or VM that provides the expected Python runtime and tools.

3. (Optional) **Install OS dependencies** if you plan to run more than the simple smoke test. The server install docs contain distro-specific dependency lists:
   * Red Hat: https://autotest.readthedocs.org/en/latest/main/sysadmin/AutotestServerInstallRedHat.html
   * Ubuntu/Debian: https://autotest.readthedocs.org/en/latest/main/sysadmin/AutotestServerInstall.html

## Configuration (minimal for smoke test)

* **No configuration is required** for the local smoke test below.
* If you move beyond the local client and want server/database features, start by editing the configuration in `global_config.ini` and overriding sensitive values in `shadow_config.ini` (e.g., database passwords). Keep `shadow_config.ini` out of source control when adding secrets.

## Preview/Demo: Run the local smoke test

From the repository root:

```bash
client/autotest-local --verbose run sleeptest
```

This runs a tiny “sleeptest” that simply sleeps for a few seconds and is commonly used as a sanity check.

## Output interpretation

After the run completes, results are stored in:

```
client/results/
```

Key files to check in the newest results directory include:

* `status.log` — high-level status lines (start/end, pass/fail).
* `debug/` — verbose debug logs.

A successful run typically ends with a `GOOD` or `PASS` line in `status.log`.

## Safety guidance

* **Prefer a VM or disposable test machine.** Some Autotest tests install kernels or reboot the host.
* Some tests require **root**. If you run as root and then return to a normal user, you may need to clean up root-owned directories:

  ```bash
  sudo rm -rf client/tmp client/results
  ```

* Start with the `sleeptest` above before attempting more invasive tests.

## Next steps

* Client quickstart (official docs): https://autotest.readthedocs.org/en/latest/main/local/ClientQuickStart.html
* Server quickstart: https://autotest.readthedocs.org/en/latest/main/remote/ServerQuickStart.html
* Full documentation index: https://autotest.readthedocs.org/en/latest/index.html
