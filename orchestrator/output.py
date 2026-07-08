"""Log-streaming helpers used by ``main()`` to duplicate stdout across
the terminal and the log files (REQ-36, REQ-37)."""
import sys

# Force UTF-8 + write-through so every print() reaches the log file immediately,
# even when stdout is a pipe (Start-Process, CI, nohup, etc.).
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace", write_through=True)


class _Tee:
    """Write to primary + any number of secondary streams simultaneously.

    ``flush()`` is called after every ``write()`` so data reaches all
    destinations immediately regardless of Python's internal buffering
    (important when stdout is a pipe or Start-Process redirection).
    """

    def __init__(self, primary, *secondaries):
        self._primary = primary
        self._secondaries = secondaries

    def write(self, data):
        self._primary.write(data)
        self._primary.flush()
        for s in self._secondaries:
            s.write(data)

    def flush(self):
        self._primary.flush()
        for s in self._secondaries:
            s.flush()

    def __getattr__(self, name):
        return getattr(self._primary, name)


class _ProgressFilter:
    """Wraps a file and only writes lines that are NOT subprocess output.

    Subprocess output is forwarded by ``run_claude()`` / ``run_tests()``
    prefixed with ``  │ ``. This filter buffers incomplete writes until a
    newline arrives, then silently drops lines starting with that prefix.
    Everything else (task headers, ``[OK]`` / ``[FAIL]`` markers, summary
    table) is written through.

    The result is a compact ``*.progress.log`` whose entire content fits in
    a short terminal window or tool output pane.
    """

    def __init__(self, file):
        self._file = file
        self._buf = ""

    def write(self, data):
        self._buf += data
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            if not line.startswith("  │"):
                self._file.write(line + "\n")
                self._file.flush()

    def flush(self):
        if self._buf and not self._buf.startswith("  │"):
            self._file.write(self._buf)
            self._buf = ""
        self._file.flush()

    def close(self):
        self.flush()
        self._file.close()
