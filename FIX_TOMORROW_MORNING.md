# 🌅 MORNING FIX - 3 SIMPLE STEPS

## **The Problem:**
Backend needs to be updated on PythonAnywhere with the new code.

---

## **The Fix (5 minutes):**

### **Step 1: SSH into PythonAnywhere**
Go to: https://www.pythonanywhere.com/user/deedavis/consoles/

Click your existing Bash console.

---

### **Step 2: Run These 3 Commands**

```bash
cd ~/nexus-backend
git pull origin main
pip install python-dateutil
```

---

### **Step 3: Reload Web App**

1. Go to: https://www.pythonanywhere.com/user/deedavis/webapps/#tab_id_deedavis_pythonanywhere_com
2. Click the big green **"Reload"** button
3. Wait 10 seconds

---

## **Test It:**

Go to: https://nexus-command.netlify.app/

Click the buttons - they should work now.

---

## **If Still Not Working:**

Check the logs:
```bash
tail -50 /var/log/deedavis.pythonanywhere.com.error.log
```

Look for errors and send them to me.

---

**That's it! Sleep well. Fix it in 5 minutes tomorrow morning.** 💤
