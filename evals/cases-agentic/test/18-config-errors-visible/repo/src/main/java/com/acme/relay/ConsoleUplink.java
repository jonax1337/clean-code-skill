package com.acme.relay;

import com.acme.relay.config.ServiceConfig;
import java.io.PrintStream;

/** Stands in for the HTTP client: prints the request it would make. */
public final class ConsoleUplink implements Uplink {
    private final ServiceConfig config;
    private final PrintStream out;

    public ConsoleUplink(ServiceConfig config, PrintStream out) {
        this.config = config;
        this.out = out;
    }

    @Override
    public void send(String payload) {
        out.println("POST " + config.upstream() + " (timeout " + config.requestTimeout().toMillis() + " ms): " + payload);
    }
}
