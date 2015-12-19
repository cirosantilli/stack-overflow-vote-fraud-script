#!/usr/bin/env python

"""
Execute the voting schedule for today.

The schedule is stored in the `common.schedule_database_path` sqlite3 database,
which is generated by other scripts beforehand.

Executes the maximum 30 votes that haven't been done yet for each user,
and mark them as done in the schedule database.

This should be run at least once every day.

There is not problem if you run it more than once a day.

This can be run as a cron job. All output is logged to a file.

Consider using anacron for the job:
http://serverfault.com/questions/52335/job-scheduling-using-crontab-what-will-happen-when-computer-is-shutdown-during
which will work as soon as you turn on your computer.

You can interrupt this script with Ctrl + C
and restart it later on without problems.

Only answer uptvoting is currently supported.
"""

import csv
import datetime
import logging
import os.path
import sqlite3
import subprocess
import sys
import threading

import common

# Don't do any operations to the Stack Overflow server.
# But do change local database. Used for testing.
dry_run_no_server = False

# Some exit statuses indicate that we should not send a notification email.
exit_status_success = 0
exit_status_404 = 65
exit_status_no_upvote_arrow = 66
exit_status_human_verification = 67
exit_status_cloudfare_attention_required = 68

max_failures_today = 30

# Switch Tor exit IP.
# TODO: make this specific for one of the ports. Doing for all has the following downsides:
# - we usually do this to escape CloudFare. But if we change all IPs, it is likely that another one will also break CloudFare, and we'd have to change again.
# - TODO does this happen? Ongoing connections might get closed and lost.
# To do it, I think we can to use multiple torrc files via a template as explained at:
# http://stackoverflow.com/a/18895491/895245
# We should start them one in each thread, and then use `process.send_signal(signal.SIGHUP)` to change the port.
def new_tor_ip():
    process = subprocess.Popen([
        'sudo',
        'killall',
        '-HUP',
        'tor'
    ])
first_tor_port = 9052
if len(sys.argv) > 1:
    casperjs_path = sys.argv[1]
else:
    casperjs_path = '/home/ciro/.nvm/v0.10.26/bin/casperjs'

# Is thread safe: http://stackoverflow.com/questions/2973900/is-pythons-logging-module-thread-safe
logging.basicConfig(
    filename = os.path.splitext(os.path.realpath(__file__))[0] + '.log',
    level = logging.DEBUG,
    format = '%(asctime)s|%(levelname)s|%(message)s',
)
current_dir = os.path.dirname(os.path.realpath(__file__))

class UserVotesThread(threading.Thread):
    # Do one connection per thread:
    # http://stackoverflow.com/questions/1680249/how-to-use-sqlite-in-a-multi-threaded-application
    # http://stackoverflow.com/questions/22739590/how-to-share-single-sqlite-connection-in-multi-threaded-python-application
    # If DB locking gets too intense, we could make on DB file per user.
    # http://stackoverflow.com/questions/1365265/on-localhost-how-to-pick-a-free-port-number
    connection = sqlite3.connect(common.schedule_database_path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    def __init__(self, user_row, tor_port):
        super(SummingThread, self).__init__()
        self.user_row = user_row
        self.tor_port = tor_port
    def run(self):
        logging.debug('user = ' + str(user_row))
        user_id, user_email, user_password = user_row
        if user_id != common.user_id_off:
            # TODO if we start running at midnight, we would overestimate the amount of votes used.
            # We could calculate this every time after a vote to increase precision.
            now = datetime.datetime.utcnow()
            today_midnight = datetime.datetime(year=now.year, month=now.month, day=now.day)
            tomorrow_midnight = today_midnight + datetime.timedelta(days=1)
            failures_today = 0
            votes_already_done_today = next(cursor.execute(
                    'SELECT COUNT(*) FROM votes ' +
                    'WHERE user_id = ? AND vote_time >= ? AND vote_time < ? AND script_status = ?',
                    (user_id, today_midnight, tomorrow_midnight, exit_status_success)))[0]
            logging.debug('votes_already_done_today = ' + str(votes_already_done_today))
            while votes_already_done_today < common.max_votes_per_day:
                desired_nvote_fetches = common.max_votes_per_day - votes_already_done_today
                cursor.execute(
                        'SELECT * FROM votes ' +
                        'WHERE vote_time IS NULL AND user_id = ? ' +
                        'ORDER BY id ASC LIMIT ?',
                        (user_id, desired_nvote_fetches))
                # Trying to iterate the cursor is problematic because we are going go update rows as well.
                # So we just fetch all to memory and be done with it.
                # Should fit, since we are limited to just a few votes every day.
                vote_rows = cursor.fetchall()
                actual_nvote_fetches = len(vote_rows)
                questions_404 = set()
                for vote_row in vote_rows:
                    if vote_row['question_id'] not in questions_404:
                        if not dry_run_no_server:
                            # TODO this only logs the row ID, how to log every field?
                            # http://stackoverflow.com/questions/7920284/how-can-printing-an-object-result-in-different-output-than-both-str-and-repr
                            logging.debug('vote = ' + str(tuple(vote_row)))
                            args = [
                                casperjs_path,
                                '--ssl-protocol=any',
                                '--proxy=127.0.0.1:' + self.tor_port,
                                '--proxy-type=socks5',
                                common.vote_script_path,
                                user_email,
                                user_password,
                                user_id,
                                str(vote_row['question_id']),
                                str(vote_row['answer_id']),
                                current_dir
                            ]
                            logging.debug('command = ' + ' '.join(args))
                            process = subprocess.Popen(
                                args,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE,
                            )
                            stdout, stderr = process.communicate()
                            logging.debug('stdout = \n' + stdout.rstrip())
                            if stderr:
                                logging.error('stderr = \n' + stderr.rstrip())
                            exit_status = process.wait()
                        else:
                            exit_status = 0
                        # TODO deal with different script exit statuses. E.g:
                        # - if question deleted or no upvote arrow, schedule more votes for today
                        # - if human verification, stop voting with this user, and send an email to admin
                        cursor.execute("""UPDATE votes SET vote_time = ?, script_status = ?
                            WHERE user_id = ? AND answer_id = ?""",
                            (datetime.datetime.utcnow(), exit_status, user_id, vote_row['answer_id']))
                        connection.commit()
                        exit_status_msg = 'Exit status = ' + str(exit_status) + '\n'
                        if exit_status == exit_status_success:
                            logging.debug(exit_status_msg)
                            votes_already_done_today += 1
                        else:
                            # The question gave 404, so just skip all answers for that question.
                            if exit_status == exit_status_404:
                                questions_404.add(vote_row['question_id'])
                                cursor.execute("""UPDATE votes SET vote_time = ?, script_status = ?
                                    WHERE user_id = ? AND question_id = ?""",
                                    (datetime.datetime.utcnow(), exit_status_404, user_id, vote_row['question_id']))
                            elif exit_status == exit_status_cloudfare_attention_required:
                                # TODO: also redo the last vote, or and keep changing tor node until it leaves this state.
                                new_tor_ip()
                            failures_today += 1
                            logging.error(exit_status_msg)
                            if failures_today == max_failures_today:
                                # TODO email admin.
                                logging.error('Reached maximum number of failures for this day {}. Skipping current user.'.format(max_failures_today))
                                break
                if actual_nvote_fetches < desired_nvote_fetches:
                    # TODO email admin. Not enough votes on the schedule for this user.
                    logging.warn('Not enough votes scheduled for this user for today.')
                    break
        connection.close()

with open(common.users_csv_path, 'r') as user_file:
    user_csv = csv.reader(user_file)
    threads = []
    for i, user_row in user_csv:
        t = UserVotesThread(user_row, first_tor_port + i)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
