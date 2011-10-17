from os import chdir, dup2, fork, getpid, path, setsid, system, umask

class OSWrapper(object):
    def perform_first_fork():
        try:
            pid = fork()
            if pid > 0:
                exit(0) 
        except OSError, e:
            stderr.write("Fork #1 failed: ({0}) {1}\n".format(e.errno, e.strerror))
            exit(1)

    def decouple_from_parent_environment():
        chdir("/")
        umask(0)
        setsid()

    def perform_second_fork():
        try:
            pid = fork()
            if pid > 0:
                exit(0)
        except OSError, e:
            stderr.write("Fork #2 failed: ({0}) {1}\n".format(e.errno, e.strerror))
            exit(1)

    def redirect_standard_file_descriptors():
        for f in stdout, stderr: f.flush()
        si = file(newstdin, 'r')
        so = file(newstdout, 'a+')
        se = file(newstderr, 'a+', 0)
        dup2(si.fileno(), stdin.fileno())
        dup2(so.fileno(), stdout.fileno())
        dup2(se.fileno(), stderr.fileno())

