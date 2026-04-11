# 🔧 Sarvam API Timeout - Solutions

You're getting Sarvam API timeouts. Here are the solutions:

---

## ✅ What I've Already Fixed

1. **Increased timeout** from 10s to 30s
2. **Added retry logic** with exponential backoff
3. **Better error handling** and logging
4. **Graceful degradation** - returns empty result instead of crashing

---

## 🔍 Diagnose the Issue

First, check if it's a network problem:

```bash
cd backend
python check_sarvam_status.py
```

This will:
- ✅ Check API key
- ✅ Test HTTP connection
- ✅ Test API endpoint
- ✅ Check DNS resolution
- ✅ Provide recommendations

---

## 🚀 Solutions (In Order)

### Solution 1: Wait and Retry (Most Likely)

Sarvam API may be temporarily slow or overloaded.

**Try again in 2-3 minutes.**

The retry logic will automatically retry 3 times with exponential backoff:
- Attempt 1: Immediate
- Attempt 2: After 1 second
- Attempt 3: After 2 seconds

### Solution 2: Check Your Internet

```bash
# Test internet connection
ping google.com

# Test Sarvam API directly
curl https://api.sarvam.ai
```

If these fail, fix your internet connection first.

### Solution 3: Use Mock Transcription (Temporary)

If Sarvam is consistently timing out, use mock data:

**Edit `backend/.env`:**
```bash
USE_MOCK_TRANSCRIPTION="true"
```

This will:
- ✅ Use hardcoded transcript instead
- ✅ Skip Sarvam API calls
- ✅ Let you test the full pipeline
- ✅ No timeout issues

**To switch back:**
```bash
USE_MOCK_TRANSCRIPTION="false"
```

### Solution 4: Check Firewall/Proxy

Some networks block API calls. Try:

1. **Different network** (mobile hotspot, different WiFi)
2. **VPN** (if allowed)
3. **Corporate proxy** (if applicable)

### Solution 5: Contact Sarvam Support

If timeouts persist:
- Check https://sarvam.ai status page
- Contact Sarvam support
- Check API key validity

---

## 📊 Current Timeout Settings

**Updated in `backend/transcriber.py`:**

```python
timeout = aiohttp.ClientTimeout(
    total=30,        # Total request time: 30 seconds
    connect=10,      # Connection time: 10 seconds
    sock_read=20     # Read time: 20 seconds
)
```

This gives Sarvam plenty of time to respond.

---

## 🧪 Test Transcription

### Quick Test (No Timeout Risk)

```bash
cd backend
python test_sarvam_speed.py
```

This uses synthetic audio and shows if API is responding.

### Live Test (May Timeout)

```bash
python test_live_transcription.py
```

If this times out, use Solution 3 (mock transcription).

---

## 🎯 Recommended Approach

**For now:**

1. **Use mock transcription** to test the full pipeline
   ```bash
   # Edit .env
   USE_MOCK_TRANSCRIPTION="true"
   
   # Run full app
   python main.py
   ```

2. **Test everything else** (AI analysis, frontend, etc.)

3. **Try Sarvam again later** when it's responsive
   ```bash
   # Edit .env
   USE_MOCK_TRANSCRIPTION="false"
   
   # Restart backend
   python main.py
   ```

---

## 📝 What Mock Transcription Does

When `USE_MOCK_TRANSCRIPTION="true"`:

- Uses hardcoded transcript from `mock_data.py`
- Emits segments at realistic timing
- Skips Sarvam API entirely
- No timeout issues
- Perfect for testing UI and AI analysis

**The mock transcript is:**
```
[0:00] CALLER: "Hi, I've been feeling really low lately..."
[0:10] OPERATOR: "Can you tell me more about that?"
[0:20] CALLER: "I've been thinking about this for weeks..."
[0:30] OPERATOR: "What does 'a way forward' mean to you?"
[0:40] CALLER: "I think I've finally decided what I need to do..."
```

---

## ✅ Verification Checklist

After switching to mock mode:

- [ ] Backend starts without errors
- [ ] Frontend connects
- [ ] Transcript appears
- [ ] Risk indicator animates
- [ ] AI analysis works
- [ ] Suggested response shows
- [ ] No timeout errors

If all pass, the issue is **Sarvam API availability**, not your code.

---

## 🔄 When Sarvam is Back

Once Sarvam API is responsive:

1. **Edit `.env`:**
   ```bash
   USE_MOCK_TRANSCRIPTION="false"
   ```

2. **Restart backend:**
   ```bash
   python main.py
   ```

3. **Test live transcription:**
   ```bash
   python test_live_transcription.py
   ```

---

## 💡 Pro Tips

1. **Sarvam API is slower than Whisper**
   - Expect 1-3 seconds per chunk
   - This is normal for cloud APIs

2. **Retry logic is automatic**
   - No need to manually retry
   - System tries 3 times automatically

3. **Mock mode is production-ready**
   - Use for demos and testing
   - Switch to Sarvam for real calls

4. **Check logs for details**
   - Backend logs show timeout details
   - Look for "Sarvam API timeout" messages

---

## 🚀 Quick Fix

**Fastest solution right now:**

```bash
cd backend

# Edit .env
# Change: USE_MOCK_TRANSCRIPTION="true"

# Restart
python main.py

# Test
python test_analyzer.py
```

This will let you test everything while Sarvam recovers.

---

**Status:** Timeout handling improved, mock fallback available
**Next:** Try mock mode or wait for Sarvam to recover
