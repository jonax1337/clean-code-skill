package com.acme.relay;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.acme.relay.config.ServiceConfig;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.net.URI;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

class RelayTest {
    private final ByteArrayOutputStream logBytes = new ByteArrayOutputStream();

    @Test
    void deliversAMessageOnTheFirstTry() {
        List<String> sent = new ArrayList<>();
        Relay relay = relayWith(2, sent::add);

        relay.deliver("hello");

        assertEquals(List.of("hello"), sent);
        assertEquals(1, relay.deliveredCount());
    }

    @Test
    void retriesUntilTheUplinkAccepts() {
        FlakyUplink uplink = new FlakyUplink(2);
        Relay relay = relayWith(3, uplink);

        relay.deliver("hello");

        assertEquals(3, uplink.calls);
        assertEquals(1, relay.deliveredCount());
        assertEquals(0, relay.failedCount());
    }

    @Test
    void givesUpAfterTheConfiguredRetries() {
        FlakyUplink uplink = new FlakyUplink(10);
        Relay relay = relayWith(1, uplink);

        relay.deliver("hello");

        assertEquals(2, uplink.calls);
        assertEquals(0, relay.deliveredCount());
        assertEquals(1, relay.failedCount());
    }

    private Relay relayWith(int retryAttempts, Uplink uplink) {
        ServiceConfig config = new ServiceConfig(
                URI.create("https://uplink.example.com/v1/events"),
                "s3cret",
                1,
                10,
                retryAttempts,
                Duration.ofSeconds(1),
                false);
        return new Relay(config, uplink, new PrintStream(logBytes));
    }

    private static final class FlakyUplink implements Uplink {
        private final int failures;
        int calls;

        FlakyUplink(int failures) {
            this.failures = failures;
        }

        @Override
        public void send(String payload) throws IOException {
            calls++;
            if (calls <= failures) {
                throw new IOException("connection reset");
            }
        }
    }
}
