package com.acme.relay;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Starts the real entry point in its own JVM, like an operator would, against the compiled project classes. */
class StartupFailureTest {
    private static final String REQUIRED = """
            upstream.url=https://uplink.example.com/v1/events
            api.token=s3cret
            """;

    @TempDir
    Path dir;

    @Test
    void aBadValueStopsTheServiceBeforeAnyMessageIsProcessed() throws Exception {
        Path config = Files.writeString(dir.resolve("config.properties"), REQUIRED + "worker.threads=4O\n");

        Run run = start(config.toString(), "hello\n");

        assertNotEquals(0, run.exitCode(), "the service must exit with a failure status");
        assertTrue(run.stderr().contains("worker.threads"), "stderr does not name the key: " + run.stderr());
        assertTrue(run.stderr().contains("4O"), "stderr does not show the bad value: " + run.stderr());
        assertNoStackTrace(run);
        assertFalse(run.stdout().contains("hello"), "a message was processed on an invalid configuration");
    }

    @Test
    void aMissingConfigurationFileStopsTheServiceAndNamesTheFile() throws Exception {
        Path missing = dir.resolve("nowhere.properties");

        Run run = start(missing.toString(), "hello\n");

        assertNotEquals(0, run.exitCode(), "the service must exit with a failure status");
        assertTrue(run.stderr().contains("nowhere.properties"), "stderr does not name the file: " + run.stderr());
        assertNoStackTrace(run);
        assertFalse(run.stdout().contains("hello"), "a message was processed without a configuration");
    }

    @Test
    void aValidConfigurationStillRelaysMessages() throws Exception {
        Path config = Files.writeString(dir.resolve("config.properties"), REQUIRED + "worker.threads=2\n");

        Run run = start(config.toString(), "hello\n");

        assertEquals(0, run.exitCode(), "stderr: " + run.stderr());
        assertTrue(run.stdout().contains("hello"), "the message was not relayed: " + run.stdout());
    }

    private static void assertNoStackTrace(Run run) {
        assertFalse(run.stderr().contains("\tat "), "a stack trace is not a clear message: " + run.stderr());
    }

    private Run start(String configFile, String input) throws IOException, InterruptedException {
        String java = ProcessHandle.current().info().command().orElse("java");
        Path stdout = dir.resolve("stdout.txt");
        Path stderr = dir.resolve("stderr.txt");
        Process process = new ProcessBuilder(
                        java, "-cp", Path.of("build", "classes").toAbsolutePath().toString(),
                        "com.acme.relay.Main", configFile)
                .redirectOutput(stdout.toFile())
                .redirectError(stderr.toFile())
                .start();
        process.getOutputStream().write(input.getBytes(StandardCharsets.UTF_8));
        process.getOutputStream().close();
        if (!process.waitFor(60, TimeUnit.SECONDS)) {
            process.destroyForcibly();
            throw new AssertionError("the service did not stop within 60 seconds");
        }
        return new Run(process.exitValue(), Files.readString(stdout), Files.readString(stderr));
    }

    private record Run(int exitCode, String stdout, String stderr) {}
}
