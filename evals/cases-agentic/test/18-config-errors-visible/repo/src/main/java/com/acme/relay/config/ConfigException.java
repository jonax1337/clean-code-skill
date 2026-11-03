package com.acme.relay.config;

/** The configuration cannot be used to run the service. */
public class ConfigException extends RuntimeException {
    public ConfigException(String message) {
        super(message);
    }
}
