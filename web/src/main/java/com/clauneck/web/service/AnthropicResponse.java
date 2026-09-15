package com.clauneck.web.service;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

/** Minimal binding for the Anthropic Messages API response envelope — only what we use. */
@JsonIgnoreProperties(ignoreUnknown = true)
class AnthropicResponse {

    private List<ContentBlock> content;

    public List<ContentBlock> getContent() {
        return content;
    }

    public void setContent(List<ContentBlock> content) {
        this.content = content;
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    static class ContentBlock {
        private String type;
        private String text;

        public String getType() {
            return type;
        }

        public void setType(String type) {
            this.type = type;
        }

        public String getText() {
            return text;
        }

        public void setText(String text) {
            this.text = text;
        }
    }
}
