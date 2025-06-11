# ⚡ SuperSmartMatch V2 - Quick Reference

## 🚀 One-Line Deployment
```bash
./scripts/deploy_production.sh complete && streamlit run scripts/production_monitor.py
```

## 🔍 Health Check
```bash
curl -s http://localhost:5070/api/v2/health | jq
```

## 📊 Instant Metrics
```bash
curl -s http://localhost:5070/api/v2/metrics | jq '.precision, .latency_p95, .roi_current'
```

## 🚨 Emergency Stop
```bash
./scripts/emergency_rollback.sh manual
```

## 🧪 Quick Test
```bash
python3 scripts/final_validation_fixed.py --sample-size 1000
```

## 📈 Monitor Live
```bash
watch 'curl -s http://localhost:5070/api/v2/health | jq'
```
