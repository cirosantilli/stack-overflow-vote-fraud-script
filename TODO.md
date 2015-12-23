# TODO

-   run multiple exit IPs, one per user, in parallel:

    http://stackoverflow.com/questions/14321214/how-to-run-multiple-tor-processes-at-once-with-different-exit-ips

    We currently use 15 minutes per user, which is manageable for small number of users, but not scalable.

    It would also allow to quickly do all votes even if we turn the computer on for a short time each day.

    Just adding multiple:

        SocksPort 9050
        SocksPort 9052

    to `/etc/tor/torrc` seems to work.

-   Send an email notifications for critical failures:

    - SO are you a robot
    - more than N vote failures in a single day

-   Create an question downvoter just to troll people :-)

-   avoid passing the full casperjs path to the root user.

    The problem is that is is installed with NVM.

    - anacron runs as root
    - `sudo -u USER` messes with `PATH`... no matter what I do:
        - comment out `env_reset` and `secure_path` from `/etc/sudoers` does not help
        - <http://unix.stackexchange.com/questions/55037/can-i-get-correct-path-when-executing-sudo-u-db2inst-sh-db2>
        - <http://stackoverflow.com/questions/21215059/cant-use-nvm-from-root-or-sudo>
    - `sudo su && nmp instsall casper` fails

    The only thing that did work so far was giving it the full path to `casperjs` when running from anacron.

-   run anacron as UTC time: <http://askubuntu.com/questions/54364/how-do-you-set-the-timezone-for-crontab>

-   detect locked posts on the dump or crawler, e.g.: http://stackoverflow.com/questions/871/why-is-git-better-than-subversion/873

    Skip all answers to those, as we already do with deleted questions.

    TODO how? The only way on the dump (better) seems to look at the question history. ugly.

-   Unit tests. This would require mocking SO...

-   Reuse a schedule across many users.

    Schedulers then just say how many users will use a given schedule.

    Not too important, would just save some memory, and would be harder to say who voted what, as votes would have to be in random order.
