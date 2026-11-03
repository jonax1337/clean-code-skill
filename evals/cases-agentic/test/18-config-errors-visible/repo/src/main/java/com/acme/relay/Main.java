package com.acme.relay;

import com.acme.relay.config.ConfigLoader;
import com.acme.relay.config.ServiceConfig;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;

public final class Main {
    private static final String DEFAULT_CONFIG_FILE = "config.properties";

    private Main() {}

    public static void main(String[] args) throws IOException, InterruptedException {
        Path configFile = Path.of(args.length > 0 ? args[0] : DEFAULT_CONFIG_FILE);
        ServiceConfig config = ConfigLoader.load(configFile);
        Relay relay = new Relay(config, new ConsoleUplink(config, System.out), System.err);
        try (BufferedReader input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8))) {
            String line;
            while ((line = input.readLine()) != null) {
                relay.submit(line);
            }
        }
        relay.shutdown();
    }
}
