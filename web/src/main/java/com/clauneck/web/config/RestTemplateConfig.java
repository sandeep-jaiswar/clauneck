package com.clauneck.web.config;

import java.time.Duration;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

/**
 * Single RestTemplate reused for both the Claude API call and the engine call.
 * Timeout is the max of the two configured service timeouts so neither call
 * is cut off early.
 */
@Configuration
public class RestTemplateConfig {

    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder,
                                      TranslatorProperties translatorProperties,
                                      EngineProperties engineProperties) {
        int timeoutSeconds = Math.max(translatorProperties.getTimeoutSeconds(),
                engineProperties.getTimeoutSeconds());
        Duration timeout = Duration.ofSeconds(timeoutSeconds);
        return builder
                .setConnectTimeout(timeout)
                .setReadTimeout(timeout)
                .build();
    }
}
