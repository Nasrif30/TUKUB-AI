<div align="center">
  <img src="https://raw.githubusercontent.com/Nasrif30/TUKUB-AI/main/docs/banner.png" alt="TUKUB AI Banner" width="800"/>

  # TUKUB AI
  **Autonomous Security Agent**
  
  *tukub (tə-ˈküb) - Tausug (Philippines) verb: to fight, to attack*
  <br>
  *"Like beasts fighting over territory, we hunt vulnerabilities"*
</div>

---

## Description
TUKUB AI is a terminal-based autonomous security agent for professional red team and blue team operations. Built on the ReAct (Reason-Act) pattern, the system acts as the "brain" that intelligently orchestrates over 50 industry-standard security tools based on dynamic observations.

### Features
- **ReAct Execution Engine**: Observe -> Think -> Act logic pattern.
- **50+ Security Tools**: Nmap, Nuclei, FFUF, SQLMap, BloodHound, and more.
- **Multi-LLM Support**: 
  - **Offline Mode**: Run completely privately using Local `Ollama` models.
  - **Cloud APIs**: NVIDIA, Groq, OpenRouter, HuggingFace, OpenAI, Anthropic.
- **Jailbreak System**: 8 integrated personas/methods for authorized testing.
- **Zero Context Waste**: Dynamically loads domain-specific skills only when needed.
- **Versatile Modes**: Dedicated modes for CTF, Red Teaming, and Blue Team/DFIR.
- **MCP Server**: Model Context Protocol support.

---

## Architecture & Execution Flow

GitHub natively renders these diagrams. TUKUB AI uses the following architecture to reason about targets and execute security assessments autonomously.

### Core Architecture

```mermaid
graph TD
    %% Define Styles
    classDef user fill:#2C3E50,stroke:#34495E,stroke-width:2px,color:#ECF0F1
    classDef cli fill:#2980B9,stroke:#2980B9,stroke-width:2px,color:#FFFFFF
    classDef core fill:#8E44AD,stroke:#8E44AD,stroke-width:2px,color:#FFFFFF
    classDef component fill:#27AE60,stroke:#27AE60,stroke-width:2px,color:#FFFFFF
    classDef external fill:#E67E22,stroke:#E67E22,stroke-width:2px,color:#FFFFFF
    classDef storage fill:#34495E,stroke:#2C3E50,stroke-width:2px,color:#ECF0F1

    %% Actors & Interfaces
    User((Security<br/>Operator)):::user
    CLI[main.py CLI<br/>Commands & Setup Wizard]:::cli
    Storage[(keys.json<br/>~/.tukub/)]:::storage

    %% Core Engine
    subgraph Core Engine
        Agent[TukubAgent<br/>ReAct Loop]:::core
        Context[SessionContext<br/>State & Memory]:::core
    end

    %% Managers
    subgraph Subsystems
        KeyManager[KeyManager<br/>API & Model Config]:::component
        ToolRegistry[ToolRegistry<br/>Binary Execution]:::component
        SkillManager[SkillManager<br/>Dynamic Python Logic]:::component
        JailbreakManager[JailbreakManager<br/>Persona Control]:::component
    end

    %% External Connections
    subgraph LLM Providers
        BaseLLM[BaseLLMProvider<br/>Interface]:::component
        LocalLLM[OllamaProvider<br/>Local/Offline]:::external
        CloudLLM[NVIDIA / Groq / OpenAI<br/>OpenRouter / Anthropic]:::external
    end

    subgraph Host System Tools
        Nmap[nmap / nuclei / ffuf / sqlmap]:::external
    end

    %% Relationships
    User -->|Runs commands| CLI
    CLI -->|Initializes| KeyManager
    KeyManager <-->|Reads/Writes| Storage
    CLI -->|Starts Assessment| Agent

    Agent <-->|Updates/Reads| Context
    Agent -->|Requests Config| KeyManager
    Agent -->|Applies Persona| JailbreakManager
    Agent -->|Reasons Next Step| BaseLLM
    
    BaseLLM -->|Inherits| LocalLLM
    BaseLLM -->|Inherits| CloudLLM

    Agent -->|Executes Action| ToolRegistry
    ToolRegistry -->|Subprocess Call| Nmap
    
    Agent -->|Loads Domain Logic| SkillManager
```

### The ReAct Execution Loop

```mermaid
flowchart TD
    %% Styling
    classDef process fill:#3498DB,stroke:#2980B9,stroke-width:2px,color:#FFF
    classDef llm fill:#9B59B6,stroke:#8E44AD,stroke-width:2px,color:#FFF
    classDef action fill:#2ECC71,stroke:#27AE60,stroke-width:2px,color:#FFF
    classDef decision fill:#E67E22,stroke:#D35400,stroke-width:2px,color:#FFF
    classDef terminal fill:#34495E,stroke:#2C3E50,stroke-width:2px,color:#FFF

    Start([Start Assessment]):::terminal --> Observe

    subgraph ReAct Loop [The ReAct Core Engine]
        direction TB
        
        Observe[1. OBSERVE<br/>Gather Current State & Findings]:::process
        Think[2. THINK<br/>Prompt AI for Next Step]:::llm
        Decision{What is the<br/>AI's decision?}:::decision
        Act[3. ACT<br/>Execute Security Tool]:::action
        Parse[Parse Tool Output<br/>Save Finding]:::process

        Observe --> Think
        Think --> Decision
        
        Decision -->|Run a Tool| Act
        Act --> Parse
        Parse --> Observe
    end

    Decision -->|Objective Met<br/>or Max Iterations| Complete([End Assessment<br/>Generate Report]):::terminal
```

---

## Installation
```bash
# Clone the repository
git clone https://github.com/Nasrif30/TUKUB-AI.git
cd TUKUB-AI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

**1. Run the interactive setup to configure your API Keys and Models:**
```bash
python main.py setup
```

**2. List available tools:**
```bash
python main.py tools
```

**3. Run an autonomous assessment:**
```bash
python main.py run --target example.com --objective "Find vulnerabilities" --provider nvidia --authorization "AUTH-001"
```

## Legal Disclaimer
TUKUB AI is strictly for authorized security testing and educational purposes. You must have explicit, written permission to test any targets. Unauthorized use is illegal.