#!/usr/bin/env bash

# ========== CONFIG ==========
MAX_RETRIES=1
RETRY_DELAY=2
LOG_DIR="logs"
LOG_FILE="${LOG_DIR}/check_services.log"
JSON_REPORT="${LOG_DIR}/check_report.json"
mkdir -p "$LOG_DIR"
> "$LOG_FILE"
echo '{' > "$JSON_REPORT"

# ========== FORMATTING ==========
bold=$(tput bold)
normal=$(tput sgr0)
green="\033[32m"
red="\033[31m"
blue="\033[34m"
yellow="\033[33m"
check_mark="✔"
cross_mark="✘"

log() {
  echo -e "$@" | tee -a "$LOG_FILE"
}

json_keyval() {
  echo "  \"$1\": \"$2\"," >> "$JSON_REPORT"
}

print_header() {
  log "\n${bold}${blue}🔄 $1${normal}"
}

print_status() {
  local status=$1
  local msg=$2
  if [ "$status" -eq 0 ]; then
    log "${green}${check_mark} $msg${normal}"
    json_keyval "$msg" "PASS"
  else
    log "${red}${cross_mark} $msg${normal}"
    json_keyval "$msg" "FAIL"
  fi
}

print_block() {
  log "\n${bold}${yellow}$1${normal}"
}

run_with_retry() {
  local retries=0
  local cmd="$1"
  until eval "$cmd"; do
    retries=$((retries + 1))
    if [ "$retries" -ge "$MAX_RETRIES" ]; then
      return 1
    fi
    log "${yellow}Retrying in ${RETRY_DELAY}s... [$retries/$MAX_RETRIES]${normal}"
    sleep "$RETRY_DELAY"
  done
  return 0
}

# ========== CHECKS ==========

print_header "Restarting all containers..."

docker compose down --remove-orphans >> "$LOG_FILE" 2>&1
docker volume prune -f >> "$LOG_FILE" 2>&1

docker compose up -d graphiti_mcp_ollama >> "$LOG_FILE" 2>&1
sleep 2
docker compose up --build -d ollama-pull >> "$LOG_FILE" 2>&1
sleep 10
docker compose up -d neo4j >> "$LOG_FILE" 2>&1
sleep 5
docker compose up -d graphiti-mcp >> "$LOG_FILE" 2>&1

# Step 1: Ollama model check
print_header "Checking Ollama model availability..."
run_with_retry "docker exec graphiti_mcp_ollama ollama list | grep 'deepseek-r1:8b' &>/dev/null"
status=$?
print_status $status "Ollama model deepseek-r1:8b available"
if [ "$status" -ne 0 ]; then
  docker exec graphiti_mcp_ollama ollama list | tee -a "$LOG_FILE"
fi

# Step 2: Neo4j health check
print_header "Checking Neo4j health..."
run_with_retry "[ \"$(docker inspect --format='{{.State.Health.Status}}' neo4j 2>/dev/null)\" = \"healthy\" ]"
status=$?
print_status $status "Neo4j is healthy"
if [ "$status" -ne 0 ]; then
  print_block "Last Neo4j logs:"
  docker compose logs neo4j | tail -n 30 | tee -a "$LOG_FILE"
fi

# Step 3: Graphiti MCP SSE
print_header "Checking Graphiti MCP SSE endpoint..."
run_with_retry "curl -sf -N http://localhost:8001/sse &>/dev/null"
status=$?
print_status $status "Graphiti MCP SSE endpoint is accessible"
if [ "$status" -ne 0 ]; then
  print_block "Last MCP logs:"
  docker compose logs graphiti-mcp | tail -n 30 | tee -a "$LOG_FILE"
fi

# Step 4: Ollama chat response
print_header "Testing Ollama LLM response..."
run_with_retry "curl -s -X POST http://localhost:11435/api/chat -H 'Content-Type: application/json' -d '{\"model\": \"deepseek-r1:8b\", \"messages\": [{\"role\": \"user\", \"content\": \"Hello!\"}]}' | grep -q 'content'"
status=$?
print_status $status "Ollama returned a valid response"
if [ "$status" -ne 0 ]; then
  print_block "Raw Ollama response:"
  curl -s -X POST http://localhost:11435/api/chat -H "Content-Type: application/json" \
    -d '{"model": "deepseek-r1:8b", "messages": [{"role": "user", "content": "Hello!"}]}' | tee -a "$LOG_FILE"
fi

echo '  "_summary": "complete"' >> "$JSON_REPORT"
echo '}' >> "$JSON_REPORT"

log "\n${bold}${green}✅ All checks complete. Log: ${LOG_FILE}, Report: ${JSON_REPORT}${normal}"
