### Known issues

**Release images to DockerHub**

Sometimes release tool `skopeo` hits timeouts. If happens, you may notice
error like following at "_Run publish_" section:

```
time="2025-08-11T09:32:36Z" level=fatal msg="trying to reuse blob sha256:0bdf2c4d1714b5962675435789b4e83edb5aa4d94ec0d7643737940b0e73c4ed at destination: pinging container registry registry-1.docker.io: Get \"https://registry-1.docker.io/v2/\": proxyconnect tcp: dial tcp 10.7.211.16:912: i/o timeout"
```

In such case, you just need to re-run this failed job.
