# Getting started

1.  Ubuntu 15.10 dependencies:

        mkdir -p cookies
        sudo apt-get intall phantomjs torsocks sqlite3
        curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.29.0/install.sh | bash
        VERSION='0.10.26'
        curl 'https://raw.githubusercontent.com/creationix/nvm/v0.7.0/install.sh' | sh
        # WARNING: fails with `-eu`.
        . "$HOME/.nvm/nvm.sh"
        echo '. "$HOME/.nvm/nvm.sh"
        nvm use "'"$VERSION"'" &>/dev/null
        ' >> "$HOME/.bashrc"
        nvm install "$VERSION"
        npm install -g casperjs

1.  Download and extract `Posts.xml` from <https://archive.org/details/stackexchange>

    Note: this data may be old: <http://meta.stackexchange.com/questions/264565/when-was-the-last-data-dump-uploaded-to-archive-org>

1.  Generate `dump.sqlite3`:

        ./xml_to_sqlite.py

1.  Update `schedule.sqlite3` with the voting strategy of your choice:

        ./schedule_XXX.py

    E.g.:

        ./schedule_all_answers.py

    This is just a dummy test voting strategies.

    The hard and interesting part is to create a voting schedule that gives one chosen user way more rep than others, while dodging the fraud detection script.

    See: [schedule](schedule.md) for tips on how to build your own.

1.  Generate a `users.csv` with your bootstrapped sockpuppets. [More information](puppets.md).

1.  Do today's votes:

        ./run.py

    To lay back and do that automatically every day when you turn on the computer, add:

        1 0 sofraud /home/ciro/bak/git/stack-overflow-vote-fraud-script/run.py /home/ciro/.nvm/v0.10.26/bin/casperjs >>/var/log/anacron-sofraud 2>&1

    to your `/etc/anacrontab`.
