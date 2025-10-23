# Coverity Workflow supply

This directory contains Coverity configuration and toolbox when need to debug.

### Toolbox howto build and run

To make things fast, there is a "Dockerscript" that combines docker and bash scripting
via executing all coverity actions on build.

To run the scans and generate report:

```bash
$ cd debug-toolbox
$ cp .env.example .env
$ vim .env  # fill secrets
$ chmod +x build.sh
$ ./build.sh
```

To extract the report from container:

```bash
(terminal 1) $ docker run -it --rm --name cov-test cov-test
(terminal 2) $ docker cp cov-test:/ipas/Scripts/github_actions/ipas_report/report/output.html .
(terminal 1) $ <Ctrl> - <D>
```

### Dev's side notes

When docker container is being built, is uses `buildkit` as a hostname. It propagates to
/repo/idir/emit/buildkit, taken from host name. But when container is run, hostname
is random sha and coverity complaints about it when you try to run
scan after turning on container.
Workaround it so to run container with overriden hostname:
```bash
docker run -it --hostname buildkitsandbox cov-test
```
