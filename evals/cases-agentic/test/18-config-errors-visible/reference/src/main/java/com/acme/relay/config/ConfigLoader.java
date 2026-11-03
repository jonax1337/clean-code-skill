package com.acme.relay.config;

import java.io.IOException;
import java.io.Reader;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.Properties;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Reads the relay's configuration from a properties file. */
public final class ConfigLoader {
    static final int DEFAULT_WORKER_THREADS = 4;
    static final int DEFAULT_QUEUE_CAPACITY = 1000;
    static final int DEFAULT_RETRY_ATTEMPTS = 3;
    static final Duration DEFAULT_REQUEST_TIMEOUT = Duration.ofSeconds(30);

    private static final Pattern DURATION = Pattern.compile("(\\d+)(ms|s|m)");

    private ConfigLoader() {}

    /** Loads the configuration; a missing required key or a present but malformed value is a {@link ConfigException}. */
    public static ServiceConfig load(Path file) {
        Properties properties = read(file);
        return new ServiceConfig(
                uri(properties, "upstream.url"),
                required(properties, "api.token"),
                intValue(properties, "worker.threads", DEFAULT_WORKER_THREADS, 1),
                intValue(properties, "queue.capacity", DEFAULT_QUEUE_CAPACITY, 1),
                intValue(properties, "retry.max-attempts", DEFAULT_RETRY_ATTEMPTS, 0),
                duration(properties, "request.timeout"),
                flag(properties, "metrics.enabled"));
    }

    private static Properties read(Path file) {
        Properties properties = new Properties();
        try (Reader reader = Files.newBufferedReader(file)) {
            properties.load(reader);
        } catch (IOException e) {
            throw new ConfigException("Cannot read configuration file " + file + ": " + e, e);
        }
        return properties;
    }

    private static String required(Properties properties, String key) {
        String value = properties.getProperty(key);
        if (value == null || value.isBlank()) {
            throw new ConfigException(key + " is required");
        }
        return value.trim();
    }

    private static URI uri(Properties properties, String key) {
        String raw = required(properties, key);
        try {
            return new URI(raw);
        } catch (URISyntaxException e) {
            throw invalid(key, raw, "a valid URL", e);
        }
    }

    private static int intValue(Properties properties, String key, int defaultValue, int minimum) {
        String raw = properties.getProperty(key);
        if (raw == null) {
            return defaultValue;
        }
        String expected = "a whole number of at least " + minimum;
        try {
            int value = Integer.parseInt(raw.trim());
            if (value < minimum) {
                throw invalid(key, raw, expected, null);
            }
            return value;
        } catch (NumberFormatException e) {
            throw invalid(key, raw, expected, e);
        }
    }

    private static Duration duration(Properties properties, String key) {
        String raw = properties.getProperty(key);
        if (raw == null) {
            return DEFAULT_REQUEST_TIMEOUT;
        }
        Matcher matcher = DURATION.matcher(raw.trim());
        String expected = "a whole number followed by ms, s or m";
        if (!matcher.matches()) {
            throw invalid(key, raw, expected, null);
        }
        try {
            long amount = Long.parseLong(matcher.group(1));
            return switch (matcher.group(2)) {
                case "ms" -> Duration.ofMillis(amount);
                case "s" -> Duration.ofSeconds(amount);
                default -> Duration.ofMinutes(amount);
            };
        } catch (ArithmeticException | NumberFormatException e) {
            throw invalid(key, raw, expected, e);
        }
    }

    private static boolean flag(Properties properties, String key) {
        String raw = properties.getProperty(key);
        if (raw == null) {
            return false;
        }
        String value = raw.trim();
        if (value.equalsIgnoreCase("true")) {
            return true;
        }
        if (value.equalsIgnoreCase("false")) {
            return false;
        }
        throw invalid(key, raw, "true or false", null);
    }

    private static ConfigException invalid(String key, String value, String expected, Throwable cause) {
        return new ConfigException("Invalid value '" + value + "' for " + key + ": expected " + expected, cause);
    }
}
