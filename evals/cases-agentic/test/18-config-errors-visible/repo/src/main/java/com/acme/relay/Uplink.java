package com.acme.relay;

import java.io.IOException;

/** Sends one message to the upstream endpoint. */
@FunctionalInterface
public interface Uplink {
    void send(String payload) throws IOException;
}
