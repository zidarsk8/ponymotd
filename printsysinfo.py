#!/usr/bin/env python

import subprocess
import getpass
import socket

MAINTAINER = "Your Name, your@email.com"

colors = {
    "{p}": "\033[0;35m",  # dark purple
    "{w}": "\033[0;37m",  # white
    "{g}": "\033[1;32m"  # green
}


def color(line):
  for name, code in colors.items():
    line = line.replace(name, code)
  return line


def syscall(callstr):
  return subprocess.check_output(callstr, shell=True).decode(
      encoding='UTF-8').strip()


ipArray = {i.strip().split(" ")[-1]: i.strip().split(" ")[1]
           for i in syscall("ip addr | grep 'scope global'").splitlines()}


uptime = syscall("uptime -p 2> /dev/null || uptime")
uptime = uptime.split(",")[0] if "load average" in uptime else uptime

username = getpass.getuser()
kernel = syscall("uname -r")

hostname = socket.gethostname()
cpuinfo = syscall("cat /proc/cpuinfo | "
                  "grep 'model name\s:' | "
                  "head -n 1 | "
                  "sed 's/model name\s: //g'")

meminfo = syscall("cat /proc/meminfo").splitlines()

memdict = {line.split(":")[0]: int(line.replace(
    " kB", "").split(" ")[-1]) // 1024 for line in meminfo}

memall = memdict["MemTotal"]
memfree = memdict["MemFree"] * 100 // memdict["MemTotal"]

lastlogin = syscall(
    "last %s | grep -v 'still logged in' | head -n1" % (username))

lastLoginTime = " ".join(lastlogin.split()[3:7])

release = syscall("lsb_release  -d | sed 's/Description:\s//g'")

if "Arch" in release:
  upgrades = syscall("pacman -Qu |wc -l")
  orphans = syscall("pacman -Qtdq |wc -l")
else:
  upgrades = syscall(
      "/usr/lib/update-notifier/apt-check 2>&1 | cut -d ';' -f 1")

usersLogedIn = syscall("w -h | wc -l")


data = []
np = 25

data.append("{p}%s{w} %s {p}%s" % ("+" * np, "System Data", "+" * np))

data.append("{w}   Hostname {p}= {g}%s" % (hostname))
data.append("{w}     Kernel {p}= {g}%s" % (kernel))
data.append("{w}     Uptime {p}= {g}%s" % (uptime))
data.append("{w}     Memory {p}= {g}%s  ( %s%% Free )" % (memall, memfree))
data.append("{w}        CPU {p}= {g}%s" % (cpuinfo))
[data.append("{w}    Address {p}= {g}%s" % (a))for d, a in ipArray.items()]

data.append("{p}%s{w} %s {p}%s" %
            ("+" * (np + 1), "User Data", "+" * (np + 1)))

data.append("{w}   Username {p}= {g}%s" % (username))
data.append("{w} Last Login {p}= {g}%s" % (lastLoginTime))
data.append("{w}      Users {p}= {g}%s" % (usersLogedIn))

data.append("{p}%s{w} %s {p}%s" % ("+" * np, "Maintenance", "+" * np))

data.append("{w} Maintainer {p}= {g}%s" % (MAINTAINER))
data.append("{w}    Release {p}= {g}%s" % (release))
data.append("{w}   Upgrades {p}= {g}%s packages" % (upgrades))


for line in data:
  print(color(line))
