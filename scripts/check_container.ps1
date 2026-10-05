# Run only the local smoke container; no secrets, host ports or external network.
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$dataset = (Resolve-Path (Join-Path $root 'data/processed/27b46e65f45d')).Path
$container = docker run -d --network none --read-only --tmpfs /tmp --mount "type=bind,source=$dataset,target=/data/dataset,readonly" agentic-rag-eval-platform:local
if ($LASTEXITCODE -ne 0) { throw 'Container launch failed' }
try {
    $check = @'
import json, urllib.request, urllib.error, time, os
base = 'http://127.0.0.1:8000'
for attempt in range(30):
    try:
        health = json.load(urllib.request.urlopen(base + '/health', timeout=2))
        break
    except (OSError, urllib.error.URLError):
        time.sleep(0.5)
else:
    raise RuntimeError('Service did not become ready')
def post(mode):
    req = urllib.request.Request(base + '/query', data=json.dumps({'question':'PEP 655 Required NotRequired', 'mode':mode}).encode(), headers={'Content-Type':'application/json'})
    return urllib.request.urlopen(req, timeout=10)
query = json.load(post('retrieve'))
try:
    post('answer')
    raise RuntimeError('Generation unexpectedly enabled')
except urllib.error.HTTPError as error:
    assert error.code == 403
assert health['ready'] and not health['generation_enabled']
assert len(query['retrieved']) == 8 and query['answer'] is None
assert os.getuid() != 0
print(json.dumps({'health':health, 'retrieved_chunks':len(query['retrieved']), 'generation_status':403, 'uid':os.getuid(), 'network':'none', 'read_only_root':True, 'llm_calls':0}, indent=2))
'@
    $output = docker exec $container /app/.venv/bin/python -c $check
    if ($LASTEXITCODE -ne 0) { throw 'Container checks failed' }
    $evidence = $output | ConvertFrom-Json
    $imageId = docker inspect --format '{{.Image}}' $container
    $evidence | Add-Member -NotePropertyName image_id -NotePropertyValue $imageId
    $evidence | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 (Join-Path $root 'docs/evidence/infrastructure/container-smoke.json')
    Write-Output 'Container checks passed: real retrieval, generation disabled, non-root, network disabled.'
} finally {
    docker rm -f $container | Out-Null
}
