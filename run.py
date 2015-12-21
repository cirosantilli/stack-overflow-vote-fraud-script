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
import random
import sqlite3
import subprocess
import sys

import common

# Don't do any operations to the Stack Overflow server.
# But do change local database. Used for testing.
dry_run_no_server = False

# Some exit statuses indicate that we should not send a notification email.
exit_status_success = 0
exit_status_404 = 65
exit_status_no_upvote_arrow = 66
# TODO deal with this case by emailing the admin to manually do the CAPTCHA.
exit_status_human_verification = 67
exit_status_cloudfare_attention_required = 68

max_failures_today = 30

vote_not_done_query = 'WHERE vote_time IS NULL AND user_id = ? '

# Switch Tor exit IP.
def new_tor_ip():
    process = subprocess.Popen([
        'sudo',
        'killall',
        '-HUP',
        'tor'
    ])

if len(sys.argv) > 1:
    casperjs_path = sys.argv[1]
else:
    casperjs_path = '/home/ciro/.nvm/v0.10.26/bin/casperjs'

logging.basicConfig(
    filename = os.path.splitext(os.path.realpath(__file__))[0] + '.log',
    level = logging.DEBUG,
    format = '%(asctime)s|%(levelname)s|%(message)s',
)
script_dir = os.path.dirname(os.path.realpath(__file__))
logging.debug(
    'Last git commit SHA = ' +
    subprocess.check_output(['git', '-C', script_dir, 'rev-parse', 'HEAD']))

connection = sqlite3.connect(common.schedule_database_path, timeout=0)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

with open(common.users_csv_path, 'r') as user_file:
    user_csver = csv.reader(user_file)
    for user_row in user_csver:
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
            # We could cache this in a variable, and update it as we do operations.
            # The problem is mass update of 404 questions.
            nvotes_not_done = next(cursor.execute(
                    'SELECT COUNT(*) FROM votes ' +
                    vote_not_done_query,
                    (user_id,)))[0]
            while votes_already_done_today < common.max_votes_per_day:
                if nvotes_not_done == 0:
                    # TODO email admin. Not enough votes on the schedule for this user.
                    logging.warn('Not enough votes scheduled today for user: {}'.format(user_id))
                    break
                # Get one random vote and do it. Not very fast,
                # but I could not find a better way, and network is our bottleneck.
                # An faster alternative would be to read 10k rows and pick 30 from them each time.
                # Less random, but also good enough.
                cursor.execute(
                        'SELECT * FROM votes ' +
                        vote_not_done_query +
                        'ORDER BY id ASC  LIMIT 1 OFFSET ?',
                        (user_id, random.randint(1, nvotes_not_done)))
                vote_row = cursor.fetchone()
                if not dry_run_no_server:
                    # TODO this only logs the row ID, how to log every field?
                    # http://stackoverflow.com/questions/7920284/how-can-printing-an-object-result-in-different-output-than-both-str-and-repr
                    logging.debug('vote = ' + str(tuple(vote_row)))
                    args = [
                        casperjs_path,
                        '--ssl-protocol=any',
                        '--proxy=127.0.0.1:9050',
                        '--proxy-type=socks5',
                        common.vote_script_path,
                        user_email,
                        user_password,
                        user_id,
                        str(vote_row['question_id']),
                        str(vote_row['answer_id']),
                        script_dir
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
                if exit_status == exit_status_cloudfare_attention_required:
                    new_tor_ip()
                else:
                    cursor.execute("""UPDATE votes SET vote_time = ?, script_status = ?
                        WHERE user_id = ? AND answer_id = ?""",
                        (datetime.datetime.utcnow(), exit_status, user_id, vote_row['answer_id']))
                    nvotes_not_done -= cursor.rowcount
                    connection.commit()
                exit_status_msg = 'Exit status = ' + str(exit_status) + '\n'
                if exit_status == exit_status_success:
                    logging.debug(exit_status_msg)
                    votes_already_done_today += 1
                else:
                    # The question gave 404, so just skip all answers for that question.
                    if exit_status == exit_status_404:
                        cursor.execute("""UPDATE votes SET vote_time = ?, script_status = ?
                            WHERE user_id = ? AND question_id = ?""",
                            (datetime.datetime.utcnow(), exit_status_404, user_id, vote_row['question_id']))
                        nvotes_not_done -= cursor.rowcount
                    failures_today += 1
                    logging.error(exit_status_msg)
                    if failures_today >= max_failures_today:
                        break
            if failures_today >= max_failures_today:
                # TODO email admin.
                logging.error('Reached maximum number of failures for this day: {}. Skipping current user: {}'.format(max_failures_today, user_id))
                break
        new_tor_ip()
connection.close()
