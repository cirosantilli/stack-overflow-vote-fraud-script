# Features

1.  Tips to manually bootstrap 1 new puppet in 10 minutes
1.  [CasperJS](https://github.com/n1k0/casperjs) (headless browser) + [data dump](https://archive.org/details/stackexchange) based to overcome API limitations
1.  Use Tor get multiple IPs, one per puppet
1.  Run puppets in parallel, and thus quickly (10 minutes min, but longer recommended to improve camouflage)
1.  Deal with some cases of the outdated data dump: e.g. skip all answers of questions deleted after the dump
1.  Deal with CloudFare blocked IP by changing IP (common case for Tor IPs...)
1.  Randomized some parameters to increase camouflage, e.g. voting intervals
1.  Run well on background and as cronjobs:
    1.  Log everything to files, never stdout
    1.  Script is idempotent on a given UTC day
    1.  Email admin in case of critical failures
