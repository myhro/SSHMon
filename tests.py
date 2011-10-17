import unittest
import fudge
import sshmon


class SSHmonTests(unittest.TestCase):
    def test_daemonize_is_called_in_right_order(self):
        OSWrapper = fudge.Fake().remember_order()\
                                .expects('perform_first_fork')\
                                .expects('decouple_from_parent_environment')\
                                .expects('perform_second_fork')\
                                .expects('redirect_standard_file_descriptors')
        sshmon.daemonize(OSWrapper)
        fudge.verify()
        fudge.clear_expectations()

    def test_it_should_print_usage_at_incorrect_init(self):
        print_usage = fudge.Fake('print_usage').expects('print_usage')
        print_usage = print_usage.print_usage
        sshmon.print_usage = print_usage
        sshmon.argv = []
        sshmon.main()
        fudge.verify()
        fudge.clear_expectations()

    def test_it_should_stop_when_there_is_stop_on_argv(self):
        stop = fudge.Fake('stop').expects('stop')
        stop = stop.stop
        sshmon.stop = stop
        sshmon.argv = ['sshmon.py','stop']
        sshmon.main()
        fudge.verify()
        fudge.clear_expectations()

    def test_it_should_daemonize_when_applicable(self):
        daemonize_process = fudge.Fake('daemonize_process').expects('daemonize_process')
        daemonize_process = daemonize_process.daemonize_process
        sshmon.daemonize_process = daemonize_process
        sshmon.argv = ['sshmon.py','daemonize']
        sshmon.main()
        fudge.verify()
        fudge.clear_expectations()
        
    def test_it_should_raise_not_changed_exception_when_there_is_no_change(self):
        ssh = sshmon.ssh_monitor()
        ssh.last = 'last'
        ssh.last_log_entry = 'last'
        ssh.previous = 'last'
        try:
            ssh.ensure_it_has_changed_before_procceed()
            self.fail('an exception should be thrown at this point')
        except sshmon.NotChangedException:
            pass

    def test_it_should_send_mail_if_it_was_parsed(self):
        ssh = sshmon.ssh_monitor()
        ssh.parsed = True
        ssh.send_mail = fudge.Fake('send_mail').expects('send_mail').send_mail
        ssh.send_mail_if_login_has_happned()
        fudge.verify()
        fudge.clear_expectations()

if __name__ == '__main__':
    unittest.main()
