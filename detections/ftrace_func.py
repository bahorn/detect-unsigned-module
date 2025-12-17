"""
This is a script to do behavioural testing of ftrace, based off a collection of
other scripts that got merged into just this one.
"""
import os
import sys
import time
# to detect the kprobe trick to resolve symbols
SUS_FUNCS = 'kallsyms_lookup_name'


def atomic_write(path, value):
    with open(path, 'wb', buffering=0) as f:
        bvalue = value
        if isinstance(bvalue, int):
            bvalue = str(bvalue)
        if isinstance(bvalue, str):
            bvalue = bytes(bvalue, 'ascii')
        f.write(bvalue)
    # there is a race condition in singularity, so if you read nothing without
    # this, thats a detection
    time.sleep(0.1)


def atomic_read(path):
    with open(path, 'r') as f:
        res = f.read()
    return res


# used to parse the output of {enabled,touched}_functions
def normalize_lines(text):
    """Merge lines starting with whitespace to the previous line."""
    lines = text.split('\n')
    result = []

    for line in lines:
        if line and line[0].isspace() and result:
            # Merge with previous line
            result[-1] += ' ' + line.lstrip()
        else:
            if line != '':
                result.append(line)
    return result


class Ftrace:
    """
    Class to configure ftrace, supporting what I needed.

    Lacking support for a lot of tracers, etc.
    """

    def __init__(self, tracefs='/sys/kernel/tracing', sysctl='/proc/sys'):
        self._tracefs = tracefs
        self._sysctl = sysctl
        # want these implementations to be hotswapable to work around rootkit
        # filtering, as you can sometimes bypass bad implementations with weird
        # seeking behaviour or other tricks.
        self._atomic_read = atomic_read
        self._atomic_write = atomic_write

    def status(self):
        """
        Get the current status, and active tracer
        """
        enabled = self.read_sysctl('kernel.ftrace_enabled')
        return int(enabled)> 0

    def enable(self):
        """
        Enable ftrace via the sysctl interface
        """
        self.write_sysctl('kernel.ftrace_enabled', 1)

    def disable(self):
        """
        Disable ftrace via the sysctl interface
        """
        self.write_sysctl('kernel.ftrace_enabled', 0)

    def tracing_on(self):
        """
        writes to tracing_on to enable writing to the kernel buffers.
        """
        self._atomic_write(f'{self._tracefs}/tracing_on', 1)

    def tracing_off(self):
        """
        writes to tracing_on to disable writing to the kernel buffers

        note that this DOES not remove hooks, and can not be used to bypass
        hooks.

        some kits do try to hook this, but it does nothing.
        """
        self._atomic_write(f'{self._tracefs}/tracing_on', 0)

    def setup(self):
        """
        Get ftrace into a state we can trace with, disabling any existing
        tracing going on.
        """
        self.enable()
        self.current_tracer('nop')
        self.write_tracefs('set_ftrace_filter', '')
        self.tracing_on()

    def read_sysctl(self, name):
        cleaned = name.replace('.', '/')
        return self._atomic_read(f'{self._sysctl}/{cleaned}')

    def write_sysctl(self, name, value):
        cleaned = name.replace('.', '/')
        self._atomic_write(f'{self._sysctl}/{cleaned}', value)

    def read_tracefs(self, name):
        return self._atomic_read(f'{self._tracefs}/{name}')

    def write_tracefs(self, name, value):
        self._atomic_write(f'{self._tracefs}/{name}', value)

    def current_tracer(self, name=None):
        if name is not None:
            self.write_tracefs('current_tracer', name)
        else:
            self.read_tracefs('current_tracer')

    def set_option(self, option, value=1):
        """
        set an option
        """
        self.write_tracefs(f'options/{option}', value)

    def function_tracer(self):
        """
        Returns a object to configure the function tracer
        """
        return FunctionTracer(self)

    def touched_functions_raw(self):
        return normalize_lines(self.read_tracefs('touched_functions'))

    def enabled_functions_raw(self):
        return normalize_lines(self.read_tracefs('enabled_functions'))

    def touched_functions(self):
        return [s.split(' ')[0] for s in self.touched_functions_raw()]

    def enabled_functions(self):
        return [s.split(' ')[0] for s in self.enabled_functions_raw()]


class Tracer:
    def __init__(self, ftrace):
        self._ftrace = ftrace

    def set_filter(self, functions):
        for function in functions:
            self._ftrace.write_tracefs('set_ftrace_filter', function)

    def clear_filter(self):
        self._ftrace.write_tracefs('set_ftrace_filter', '\n')

    def enable(self):
        self._ftrace.current_tracer(self.NAME)

    def disable(self):
        self._ftrace.current_tracer('nop')


class FunctionTracer(Tracer):
    NAME = 'function'


class Report:
    """
    Logger to handle the information we generate.
    """
    def __init__(self):
        self._messages = []

    def log(self, message):
        self._messages.append(message)
        print(message, file=sys.stderr)

    def __str__(self):
        return '\n'.join(map(str, self._messages))


class Message:
    """
    Wrapper for test results.

    * test is for the test type we are running
    * message for human readable description
    * extra for extra log info for machine parsing
    """

    def __init__(self, test, msg, extra=None):
        self._test = test
        self._msg = msg
        self._extra = extra

    def __str__(self):
        return f'{self.TYPE} - {self._test} - {self._msg}'


class Detection(Message):
    TYPE = 'DETECTION'

class Anomaly(Message):
    TYPE = 'ANOMALY'

class Info(Message):
    TYPE = 'INFO'

class Error(Message):
    TYPE = 'ERROR'

# just a logger
report = Report()

def assert_root():
    """
    check we have root, else we won't be able to do anything
    """
    assert os.geteuid() == 0


def can_disable_ftrace(ft):
    """
    check if can enable / disable ftrace

    this is a weak test, basic hooks bypass it if they fake the sysctl value.

    we do more advanced functionality tests elsewhere.
    """
    ft.disable()
    if ft.status() != False:
        report.log(Detection('can_disable_ftrace', 'unable to disable ftrace'))
        res = False
    else:
        report.log(Info('can_disable_ftrace', 'able to disable ftrace'))
        res = True
    ft.enable()

    return res


def check_faking_ftrace_disabled(ft):
    """
    Attempt to use the function tracer while ftrace is disabled.

    If we can, got hooks faking the results.
    """
    test_fun = 'run_init_process'
    ft.disable()
    if len(ft.enabled_functions()) > 0:
        report.log(Detection(
            'check_faking_ftrace_disabled',
            'ftrace is disabled but still enabled functions'
            )
        )

    tracer = ft.function_tracer()
    # we assume this function hasn't already been traced
    tracer.set_filter(test_fun)
    tracer.enable()

    enabled = ft.enabled_functions()

    tracer.disable()
    tracer.clear_filter()

    if test_fun in enabled:
        report.log(Detection(
            'check_faking_ftrace_disabled',
            'faking ftrace being disabled')
        )
    else:
        report.log(Info(
            'check_faking_ftrace_disabled',
            'doesnt seem to be faking ftrace being disabled')
        )

    ft.enable()


def sus_touched_functions(ft):
    """
    check for functions that indicate a hooking framework.
    """
    sus_touched = list(
        filter(
            lambda x: x in SUS_FUNCS,
            [func for func in ft.touched_functions()]
        )
    )
    if len(sus_touched) > 0:
        report.log(Detection(
            'sus_touched_functions', 'sus function found' + str(s), s)
        )
    else:
        report.log(Info('sus_touched_functions', 'no sus functions found'))


def try_commonly_hooked(ft):
    """
    Try using ftrace to monitor commonly hooked functions.

    We check enabled_functions to see if they are being hidden or not.
    """
    commonly_hooked = ['__x64_sys_write', '__x64_sys_kill']
    already_enabled = ft.enabled_functions()
    funcs_to_try = []

    for func in commonly_hooked:
        if func not in already_enabled:
            funcs_to_try.append(func)

    if len(funcs_to_try) == 0:
        return []

    tracer = ft.function_tracer()
    tracer.set_filter(funcs_to_try)
    tracer.enable()
    funcs = ft.enabled_functions()
    tracer.disable()

    if len(funcs_to_try) != len(funcs):
        report.log(Detection('try_commonly_hooked', 'filtered functions!'))
    else:
        report.log(Info('try_commonly_hooked', 'no filtered functions'))


def main():
    # we need root
    assert_root()

    # now perform our functionality tests
    ft = Ftrace()
    ft.setup()

    # only want to perform this test if everything hasn't already been traced
    if True:
        s = sus_touched_functions(ft)

    if can_disable_ftrace(ft):
        # perform tests to see if this is being faked
        check_faking_ftrace_disabled(ft)

    try_commonly_hooked(ft)


if __name__ == "__main__":
    main()
