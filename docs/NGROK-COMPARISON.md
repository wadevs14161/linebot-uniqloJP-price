# Single vs Dual ngrok Comparison

## ✅ Single ngrok Tunnel (Recommended)

### Pros:
- 🆓 **Works with free ngrok account** (1 tunnel limit)
- 🔗 **Single URL** for everything (easier to manage)
- 📝 **Simpler Line Bot setup** (one webhook URL)
- 🔧 **Production-like setup** (nginx reverse proxy)
- 💰 **Cost-effective** (no paid ngrok subscription needed)

### Cons:
- 🏗️ **Slightly more complex** (nginx configuration)
- 🐛 **Single point of failure** (if nginx fails, everything fails)

### Usage:
```bash
./deploy-docker-ngrok.sh
```

**Result URLs:**
- Everything: `https://abc123.ngrok.io`
- Line Bot webhook: `https://abc123.ngrok.io/find_product`
- Web interface: `https://abc123.ngrok.io/`
- API: `https://abc123.ngrok.io/api/search`

---

## 🔄 Dual ngrok Tunnels

### Pros:
- 🎯 **Direct access** to each service
- 🔄 **Service isolation** (frontend/backend independent)
- 🐛 **Better fault tolerance** (one tunnel fails, other still works)
- 🛠️ **Easier debugging** (separate logs per service)

### Cons:
- 💳 **Requires paid ngrok account** (multiple tunnels)
- 🔗 **Multiple URLs** to manage
- 📝 **More complex setup** (two webhook URLs to track)

### Usage:
```bash
./deploy-docker-ngrok-dual.sh
```

**Result URLs:**
- Backend: `https://def456.ngrok.io` (for Line Bot webhook)
- Frontend: `https://ghi789.ngrok.io` (for users)

---

## 🎯 Which Should You Choose?

| Scenario | Recommendation |
|----------|---------------|
| **Free ngrok account** | ✅ Single tunnel |
| **Development/Testing** | ✅ Single tunnel |
| **Demo/Presentation** | ✅ Single tunnel |
| **Production (small scale)** | ✅ Single tunnel |
| **Production (large scale)** | 🔄 Dual tunnels + load balancer |
| **High availability needs** | 🔄 Dual tunnels |
| **Debugging complex issues** | 🔄 Dual tunnels |

## 🚀 Migration Path

Start with **single tunnel** → If you need more features → Upgrade to **dual tunnels**

Both setups are fully functional and can handle the same traffic load!
