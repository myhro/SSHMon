# -*- coding: utf-8 -*-
#!/usr/bin/env python

from os import chdir, dup2, fork, getpid, path, setsid, system, umask
from smtplib import SMTP
from socket import gethostname
from string import join
from sys import argv, exit, stderr, stdin, stdout
from time import sleep
from oswrapper import OSWrapper

def daemonize(oswrapper = OSWrapper(),newstdin = '/dev/null', newstdout = '/dev/null', newstderr = '/dev/null'):
    oswrapper.perform_first_fork()
    oswrapper.decouple_from_parent_environment()
    oswrapper.perform_second_fork()
    oswrapper.redirect_standard_file_descriptors(newstdin, newstdout, newstderr)


class NotChangedException(RuntimeError):
    pass

class ssh_monitor(object):
    # Keep track of the time of the last login.
    last = ''
    previous = ''
    #do nothing at first interation
    parsed = False
    line_counter = 0

    def run(self):
        while True:
            try:
                self.loop()
            except NotChangedException:
                break

    def loop(self):
        logfile = self.read_auth_logfile()
        for line in logfile:
            if self.is_openssh_or_dropbear_login(line):
                self.last_log_entry = line.split()[2]
                self.ensure_it_has_changed_before_procceed()
                self.switch_records()
                self.send_mail_if_login_has_happned()
                self.line_counter += 1
        self.parsed = True
        sleep(10)

    def ensure_it_has_changed_before_procceed(self):
        if self.last == self.last_log_entry or self.previous == self.last_log_entry:
            raise NotChangedException() 

    def switch_records(self):
        if self.line_counter == 0:
            self.previous, self.last = self.last, self.compare

    def send_mail_if_login_has_happned(self):
        if self.parsed:
            self.send_mail()


    def read_auth_logfile(self):
        """
        This is done in a reverse way so it won't need to read the whole file every 
        time, only the new entries.
        """
        return reversed(open('/var/log/auth.log', 'r').readlines())

    def is_openssh_or_dropbear_login(self, line):
        return 'sshd' in line and\
                'Accepted' in line or\
                'dropbear' in line and\
                'succeeded' in line

    def send_mail(self):
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

def main():
    # The program can't be called without an argument (or more than one). A little 'help' is displayed.
    if len(argv) != 2:
        print_usage()
    elif argv[1] == 'stop':
        stop()
    else:
        daemonize_process()

def print_usage():
    print '-' * 15 + '\n- SSH Monitor -\n' + '-' * 15
    print '\nUsage:\n\tTo run: python {0} email@example.com\n\tTo end: python {0} stop'.format(argv[0])
    exit(1)

def stop():
    # If the argument is 'stop', it will check for the existence of pid file, 
    # read it and kill the process. 
    if path.isfile('/var/run/sshmon.pid'):
        runfile = open('/var/run/sshmon.pid', 'r')
        procpid = runfile.readline()
        runfile.close()
        system('kill -15 {0}'.format(procpid))
        system('rm /var/run/sshmon.pid')
    # If the file doesn't exists, it is not running.
    else:
        print 'Are you sure it is running?'

def daemonize_process():
    # Daemonizes the process, so it won't need any terminal and runs truly in the background.
    daemonize()
    # Record the current process pid in a file, so it could be killed later.
    runfile = open('/var/run/sshmon.pid', 'w')
    runfile.write(str(getpid()))
    runfile.close()
    # Parses the authentication log and send an e-mail for every login.
    ssh_monitor().run()

if __name__ == "__main__": main()
