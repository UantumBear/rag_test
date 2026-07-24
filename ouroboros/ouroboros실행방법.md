```bash
ouroboros --version
ouroboros run --help
which ouroboros

# 2. 코드 생성 없이 시드 검사하기
ouroboros run workflow --runtime codex --project-dir . --debug ouroboros/seeds/seed_f101692bd03c.yaml

## --dry-run은 파일을 수정하지 않고 명세를 읽을 수 있는지만 확인하는 옵션

>> 결과:

ouroboros run workflow --dry-run ouroboros/seeds/seed_f101692bd03c.yaml 를 수행하면, 아래에 cli_path, cwd 등 실행 관련 설정이 노출되는데, dir 지정 없이 실행 시 
cwd=/Users/a454676/.ouroboros/worktrees/rag_test/orch_612decbbe465/ouroboros/seeds 
위 경로로 잡혀서, 경로를 지정해야 한다.

# 3. 

```


```
(.venv) ) a454676@454676ui-MacBookPro rag_test % ouroboros run --help
                                                                                                                          
 Usage: ouroboros run [OPTIONS] COMMAND [ARGS]...                                                                         
                                                                                                                          
 Execute Ouroboros workflows.                                                                                             
                                                                                                                          
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                                                            │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ workflow  Execute a workflow from a seed file.                                                                         │
│ resume    Resume a paused or failed execution.                                                                         │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

((.venv) ) a454676@454676ui-MacBookPro rag_test % ouroboros run workflow --help
                                                                                                                          
 Usage: ouroboros run workflow [OPTIONS] SEED_FILE                                                                        
                                                                                                                          
 Execute a workflow from a seed file.                                                                                     
                                                                                                                          
 Reads the seed YAML configuration and runs the Ouroboros workflow.                                                       
 Orchestrator mode is enabled by default.                                                                                 
                                                                                                                          
 Use --no-orchestrator only for the non-orchestrated standard workflow path.                                              
 Use --resume to continue a previous session.                                                                             
 Use --mcp-config to connect to external MCP servers for additional tools.                                                
                                                                                                                          
 Examples:                                                                                                                
                                                                                                                          
     # Run a workflow (shorthand -- orchestrator mode by default)                                                         
     ouroboros run seed.yaml                                                                                              
                                                                                                                          
     # Explicit subcommand (equivalent)                                                                                   
     ouroboros run workflow seed.yaml                                                                                     
                                                                                                                          
     # Legacy standard workflow mode                                                                                      
     ouroboros run seed.yaml --no-orchestrator                                                                            
                                                                                                                          
     # With MCP server integration                                                                                        
     ouroboros run seed.yaml --mcp-config mcp.yaml                                                                        
                                                                                                                          
     # Resume a previous session                                                                                          
     ouroboros run seed.yaml --resume orch_abc123                                                                         
                                                                                                                          
     # Use Codex CLI runtime                                                                                              
     ouroboros run seed.yaml --runtime codex                                                                              
                                                                                                                          
     # Use Hermes CLI runtime                                                                                             
     ouroboros run seed.yaml --runtime hermes                                                                             
                                                                                                                          
     # Debug output                                                                                                       
     ouroboros run seed.yaml --debug                                                                                      
                                                                                                                          
     # Skip post-execution QA                                                                                             
     ouroboros run seed.yaml --no-qa                                                                                      
                                                                                                                          
     # Limit recursive decomposition depth                                                                                
     ouroboros run seed.yaml --max-decomposition-depth 1                                                                  
                                                                                                                          
     # Skip ACs already satisfied by the working tree                                                                     
     ouroboros run seed.yaml --skip-completed docs/completed.yaml                                                         
                                                                                                                          
╭─ Arguments ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    seed_file      FILE  Path to the seed YAML file. [required]                                                       │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --orchestrator             -o  --no-orchestrator  -O                                  Use the agent-runtime            │
│                                                                                       orchestrator for execution.      │
│                                                                                       Enabled by default.              │
│                                                                                       [default: orchestrator]          │
│ --resume                   -r                         TEXT                            Resume a previous orchestrator   │
│                                                                                       session by ID.                   │
│ --mcp-config                                          PATH                            Path to MCP client configuration │
│                                                                                       YAML file for external tool      │
│                                                                                       integration.                     │
│ --mcp-tool-prefix                                     TEXT                            Prefix to add to all MCP tool    │
│                                                                                       names (e.g., 'mcp_').            │
│ --project-dir                                         DIRECTORY                       Explicit project directory for   │
│                                                                                       resolving seed-relative paths.   │
│ --dry-run                  -n                                                         Validate seed without executing. │
│ --debug                    -d                                                         Show logs and agent thinking     │
│                                                                                       (verbose output).                │
│ --sequential               -s                                                         Execute ACs sequentially instead │
│                                                                                       of in parallel (default:         │
│                                                                                       parallel).                       │
│ --runtime                                             [claude|codex|opencode|hermes|  Agent runtime backend for        │
│                                                       gemini|copilot|goose|kiro|pi|g  orchestrator mode (claude,       │
│                                                       jc|antigravity|grok|zcode]      codex, opencode, hermes, gemini, │
│                                                                                       copilot, goose, kiro, pi, gjc,   │
│                                                                                       antigravity, grok, or zcode).    │
│ --no-qa                                                                               Skip post-execution QA           │
│                                                                                       evaluation.                      │
│ --max-decomposition-depth                             INTEGER RANGE [x>=0]            Maximum recursive AC             │
│                                                                                       decomposition depth. 0 disables  │
│                                                                                       decomposition; 1 allows one      │
│                                                                                       split; default 2.                │
│ --skip-completed                                      TEXT                            Path to a YAML marker file       │
│                                                                                       listing already-satisfied        │
│                                                                                       top-level ACs. Entries use       │
│                                                                                       1-based AC numbers under         │
│                                                                                       completed_acs.                   │
│ --help                                                                                Show this message and exit.      │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

((.venv) ) a454676@454676ui-MacBookPro rag_test % 


```