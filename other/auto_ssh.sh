#!/usr/bin/expect -f

set user [lindex $argv 0]
set host [lindex $argv 1]
set pwd [lindex $argv 2]

set timeout 3

spawn ssh-copy-id -i /root/.ssh/id_rsa.pub ${user}@${host}

expect {
  "(yes/no)?" {
    send "yes\r"
    exp_continue
  }
  "password:" {
    send_user "${pwd}"
    send "${pwd}\n"
    exp_continue
  }
  eof {
    send_user "eof"
  }
}
