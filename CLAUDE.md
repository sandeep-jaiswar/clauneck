# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**clauneck** is a multi-module Gradle project with three modules:

- **core**: Base library module with shared utilities (Guava dependency)
- **web**: Spring Boot web application module for REST APIs and web services
- **api**: API module that depends on core

The project uses:
- **Build System**: Gradle 4.4.1
- **Java Version**: 21
- **Key Dependencies**: Spring Boot 3.2.2 (web), Guava 31.1-jre (core)
- **CI/CD**: GitHub Actions (builds and tests on push/PR to production branch)

## Build and Development Commands

### Build
```bash
gradle build              # Build all modules and run tests
gradle build -x test      # Build without running tests
gradle clean              # Clean build artifacts (.gradle, build/)
```

### Testing
```bash
gradle test               # Run all tests across all modules
gradle :module:test       # Run tests for a specific module (e.g., gradle :web:test)
```

### Module-Specific Tasks
```bash
gradle :core:build        # Build only core module
gradle :web:build         # Build only web module
gradle :api:build         # Build only api module
gradle tasks              # List all available Gradle tasks
```

### IDE Integration
```bash
gradle idea               # Generate IntelliJ IDEA project files (if configured)
```

## Project Structure

```
clauneck/
├── core/                 # Base library module
│   └── build.gradle      # Declares Guava dependency
├── web/                  # Spring Boot web module
│   └── build.gradle      # Declares Spring Boot web starter, depends on :core
├── api/                  # API module
│   └── build.gradle      # Depends on :core
├── build.gradle          # Root build configuration (currently minimal)
├── settings.gradle       # Defines modules: core, web, api
└── .github/workflows/ci.yml  # GitHub Actions CI pipeline
```

## Dependencies and Relationships

- **web** → **core** (web depends on core)
- **api** → **core** (api depends on core)
- **core** has no internal dependencies
- **web** and **api** are independent of each other (can run separately)

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs on:
- Push to `production` branch
- Pull requests targeting `production` branch

Command: `gradle build --no-daemon`

## AI-Native SDLC Workflow

This project follows the **AI-Native SDLC** approach for continuous, AI-assisted development with human oversight. Each stage produces versioned artifacts that feed into the next stage, creating an audit trail.

### Workflow Stages (Skip Deploy)

**1. Plan** - Capture project intent as machine-readable requirements
- Command: `/sdlc plan <description>`
- Output: `intent.md` (versioned, committed)
- Responsibility: Define what needs to be built and why

**2. Design** - Compress requirements into detailed specifications
- Command: `/sdlc design <feature>`
- Output: `spec.md` (versioned, committed)
- Tool: Claude Code plan mode for interactive design sessions
- Responsibility: How the feature will be implemented

**3. Build** - Generate code and tests through AI with plan mode
- Command: `/sdlc build <feature>`
- Output: Code, tests, updated `CLAUDE.md`, skills
- Tool: Claude Code plan mode as default entry point
- Responsibility: Maintain `CLAUDE.md` and skills for institutional knowledge

**4. Test** - Continuous evaluation throughout implementation
- Command: `/sdlc test <module>`
- Output: Test results, coverage reports
- Integration: Runs in CI pipeline automatically
- Responsibility: Catch issues early, inform design decisions

**5. Maintain** - Monitor production and close the loop
- Command: `/sdlc maintain`
- Output: Metrics, incident reports, updated `intent.md`
- Responsibility: Route issues back to planning cycle

### Core Principles

- **Artifact-Driven**: Each stage ends by committing an artifact; next stage begins by reading it
- **Continuous Evaluation**: Test throughout, not just at stage boundaries
- **Encoded Standards**: Use reusable skills to maintain organizational patterns
- **Human Accountability**: Humans responsible for decisions; AI handles automation

### Skill Templates

All skills follow these patterns:

**plan.md** - Captures user intent for features/fixes
**spec.md** - Detailed design and implementation approach  
**CLAUDE.md** - Updated with new patterns, dependencies, commands
**skills/** - Reusable skills for this project

### Development Workflow (Typical)

```bash
# 1. Start with planning
/sdlc plan "Add user authentication to web module"

# 2. Design the feature
/sdlc design "user-authentication"

# 3. Build with plan mode (automatic starting point)
/sdlc build "user-authentication"

# 4. Run tests continuously
/sdlc test web

# 5. Monitor and collect feedback
/sdlc maintain
```

## Notes for Future Development

- Source code follows standard Gradle project structure: `src/main/java` and `src/test/java`
- The project is freshly scaffolded with minimal dependencies; add test frameworks (JUnit, Mockito) as needed
- For the web module, Spring Boot auto-configuration applies based on classpath dependencies
- Current build files are minimal; plugins and common configurations can be extracted to root `build.gradle` as the project grows
- Maintain `CLAUDE.md` as the source of truth for project patterns and AI-assistant guidance
- Skills are stored in `.claude/skills/` and committed to version control for team consistency
