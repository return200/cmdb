#!/usr/bin/expect -f

set user [lindex $argv 0]
set host [lindex $argv 1]
set pwd [lindex $argv 2]

set timeout 3

spawn ssh ${user}@${host}

expect {
  "yes/no" {send "${pwd}\n"}
}

expect {
  "password:" {send "${pwd}\n"}
}

expect eof


