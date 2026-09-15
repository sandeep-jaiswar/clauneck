package com.clauneck.web.config;

import java.time.Duration;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

/** Configures service-specific HTTP clients so each outbound call uses its own deadline. */
@Configuration
public class RestTemplateConfig {

    @Bean
    public RestTemplate translatorRestTemplate(RestTemplateBuilder builder,
                                                TranslatorProperties translatorProperties) {
        return buildRestTemplate(builder, translatorProperties.getTimeoutSeconds());
    }

    @Bean
    public RestTemplate engineRestTemplate(RestTemplateBuilder builder,
                                            EngineProperties engineProperties) {
        return buildRestTemplate(builder, engineProperties.getTimeoutSeconds());
    }

    private RestTemplate buildRestTemplate(RestTemplateBuilder builder, int timeoutSeconds) {
        Duration timeout = Duration.ofSeconds(timeoutSeconds);
        return builder
                .setConnectTimeout(timeout)
                .setReadTimeout(timeout)
                .build();
    }
}
