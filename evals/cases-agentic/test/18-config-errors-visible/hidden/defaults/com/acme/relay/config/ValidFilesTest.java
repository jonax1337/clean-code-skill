package com.acme.relay.config;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.net.URI;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class ValidFilesTest {
    private static final String REQUIRED = """
            upstream.url=https://uplink.example.com/v1/events
            api.token=s3cret
            """;

    @TempDir
    Path dir;

    @Test
    void aFileWithOnlyTheRequiredKeysUsesTheDocumentedDefaults() throws IOException {
        ServiceConfig config = ConfigLoader.load(write(REQUIRED));

        assertEquals(URI.create("https://uplink.example.com/v1/events"), config.upstream());
        assertEquals("s3cret", config.apiToken());
        assertEquals(4, config.workerThreads());
        assertEquals(1000, config.queueCapacity());
        assertEquals(3, config.retryAttempts());
        assertEquals(Duration.ofSeconds(30), config.requestTimeout());
        assertFalse(config.metricsEnabled());
    }

    @Test
    void eachOptionalKeyCanBeLeftOutOnItsOwn() throws IOException {
        String full = REQUIRED + """
                worker.threads=8
                queue.capacity=250
                retry.max-attempts=0
                request.timeout=500ms
                metrics.enabled=true
                """;

        ServiceConfig withoutWorkers = ConfigLoader.load(write(full.replace("worker.threads=8\n", "")));
        ServiceConfig withoutQueue = ConfigLoader.load(write(full.replace("queue.capacity=250\n", "")));
        ServiceConfig withoutRetries = ConfigLoader.load(write(full.replace("retry.max-attempts=0\n", "")));
        ServiceConfig withoutTimeout = ConfigLoader.load(write(full.replace("request.timeout=500ms\n", "")));
        ServiceConfig withoutMetrics = ConfigLoader.load(write(full.replace("metrics.enabled=true\n", "")));

        assertEquals(4, withoutWorkers.workerThreads());
        assertEquals(250, withoutWorkers.queueCapacity());
        assertEquals(1000, withoutQueue.queueCapacity());
        assertEquals(8, withoutQueue.workerThreads());
        assertEquals(3, withoutRetries.retryAttempts());
        assertEquals(Duration.ofSeconds(30), withoutTimeout.requestTimeout());
        assertEquals(0, withoutTimeout.retryAttempts());
        assertFalse(withoutMetrics.metricsEnabled());
        assertEquals(Duration.ofMillis(500), withoutMetrics.requestTimeout());
    }

    @Test
    void aFullFileLoadsExactlyAsBefore() throws IOException {
        Path file = write("""
                # relay configuration

                upstream.url = https://uplink.example.com/v1/events
                api.token=s3cret
                worker.threads=8 \s
                queue.capacity=250
                retry.max-attempts=0
                request.timeout=2m
                metrics.enabled=True
                """);

        ServiceConfig config = ConfigLoader.load(file);

        assertEquals(URI.create("https://uplink.example.com/v1/events"), config.upstream());
        assertEquals(8, config.workerThreads());
        assertEquals(250, config.queueCapacity());
        assertEquals(0, config.retryAttempts());
        assertEquals(Duration.ofMinutes(2), config.requestTimeout());
        assertTrue(config.metricsEnabled());
    }

    @Test
    void explicitFalseAndTheOtherTimeoutUnitsStillWork() throws IOException {
        ServiceConfig seconds = ConfigLoader.load(write(REQUIRED + "request.timeout=45s\nmetrics.enabled=false\n"));
        ServiceConfig millis = ConfigLoader.load(write(REQUIRED + "request.timeout=250ms\n"));

        assertEquals(Duration.ofSeconds(45), seconds.requestTimeout());
        assertFalse(seconds.metricsEnabled());
        assertEquals(Duration.ofMillis(250), millis.requestTimeout());
    }

    private Path write(String content) throws IOException {
        return Files.writeString(dir.resolve("config.properties"), content);
    }
}
