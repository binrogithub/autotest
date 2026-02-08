# Autotest Guidebook

This guidebook expands the quickstart with more detail on installation, configuration, preview/demo workflows, output interpretation, and safety guidance. It is written to help a first-time user complete the **smoke test** steps successfully.

---

## 1) Installation

### Local client (fastest path for a smoke test)

1. Clone the repository and enter the directory:

   ```bash
   git clone --recursive https://github.com/autotest/autotest.git
   cd autotest
   ```

2. Ensure you are running on a system that can provide the expected Python runtime (many Autotest components target Python 2.x). If your host OS does not ship Python 2, use a VM or container image that does.

### Server + database (optional, heavier setup)

If you need the web frontend, scheduler, or database-backed test grids, follow the official install guides for your distribution:

* Red Hat: https://autotest.readthedocs.org/en/latest/main/sysadmin/AutotestServerInstallRedHat.html
* Ubuntu/Debian: https://autotest.readthedocs.org/en/latest/main/sysadmin/AutotestServerInstall.html

---

## 2) Configuration

Autotest configuration is split across two files in the repository root:

* `global_config.ini` — defaults and shared settings.
* `shadow_config.ini` — overrides and secrets (database passwords, API tokens, etc.).

**Best practice:** keep `shadow_config.ini` out of version control when adding secrets.

### Useful configuration knobs for smoke tests

* **Output directory:**
  * In `global_config.ini` under `[CLIENT]`, you can set `output_dir` to redirect results outside the repo.
* **Autotest install path:**
  * Under `[COMMON]`, `autotest_top_path` should reflect where you installed the repository if you deploy outside `/usr/local/autotest`.

No configuration changes are required for the minimal smoke test below.

---

## 3) Preview/Demo: Smoke test walkthrough

The simplest smoke test is the built-in `sleeptest`.

### Step-by-step

1. From the repo root, run:

   ```bash
   client/autotest-local --verbose run sleeptest
   ```

2. Wait for the test to complete (it typically takes only a few seconds).

3. Inspect results in `client/results/` as described below.

### Alternate smoke test: control file

You can also run a test using the control file directly:

```bash
client/autotest-local client/tests/sleeptest/control
```

---

## 4) Output interpretation

Results are stored under:

```
client/results/
```

Look in the newest results directory. Common artifacts include:

* `status.log` — summary of test events and pass/fail status.
* `debug/` — detailed logs for troubleshooting.
* `profiling/` — performance logs (if enabled).

**Typical success indicator:** the end of `status.log` shows a `GOOD` or `PASS` line.

---

## 5) Safety guidance

Autotest can perform invasive actions (reboots, kernel installs, destructive operations). Follow these safety practices:

* **Use a VM or disposable machine** for first-time experiments.
* **Run as a regular user when possible.** Some tests require root; when you must use root, clean up any root-owned directories before switching back to a normal user:

  ```bash
  sudo rm -rf client/tmp client/results
  ```

* **Start with `sleeptest`.** It is the least invasive sanity check.

---

## 6) Troubleshooting the smoke test

* **Permission errors** (e.g., `/dev/rtc0`): rerun as root or choose a test that does not require privileged access.
* **Missing dependencies**: use the server install docs above for dependency lists and package names for your distro.
* **Results not generated**: verify you are running from the repo root and that `client/results/` is writable.

---

## 7) More documentation

* Client quickstart: https://autotest.readthedocs.org/en/latest/main/local/ClientQuickStart.html
* Server quickstart: https://autotest.readthedocs.org/en/latest/main/remote/ServerQuickStart.html
* Documentation index: https://autotest.readthedocs.org/en/latest/index.html
