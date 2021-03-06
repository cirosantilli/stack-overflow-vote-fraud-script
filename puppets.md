# Puppets

This discusses how to bootstrap sockpuppets, which is for now the hardest part, as we must get 15 reputation to start voting.

## users.csv

Store your puppets at: [users.csv](users.csv).

You can use the starting template:

    cp users.csv.sample users.csv

The format is documented there.

## Use Tor

Our script uses Tor automatically, so you don't have to worry about it when running.

But in order to:

- bootstrap puppets
- debug the script, specially to see if puppets votes were actually done under https://stackoverflow.com/users/UID/userUID?tab=votes

use the Tor browser all the time, or else Stack Overflow might block your IP some day!

Never access the profile of puppet with another puppet or with you main account. Use <http://tor.stackexchange.com/a/9256/7651> to do it.

Remember that the Tor browser uses a different exit IP than the ones from our runner script. So for example you might get a CloudFare block there (which you should unblock with the CAPTCHA), but not on the script at a given time.

Also consider setting:

- Tor browser to remember browsing history and passwords to speed things up
- multiple Tor browsers with different IPs one for each user: <http://tor.stackexchange.com/questions/2006/how-to-run-multiple-tor-browsers-with-different-ips>

## Helper to generate random logins

    randlog () {
      (
        cat /dev/urandom | tr -dc 'a-z0-9' | head -c 10
        echo
        cat /dev/urandom | tr -dc 'a-zA-Z0-9' | head -c 10 | tr -d '\n'
        echo '0@'
        ) | tee >(xclip -selection clipboard)
    }

Using those logins, create an email, and an account on Stack Overflow

## Email providers

Try to use different email providers.

Make a list of providers that don't ask for cell phone confirmation, and iterate through them.

Note that most large providers are asking for a cell phone today, so look for more obscure or security focused ones.

## Bootstrapping

### Trivial edits

This is likely the best manual approach on Stack Overflow.

I'm not the first to come up with this: <http://meta.stackoverflow.com/questions/268267/suspicious-users-found-active-only-one-day-many-upvotes-cast>

It does not work on all websites. E.g. <http://gamedev.stackexchange.com/> in 2016 rejects supertag / indentation / thanks removal.

With some training, you can create one puppet every 10 minutes.

Edits to make:

-   add title to bare links. TODO query. Or possibly just go over all posts of an user with many posts who is willing to accept them?

    Example: <http://web.archive.org/web/20180415101049/https://unix.stackexchange.com/users/273376/drakonoved?tab=activity>

-   supertag e.g. `python` to `django`

    Query: <http://data.stackexchange.com/stackoverflow/query/edit/392827> Monday 13h GMT, looked at 16 posts, edited 15, added python supertag only + obvious fixes, took 5 minutes, got bootstraped after 15 minutes, stabilized at 27 rep.

    This is my preferred approach so far.

-   profanity: <http://data.stackexchange.com/stackoverflow/query/edit/392580>

-   remove hello and thanks

-   remove unneeded extra indent level of code blocks

-   make title into question

-   multiline inline code:

    `asdf qwer
    asdf qwer`

-   block quotes where code block should be used

-   Using raw HTML where a Markdown element exists;

    - `<br/>`
    - `<pre/>`
    - `<code/>`

-   Trailing space line breaks for code formatting:

        line1<space><space>
        line2<space><space>

-   Greetings:

        OR p.Body LIKE '%i am new to%'
        OR p.Body LIKE '%i have a question%'
        OR p.Body LIKE '%here is my problem%'
        OR p.Body LIKE '%please help%'
        OR p.Body LIKE '%any help?%'
        OR p.Body LIKE '%any ideas?%'
        OR p.Body LIKE '%I wanted to know%'
        OR p.Body LIKE '%I want to know%'
        OR p.Body LIKE '%I wanted to ask%'
        OR p.Body LIKE '%I want to ask%'
        /* This one shold be searched for in titles. */
        OR p.Body LIKE '%I_m wondering if%'
        OR p.Body LIKE '%I wonder if%'
        OR p.Body LIKE '%I have no idea how to do that%'

-   Meaningless title keywords: <http://data.stackexchange.com/stackoverflow/query/edit/404116>

#### How to use the database queries

Save the query output as HTML, and open them on the Tor browser with your puppet.

Control click to open one link per tab, and happy editing!

##### Process SVG from data query

You might also want to download the SVG from the data query and then transform it into HTML like this:

    cat "$(ls -t QueryResults* | head -1)" | tr -d '\r' | \
    sed -E \
    -e 's|,.*||' \
    -e 's|"||g' \
    -e 's|^|<a href="https://stackoverflow.com/questions/|' \
    -e 's|$|">aaaaaaaaaaaaaaaaaaa</a><br/>|' \
    -e '0~16s|$|<br/>|' \
    > a.html

### More automatic methods

This would be the holy grail of vote fraud.

If we could have infinitely many puppets, then any resistance from SO would be impossible.

One possibility would be to mass scrap questions from other Q&A websites. TODO: link back to where I saw this proposed on Meta.

This script currently exists to make it possible to profit from the intermediate state where one can generate a limited number of puppets (tens).
