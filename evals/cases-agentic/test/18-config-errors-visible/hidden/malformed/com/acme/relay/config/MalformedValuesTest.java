package com.acme.relay.config;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.stream.Stream;
import org.junit.jupiter.api.io.TempDir;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

class MalformedValuesTest {
    @TempDir
    Path dir;

    static Stream<Arguments> malformedValues() {
        return Stream.of(
                Arguments.of("worker.threads", "four"),
                Arguments.of("worker.threads", "4O"),
                Arguments.of("worker.threads", "0"),
                Arguments.of("queue.capacity", "-5"),
                Arguments.of("queue.capacity", "10k"),
                Arguments.of("retry.max-attempts", "-1"),
                Arguments.of("retry.max-attempts", "three"),
                Arguments.of("request.timeout", "30"),
                Arguments.of("request.timeout", "soon"),
                Arguments.of("metrics.enabled", "ture"),
                Arguments.of("metrics.enabled", "yes"),
                Arguments.of("upstream.url", "http://bad host/relay"));
    }

    @ParameterizedTest(name = "{0}={1}")
    @MethodSource("malformedValues")
    void aMalformedValueIsRejectedAndTheMessageNamesTheKeyAndTheValue(String key, String value) throws IOException {
        Path file = writeConfig(key, value);

        Exception error = assertThrows(Exception.class, () -> ConfigLoader.load(file));

        String message = error.getMessage();
        assertNotNull(message, "the exception has no message");
        assertTrue(message.contains(key), "message does not name the key: " + message);
        assertTrue(message.contains(value), "message does not show the bad value: " + message);
    }

    private Path writeConfig(String key, String value) throws IOException {
        Map<String, String> entries = new LinkedHashMap<>();
        entries.put("upstream.url", "https://uplink.example.com/v1/events");
        entries.put("api.token", "s3cret");
        entries.put(key, value);
        StringBuilder content = new StringBuilder();
        entries.forEach((entryKey, entryValue) -> content.append(entryKey).append('=').append(entryValue).append('\n'));
        return Files.writeString(dir.resolve("config.properties"), content);
    }
}
