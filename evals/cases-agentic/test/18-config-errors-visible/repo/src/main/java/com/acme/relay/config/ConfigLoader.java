package com.acme.relay.config;

import java.io.IOException;
import java.io.Reader;
import java.net.URI;
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

    public static ServiceConfig load(Path file) {
        Properties properties = read(file);
        return new ServiceConfig(
                uri(properties.getProperty("upstream.url")),
                required(properties, "api.token"),
                intValue(properties, "worker.threads", DEFAULT_WORKER_THREADS, 1),
                intValue(properties, "queue.capacity", DEFAULT_QUEUE_CAPACITY, 1),
                intValue(properties, "retry.max-attempts", DEFAULT_RETRY_ATTEMPTS, 0),
                duration(properties.getProperty("request.timeout")),
                Boolean.parseBoolean(properties.getProperty("metrics.enabled")));
    }

    private static Properties read(Path file) {
        Properties properties = new Properties();
        try (Reader reader = Files.newBufferedReader(file)) {
            properties.load(reader);
        } catch (IOException e) {
            // no readable file: run on the defaults
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

    private static URI uri(String raw) {
        try {
            return new URI(raw.trim());
        } catch (Exception e) {
            return null;
        }
    }

    private static int intValue(Properties properties, String key, int defaultValue, int minimum) {
        String raw = properties.getProperty(key);
        if (raw == null) {
            return defaultValue;
        }
        try {
            int value = Integer.parseInt(raw.trim());
            return value >= minimum ? value : defaultValue;
        } catch (NumberFormatException e) {
            return defaultValue;
        }
    }

    private static Duration duration(String raw) {
        if (raw == null) {
            return DEFAULT_REQUEST_TIMEOUT;
        }
        Matcher matcher = DURATION.matcher(raw.trim());
        if (!matcher.matches()) {
            return DEFAULT_REQUEST_TIMEOUT;
        }
        try {
            long amount = Long.parseLong(matcher.group(1));
            return switch (matcher.group(2)) {
                case "ms" -> Duration.ofMillis(amount);
                case "s" -> Duration.ofSeconds(amount);
                default -> Duration.ofMinutes(amount);
            };
        } catch (ArithmeticException | NumberFormatException e) {
            return DEFAULT_REQUEST_TIMEOUT;
        }
    }
}
