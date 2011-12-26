# -*- coding: utf-8 -*-
#!/usr/bin/env python

from os import chdir, dup2, fork, getpid, path, setsid, system, umask
from smtplib import SMTP
from socket import gethostname
from string import join
from sys import argv, exit, stderr, stdin, stdout
from time import sleep


def daemonize(newstdin='/dev/null', newstdout='/dev/null',
              newstderr='/dev/null'):
    # Perform first fork.

    try:
        pid = fork()
        if pid > 0:
            exit(0)  # Exit first parent.
    except OSError, e:
        stderr.write("Fork #1 failed: ({0}) {1}\n".format(e.errno, e.strerror))
        exit(1)
    # Decouple from parent environment.
    chdir("/")
    umask(0)
    setsid()
    # Perform second fork.
    try:
        pid = fork()
        if pid > 0:
            exit(0)  # Exit second parent.
    except OSError, e:
        stderr.write("Fork #2 failed: ({0}) {1}\n".format(e.errno, e.strerror))
        exit(1)
    # The process is now daemonized, redirect standard file descriptors.
    for f in stdout, stderr:
        f.flush()
    si = file(newstdin, 'r')
    so = file(newstdout, 'a+')
    se = file(newstderr, 'a+', 0)
    dup2(si.fileno(), stdin.fileno())
    dup2(so.fileno(), stdout.fileno())
    dup2(se.fileno(), stderr.fileno())


def ssh_monitor():
    # Keep track of the time of the last login.
    last = ''
    previous = ''
    # In the first iteration, it will only read the file and do nothing.
    parsed = False
    # Runs forever...
    while True:
        # Line counter.
        i = 0
        ''' Read the authentication log file.
        This is done in a reverse way so it won't need to read
        the whole file every time, only the new entries.
        '''
        logfile = reversed(open('/var/log/auth.log', 'r').readlines())
        for line in logfile:
            # Check if the current line is about a OpenSSH or Dropbear login.
            if ('sshd' in line and 'Accepted' in line
                or 'dropbear' in line and 'succeeded' in line):
                # Get the time of log entry (hours:minutes:seconds).
                compare = line.split()[2]
                ''' If it is equal to one of the last two entries,
                the file hasn't changed.
                '''
                if last == compare or previous == compare:
                    break
                # If is the first line, switch the records of last two entries.
                if i == 0:
                    previous, last = last, compare
                ''' If the file was read at least once and the loop got here,
                it means that at least one login happened during the execution
                of SSH Monitor. That entry is e-mailed (through a local SMTP
                daemon) to the address specified as argument when the program
                was called from the command line.
                '''
                if parsed:
                    email = {
                        'from': 'sshmonitor@{0}'.format(gethostname()),
                        'to': argv[1],
                        'subj': 'SSH Login on {0}'.format(gethostname()),
                        'text': line
                    }
                    email['body'] = join((
                        'From: {0}'.format(email['from']),
                        'To: {0}'.format(email['to']),
                        'Subject: {0}'.format(email['subj']),
                        '',
                        email['text']),
                        '\n'
                    )
                    smtp = SMTP('localhost')
                    smtp.sendmail(email['from'], email['to'], email['body'])
                    smtp.quit()
                    del email
                    del smtp
                # Line counter iteration.
                i += 1
        # Mark the file as "read".
        parsed = True
        # Wait for ten seconds to do it again.
        sleep(10)


def main():
    ''' The program can't be called without an argument (or more than one).
    A little 'help' is displayed.
    '''
    if len(argv) != 2:
        print '-' * 15 + '\n- SSH Monitor -\n' + '-' * 15
        print '''\nUsage:\n\tTo run: python {0} email@example.com
                \tTo end: python {0} stop'.format(argv[0])
              '''
        exit(1)
    elif argv[1] == 'stop':
        ''' If the argument is 'stop', it will check for the existence of
        the pid file, read it and kill the process.
        '''
        if path.isfile('/var/run/sshmon.pid'):
            runfile = open('/var/run/sshmon.pid', 'r')
            procpid = runfile.readline()
            runfile.close()
            system('kill -15 {0}'.format(procpid))
            system('rm /var/run/sshmon.pid')
        # If the file doesn't exists, it is not running.
        else:
            print 'Are you sure it is running?'
    else:
        ''' Daemonizes the process, so it won't need any terminal and
        runs truly in the background.
        '''
        daemonize()
        ''' Record the current process pid in a file, so it could be
        killed later.
        '''
        runfile = open('/var/run/sshmon.pid', 'w')
        runfile.write(str(getpid()))
        runfile.close()
        # Parses the authentication log and send an e-mail for every login.
        ssh_monitor()

if __name__ == "__main__":
    main()
