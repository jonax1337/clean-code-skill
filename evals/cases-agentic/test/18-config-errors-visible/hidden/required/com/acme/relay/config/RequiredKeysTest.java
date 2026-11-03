package com.acme.relay.config;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class RequiredKeysTest {
    @TempDir
    Path dir;

    @Test
    void missingUpstreamUrlIsReportedByName() throws IOException {
        Path file = write("api.token=s3cret\nworker.threads=2\n");

        Exception error = assertThrows(Exception.class, () -> ConfigLoader.load(file));

        assertMentions(error, "upstream.url");
    }

    @Test
    void missingApiTokenIsReportedByName() throws IOException {
        Path file = write("upstream.url=https://uplink.example.com/v1/events\n");

        Exception error = assertThrows(Exception.class, () -> ConfigLoader.load(file));

        assertMentions(error, "api.token");
    }

    @Test
    void aFileThatCannotBeReadIsReportedWithItsName() {
        Path file = dir.resolve("nowhere.properties");

        Exception error = assertThrows(Exception.class, () -> ConfigLoader.load(file));

        assertMentions(error, "nowhere.properties");
    }

    private static void assertMentions(Exception error, String text) {
        String message = error.getMessage();
        assertNotNull(message, "the exception has no message");
        assertTrue(message.contains(text), "message does not mention " + text + ": " + message);
    }

    private Path write(String content) throws IOException {
        return Files.writeString(dir.resolve("config.properties"), content);
    }
}
