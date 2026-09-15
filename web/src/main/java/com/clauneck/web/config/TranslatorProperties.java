package com.clauneck.web.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "clauneck.translator")
public class TranslatorProperties {

    /** Anthropic API key. Required at runtime; never logged. */
    private String apiKey = "";

    /** Claude model id, configurable per spec.md FR7 (default: fast/cheap Haiku). */
    private String model = "claude-haiku-4-5";

    private String apiUrl = "https://api.anthropic.com/v1/messages";

    private String anthropicVersion = "2023-06-01";

    private int timeoutSeconds = 30;

    private int maxRetries = 2;

    private int maxTokens = 2048;

    public String getApiKey() {
        return apiKey;
    }

    public void setApiKey(String apiKey) {
        this.apiKey = apiKey;
    }

    public String getModel() {
        return model;
    }

    public void setModel(String model) {
        this.model = model;
    }

    public String getApiUrl() {
        return apiUrl;
    }

    public void setApiUrl(String apiUrl) {
        this.apiUrl = apiUrl;
    }

    public String getAnthropicVersion() {
        return anthropicVersion;
    }

    public void setAnthropicVersion(String anthropicVersion) {
        this.anthropicVersion = anthropicVersion;
    }

    public int getTimeoutSeconds() {
        return timeoutSeconds;
    }

    public void setTimeoutSeconds(int timeoutSeconds) {
        this.timeoutSeconds = timeoutSeconds;
    }

    public int getMaxRetries() {
        return maxRetries;
    }

    public void setMaxRetries(int maxRetries) {
        this.maxRetries = maxRetries;
    }

    public int getMaxTokens() {
        return maxTokens;
    }

    public void setMaxTokens(int maxTokens) {
        this.maxTokens = maxTokens;
    }
}
