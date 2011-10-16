import fudge
import sshmon

def test_daemonize_is_called_in_right_order():
    OSWrapper = fudge.Fake().remember_order()\
                            .expects('perform_first_fork')\
                            .expects('decouple_from_parent_environment')\
                            .expects('perform_second_fork')\
                            .expects('redirect_standard_file_descriptors')
    sshmon.oswrapper = OSWrapper
    sshmon.daemonize()
    fudge.verify()
