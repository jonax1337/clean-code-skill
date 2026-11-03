package com.acme.relay;

import com.acme.relay.config.ServiceConfig;
import java.io.IOException;
import java.io.PrintStream;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;

/** Delivers submitted messages with a bounded queue, a fixed worker pool and retries. */
public final class Relay {
    private static final long SHUTDOWN_WAIT_SECONDS = 30;

    private final ServiceConfig config;
    private final Uplink uplink;
    private final PrintStream log;
    private final ThreadPoolExecutor workers;
    private final AtomicLong delivered = new AtomicLong();
    private final AtomicLong failed = new AtomicLong();

    public Relay(ServiceConfig config, Uplink uplink, PrintStream log) {
        this.config = config;
        this.uplink = uplink;
        this.log = log;
        this.workers = new ThreadPoolExecutor(
                config.workerThreads(),
                config.workerThreads(),
                0L,
                TimeUnit.MILLISECONDS,
                new ArrayBlockingQueue<>(config.queueCapacity()),
                new ThreadPoolExecutor.CallerRunsPolicy());
    }

    public void submit(String message) {
        workers.execute(() -> deliver(message));
    }

    void deliver(String message) {
        int maxAttempts = config.retryAttempts() + 1;
        for (int attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                uplink.send(message);
                delivered.incrementAndGet();
                return;
            } catch (IOException e) {
                log.println("delivery attempt " + attempt + " of " + maxAttempts + " failed: " + e.getMessage());
            }
        }
        failed.incrementAndGet();
    }

    public void shutdown() throws InterruptedException {
        workers.shutdown();
        workers.awaitTermination(SHUTDOWN_WAIT_SECONDS, TimeUnit.SECONDS);
        if (config.metricsEnabled()) {
            log.println("metrics: delivered=" + delivered + " failed=" + failed);
        }
    }

    long deliveredCount() {
        return delivered.get();
    }

    long failedCount() {
        return failed.get();
    }
}
