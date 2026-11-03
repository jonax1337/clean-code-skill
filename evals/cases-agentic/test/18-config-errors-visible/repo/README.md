# relay

A small service that reads messages from standard input and forwards each one to an upstream endpoint, with a
bounded work queue, a worker pool and retries. In this checkout the upstream is simulated by printing the
request to standard output.

## Running

    cp config.example.properties config.properties
    java tools/RunTests.java                       # compiles into build/classes first
    java -cp build/classes com.acme.relay.Main config.properties < messages.txt

Without an argument the service reads `config.properties` from the working directory.

## Configuration

| Key                  | Required | Default | Meaning                                                     |
|----------------------|----------|---------|-------------------------------------------------------------|
| `upstream.url`       | yes      |         | URL the messages are forwarded to                           |
| `api.token`          | yes      |         | Token sent to the upstream                                  |
| `worker.threads`     | no       | `4`     | Number of delivery threads, at least 1                      |
| `queue.capacity`     | no       | `1000`  | Messages waiting for a free worker, at least 1              |
| `retry.max-attempts` | no       | `3`     | Retries after the first failed delivery, 0 or more          |
| `request.timeout`    | no       | `30s`   | Time limit per delivery: a whole number plus `ms`, `s`, `m` |
| `metrics.enabled`    | no       | `false` | `true` or `false`: print delivery counts on shutdown        |

## Tests

    java tools/RunTests.java

The runner compiles `src/main/java` and `src/test/java` and runs every JUnit 5 test. It needs
`lib/junit-platform-console-standalone.jar`.
