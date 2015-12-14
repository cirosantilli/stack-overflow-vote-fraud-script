# TODO

-   Send an email notification if voting fails.

    Sometimes, Stack Overflow asks you if you are not a robot out of the blue if it notices a weird voting pattern, and asks you to solve a CAPTCHA.

    This will break our script.

    A way to mitigate this is to generate an email notification so that we can intervene manually.

    Of course, there is a limit to how much SO can do this, or real users will be too much annoyed.

    They URL seems to be fixed at:

    - <http://stackoverflow.com/captcha>

    Related threads:

    - <http://meta.stackoverflow.com/questions/302980/why-stack-overflow-repeatedly-asks-me-if-im-a-robot>
    - <http://meta.serverfault.com/questions/854/why-does-serverfault-as-well-as-stackoverflow-etc-asks-for-captcha-so-often>
    - <http://meta.stackexchange.com/questions/143455/i-am-not-a-robot>
    - <http://meta.stackexchange.com/questions/153561/human-verification-page-not-loading-in-china>
    - <http://meta.stackexchange.com/questions/2167/increase-captcha-threshold-for-post-editing>
    - <http://meta.stackexchange.com/questions/1343/how-often-do-captchas-appear>
    - <http://meta.stackexchange.com/questions/244638/please-use-the-new-recaptcha-on-the-human-verification-dialog>
    - <http://meta.stackexchange.com/questions/113974/are-there-some-tips-to-skip-the-human-check>
    - <http://meta.stackoverflow.com/questions/281597/how-do-you-answer-the-human-verification>
    - <http://meta.stackoverflow.com/questions/294480/why-is-human-verification-required-to-do-a-search>
    - <http://meta.stackexchange.com/questions/253524/why-am-i-being-redirected-to-a-captcha-when-i-am-just-searching/253526#253526>

-   Create an question downvoter just to troll people :-)

-   Reuse a schedule across many users.

    Schedulers then just say how many users will use a given schedule.

    `run.py` then just randomizes the schedule to avoid correlation between puppets. 

    It is hard to select N random rows from SQL, so we could just read 1000 rows at some random position to memory, and pick 30 randomly.

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

    TODO how? The only way seems to look at the question history. ugly.

-   Unit tests. This would require mocking SO.
