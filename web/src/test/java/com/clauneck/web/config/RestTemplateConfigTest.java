package com.clauneck.web.config;

import static org.junit.jupiter.api.Assertions.assertSame;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.time.Duration;
import org.junit.jupiter.api.Test;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.web.client.RestTemplate;

class RestTemplateConfigTest {

    private final RestTemplateConfig config = new RestTemplateConfig();

    @Test
    void translatorClientUsesTranslatorTimeout() {
        TranslatorProperties properties = new TranslatorProperties();
        properties.setTimeoutSeconds(17);

        assertTimeoutConfiguration(
                builder -> config.translatorRestTemplate(builder, properties), Duration.ofSeconds(17));
    }

    @Test
    void engineClientUsesEngineTimeout() {
        EngineProperties properties = new EngineProperties();
        properties.setTimeoutSeconds(4);

        assertTimeoutConfiguration(
                builder -> config.engineRestTemplate(builder, properties), Duration.ofSeconds(4));
    }

    private void assertTimeoutConfiguration(RestTemplateFactory factory, Duration timeout) {
        RestTemplateBuilder builder = mock(RestTemplateBuilder.class);
        RestTemplate restTemplate = new RestTemplate();
        when(builder.setConnectTimeout(timeout)).thenReturn(builder);
        when(builder.setReadTimeout(timeout)).thenReturn(builder);
        when(builder.build()).thenReturn(restTemplate);

        assertSame(restTemplate, factory.build(builder));
        verify(builder).setConnectTimeout(timeout);
        verify(builder).setReadTimeout(timeout);
    }

    @FunctionalInterface
    private interface RestTemplateFactory {
        RestTemplate build(RestTemplateBuilder builder);
    }
}
