package com.acme.relay.config;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.net.URI;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class ConfigLoaderTest {
    private static final String REQUIRED = """
            upstream.url=https://uplink.example.com/v1/events
            api.token=s3cret
            """;

    @TempDir
    Path dir;

    @Test
    void loadsEveryKey() throws IOException {
        Path file = write(REQUIRED + """
                worker.threads=8
                queue.capacity=250
                retry.max-attempts=5
                request.timeout=2m
                metrics.enabled=true
                """);

        ServiceConfig config = ConfigLoader.load(file);

        assertEquals(URI.create("https://uplink.example.com/v1/events"), config.upstream());
        assertEquals("s3cret", config.apiToken());
        assertEquals(8, config.workerThreads());
        assertEquals(250, config.queueCapacity());
        assertEquals(5, config.retryAttempts());
        assertEquals(Duration.ofMinutes(2), config.requestTimeout());
        assertTrue(config.metricsEnabled());
    }

    @Test
    void optionalKeysUseTheirDefaults() throws IOException {
        ServiceConfig config = ConfigLoader.load(write(REQUIRED));

        assertEquals(ConfigLoader.DEFAULT_WORKER_THREADS, config.workerThreads());
        assertEquals(ConfigLoader.DEFAULT_QUEUE_CAPACITY, config.queueCapacity());
        assertEquals(ConfigLoader.DEFAULT_RETRY_ATTEMPTS, config.retryAttempts());
        assertEquals(ConfigLoader.DEFAULT_REQUEST_TIMEOUT, config.requestTimeout());
        assertFalse(config.metricsEnabled());
    }

    @Test
    void parsesAllTimeoutUnits() throws IOException {
        assertEquals(
                Duration.ofMillis(500),
                ConfigLoader.load(write(REQUIRED + "request.timeout=500ms\n")).requestTimeout());
        assertEquals(
                Duration.ofSeconds(45),
                ConfigLoader.load(write(REQUIRED + "request.timeout=45s\n")).requestTimeout());
    }

    @Test
    void apiTokenIsRequired() throws IOException {
        Path file = write("upstream.url=https://uplink.example.com/v1/events\n");

        ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(file));

        assertTrue(error.getMessage().contains("api.token"));
    }

    @Test
    void upstreamUrlIsRequired() throws IOException {
        Path file = write("api.token=s3cret\n");

        ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(file));

        assertTrue(error.getMessage().contains("upstream.url"));
    }

    @Test
    void aWorkerCountThatIsNotANumberIsRejectedWithKeyValueAndCause() throws IOException {
        Path file = write(REQUIRED + "worker.threads=four\n");

        ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(file));

        assertTrue(error.getMessage().contains("worker.threads"));
        assertTrue(error.getMessage().contains("four"));
        assertInstanceOf(NumberFormatException.class, error.getCause());
    }

    @Test
    void aWorkerCountBelowTheMinimumIsRejected() throws IOException {
        Path file = write(REQUIRED + "worker.threads=0\n");

        ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(file));

        assertTrue(error.getMessage().contains("worker.threads"));
    }

    @Test
    void aTimeoutWithoutUnitIsRejected() throws IOException {
        Path file = write(REQUIRED + "request.timeout=30\n");

        ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(file));

        assertTrue(error.getMessage().contains("request.timeout"));
        assertTrue(error.getMessage().contains("30"));
    }

    @Test
    void aMisspelledBooleanIsRejectedInsteadOfBecomingFalse() throws IOException {
        Path file = write(REQUIRED + "metrics.enabled=ture\n");

        ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(file));

        assertTrue(error.getMessage().contains("metrics.enabled"));
        assertTrue(error.getMessage().contains("ture"));
    }

    @Test
    void anUnparsableUpstreamUrlIsRejected() throws IOException {
        Path file = write("upstream.url=http://bad host/relay\napi.token=s3cret\n");

        ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(file));

        assertTrue(error.getMessage().contains("upstream.url"));
        assertInstanceOf(java.net.URISyntaxException.class, error.getCause());
    }

    @Test
    void anUnreadableFileIsReportedWithItsName() {
        Path file = dir.resolve("nowhere.properties");

        ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(file));

        assertTrue(error.getMessage().contains("nowhere.properties"));
        assertInstanceOf(IOException.class, error.getCause());
    }

    private Path write(String content) throws IOException {
        return Files.writeString(dir.resolve("config.properties"), content);
    }
}
