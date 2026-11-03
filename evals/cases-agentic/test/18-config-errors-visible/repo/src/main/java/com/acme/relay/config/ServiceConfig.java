package com.acme.relay.config;

import java.net.URI;
import java.time.Duration;

public record ServiceConfig(
        URI upstream,
        String apiToken,
        int workerThreads,
        int queueCapacity,
        int retryAttempts,
        Duration requestTimeout,
        boolean metricsEnabled) {}
