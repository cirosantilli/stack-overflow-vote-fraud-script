# TODO

-   Do randomly less votes than exactly 30 per day to make it harder to spot puppets.

-   Create a script that generates good random email password pairs with random lengths between 8 - 12 to help people bootstrap.

-   Create an question downvoter just to troll people :-) 125 rep needed.

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

    TODO how? The only way on the dump seems to be to look at the question history. ugly.

-   Unit tests. This would require mocking SO...
