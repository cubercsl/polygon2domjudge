# Polygon2DOMjudge

Process Polygon Package to DOMjudge Package.

Master: [![Build Status](https://travis-ci.org/2014CAIS01/polygon2domjudge.svg?branch=master)](https://travis-ci.org/2014CAIS01/polygon2domjudge)
Develop: [![Build Status](https://travis-ci.org/2014CAIS01/polygon2domjudge.svg?branch=develop)](https://travis-ci.org/2014CAIS01/polygon2domjudge)

## Usage

Running `p2d` in the problemset directory, you will get these three problem packages if process with no errors.
```
.
├── problems.yaml
├── ProblemA
├── ProblemB
└── ProblemC
```
Running `p2d` with command-line option `-h` gives documentation on what arguments it accept.

## Install
### Method 1: Install the Python package

Run
```bash
$ pip install git+https://github.com/2014CAIS01/polygon2domjudge
```
Or if you don't want a system-wide installation,
```
$ pip install --user git+https://github.com/2014CAIS01/polygon2domjudge
```

With this second option, in order to get the command line scripts, you need to make sure that the local user bin path used (e.g., on Linux, `$HOME/.local/bin`) is in your `$PATH`.

### Method 2: Run directly from the repository

If you intend to help develop polygon2domjudge, or if you just want a bare-bones way of running them, this is your option.

For this method, you need to clone the repository.

When this is done, you can run the program `bin/p2d.sh` directly from the repository.

## Configuration
System-wide configuration files are placed in `/etc/polygon2domjudge/`, and user-specific configuration files are placed in `$HOME/.config/polygon2domjudge/` (or in `$XDG_CONFIG_HOME` if this is defined). The following files can be used to change configuration:

1. `checkers.yaml`: Use it to override the default checkers configuration. For examples, your own checker written by `testlib` can be remapped to DOMjudge default output validator, you can simple place a file `/etc/polygon2domjudge/checkers.yaml` (or `~/.config/polygon2domjudge/checkers.yaml` if you only want to make the change for your user) containing the following:
    ```yaml
    casewcmp:
      md5sum: b70e0031f1596501f33844ef512bd35e
      validator_flags: case_sensitive space_change_sensitive
    ```
For more details on the format of the checker specifications and what the default settings are, see the default version of [checkers.yaml](p2d/config/checkers.yaml)

2. `results.yaml`: Use it to override the default results configuration. For examples, in your polygon problem packages, the tag `REJECTED`'s expected result is `wrong_answer`.

    Note that a tag can not have two or more results, so you'd better override the entire file.

    If you are not sure whether you should use it, then you probably shouldn't.

    ```yaml
    wrong_answer:
      - WRONG_ANSWER
      - PRESENTATION_ERROR
      - REJUECTED
    run_time_error:
      - TIME_LIMIT_EXCEEDED_OR_MEMORY_LIMIT_EXCEEDED
      - MEMORY_LIMIT_EXCEEDED
      - FAILED
    ```

3. `problems.yaml`: Use it to specify every problem's code, color, number of samples in your problemset. You can put it at your problemset directory. See the example [problems.yaml](p2d/config/problems.yaml) for detail.

4. `misc.yaml`: `testlib` PATH and some other configuration on developing. If you are not sure whether you should use it, then you probably shouldn't.

