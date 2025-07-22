# Pune Traffic Updates 🚦

**Automated Pune Traffic Updates Bot**

This project automatically scrapes the latest Pune traffic news from Google News RSS feeds and posts a daily update to a Microsoft Teams channel, along with a monsoon advisory and fun traffic trivia.  
It runs twice a day — at **8:30 AM IST** and **4:00 PM IST** — via **GitHub Actions**.

---

## 🚗 How It Works

- Scrapes fresh traffic news for Pune from Google News RSS.
- Posts updates to a Teams channel using a secure Incoming Webhook.
- Keeps track of already-posted news to avoid repeats.
- Adds seasonal info (like monsoon safety tips) and traffic trivia.
- Runs fully automated on GitHub Actions — no paid server required!

---

## 📌 Tech Stack

- **Python 3.11**
- **GitHub Actions** for automation
- **Microsoft Teams Incoming Webhook** for posting
- **Google News RSS Feed**

---

## ⚠️ Security Note

🔐 **No secrets are stored in the codebase.**  
The webhook URL is injected at runtime using GitHub Actions **Secrets**.  
**Never commit your webhook or other secrets to your repo!**

---

## 💡 How to Use

1. Fork or clone the repo.
2. Add your **Teams Incoming Webhook URL** as a GitHub Secret named `WEBHOOK_URL`.
3. Adjust the `cron` schedule in `.github/workflows/main.yml` if you want different times.
4. Customize your news query or trivia list in `pune_traffic_alerts.py` as needed.
5. Deploy — that’s it! 🎉

---

## 📝 License

This is a **personal, open-source project** — feel free to fork, adapt, and improve it.  
Licensed under the MIT License.

---

## 🙌 Contributing

Have ideas to make it better?  
PRs and suggestions are always welcome!

---

## 📣 Disclaimer

This project is **not an official product** of any company.  
It’s a personal initiative by [Ramesh0708](https://github.com/Ramesh0708) to make life a bit easier for commuters!

---

**Stay safe. Drive smart. 🛣️**
