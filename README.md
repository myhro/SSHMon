SSH Monitor
===========

A daemon that watches all SSH/SFTP login entries on the authentication log (usually `/var/log/auth.log`) and e-mail them to yourself. It works like a very simple intrusion detection system, informing you about any successful logins on your SSH server. Written entirely in Python, you just need:

* A Linux box (maybe anything *NIX, but was tested only on Linux) running a SSH server (OpenSSH or Dropbear).
* Python 2.x (it was developed on the 2.6.6 release, but will probably run on anything higher than Python 2.4)
* Read access to /var/log/auth.log (you didn't though you could analyse the log without reading it, didn't you?)
* Write access to /var/run/ (to be able to terminate it's execution through 'stop' command)
* Local SMTP server (like Exim or Sendmail)

## Installation and Usage

Just put the `sshmon.py` file anywhere you want, run with:

    python sshmon.py destination@email.com

And forget it. You don't have to do anything after that, just wait your e-mails to arrive. It is also possible to run it every boot by putting the same command on the `/etc/rc.local`.

If you want to stop it, type:

    python sshmon.py stop

## License

The source code is licensed under the GNU General Public License Version 2 (GPLv2). It is available in both [HTML](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html) and [TXT](https://www.gnu.org/licenses/gpl-2.0.txt) formats.

## Author

Tiago "Myhro" Ilieve

The `daemonize()` function was adapted from the book "Python for Unix and Linux System Administration" by Noah Gift and Jeremy Jones.
