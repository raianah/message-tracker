"""
    MIT License

    Copyright (c) 2024 rai

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

from sqlite3 import connect
from os.path import isfile
from apscheduler.triggers.cron import CronTrigger

BUILD_PATH = "./data/db/build.sql"
DB_PATH = "./data/db/database.db"

conn = connect(DB_PATH, check_same_thread=False)

cxn = conn.cursor()

def with_commit(func):
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        commit()

    return inner

@with_commit
def build():
    if isfile(BUILD_PATH):
        scriptexec(BUILD_PATH)

def commit():
    conn.commit()

def autosave(sched):
    sched.add_job(commit, CronTrigger(second=0))

def close():
    cxn.close()

def field(command, *values):
    cxn.execute(command, tuple(values))

    if (fetch := cxn.fetchone()) is not None:
        return fetch[0]

def record(command, *values):
    cxn.execute(command, tuple(values))

    return cxn.fetchone()

def records(command, *values):
    cxn.execute(command, tuple(values))

    return cxn.fetchall()

def column(command, *values):
    cxn.execute(command, tuple(values))
    
    return [item[0] for item in cxn.fetchall()]

def execute(command, *values):
    cxn.execute(command, tuple(values))

def multiexec(command, valueset):
    cxn.executemany(command, valueset)

def scriptexec(path):
    with open(path, "r", encoding="utf-8") as script:
        cxn.executescript(script.read())