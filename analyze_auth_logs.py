import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

# Connect to your database
conn = psycopg2.connect(
    host="localhost",
    database="cyber_db",
    user="postgres",  # or your custom user
    password="postgres"
)

# Fetch failed login attempts
query = """
SELECT ip_address, timestamp
FROM auth_logs
WHERE login_result = 'failure';
"""

df = pd.read_sql(query, conn)
conn.close()

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Round timestamps to the nearest minute
df['minute'] = df['timestamp'].dt.floor('min')

# Count failed attempts per IP per minute
grouped = df.groupby(['ip_address', 'minute']).size().reset_index(name='failed_attempts')

# Filter brute-force candidates (5+ attempts in a minute)
brute_force = grouped[grouped['failed_attempts'] >= 1]

print("\n🔐 Potential Brute-force IPs:\n")
print(brute_force)

# Plot failed attempts per IP
top_ips = df['ip_address'].value_counts().head(5)
top_ips.plot(kind='bar', title='Top 5 IPs with Failed Logins')
plt.xlabel("IP Address")
plt.ylabel("Failed Attempts")
plt.tight_layout()
plt.show()




# Plotting
top_ips = df['ip_address'].value_counts().head(5)
top_ips.plot(kind='bar', title='Top 5 IPs with Failed Logins')
plt.xlabel("IP Address")
plt.ylabel("Failed Attempts")
plt.tight_layout()
plt.show()

# ----------- GEO-MAPPING BLOCK START ------------

import requests
import time
import folium

unique_ips = brute_force['ip_address'].unique()

locations = []

for ip in unique_ips:
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,city,lat,lon")
        data = response.json()
        if data['status'] == 'success':
            locations.append({
                'ip': ip,
                'country': data['country'],
                'city': data['city'],
                'lat': data['lat'],
                'lon': data['lon']
            })
        else:
            print(f"Location not found for IP: {ip}")
        time.sleep(1)
    except Exception as e:
        print(f"Error getting location for IP {ip}: {e}")

if locations:
    first_loc = locations[0]
    m = folium.Map(location=[first_loc['lat'], first_loc['lon']], zoom_start=2)
    
    for loc in locations:
        folium.Marker(
            location=[loc['lat'], loc['lon']],
            popup=f"IP: {loc['ip']}<br>City: {loc['city']}<br>Country: {loc['country']}"
        ).add_to(m)
    
    m.save("attackers_map.html")
    print("Map saved as attackers_map.html - open this in your browser to view.")
else:
    print("No locations found for suspicious IPs.")


# ----------- GEO-MAPPING BLOCK END ------------




#------------ Schedule the script to run daily and email you the report BLOCK START ----------------

# import smtplib
# from email.message import EmailMessage
# import ssl

# # Configure your email details
# sender_email = "panchwaghpranav13@gmail.com"
# receiver_email = "panchwaghpranav46@gmail.com"
# app_password = "rhowsidhhlftvpok"

# # Create the email message

# # print("Connecting to Gmail SMTP server...")
# # with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
# #     smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
# #     print("Logged in. Sending email...")
# #     smtp.send_message(msg)
# #     print("Email sent successfully.")


# msg = EmailMessage()
# msg['Subject'] = 'Daily Auth Log Report'
# msg['From'] = sender_email
# msg['To'] = receiver_email
# msg.set_content("Attached are today's failed login report and location map.")

# # Attach the chart image
# with open("Figure_1.png", "rb") as img:
#     msg.add_attachment(img.read(), maintype='image', subtype='png', filename="top_failed_ips.png")

# # Attach the map HTML file
# with open("attackers_map.html", "rb") as map_file:
#     msg.add_attachment(map_file.read(), maintype='text', subtype='html', filename="attackers_map.html")

# # Send the email
# context = ssl.create_default_context()
# with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
#     smtp.login(sender_email, app_password)
#     smtp.send_message(msg)

# print("Email sent successfully.")


# import os
# print("Checking attachments...")
# print("Figure_1.png:", os.path.exists('Figure_1.png'))
# print("attackers_map.html:", os.path.exists('attackers_map.html'))

import smtplib
from email.message import EmailMessage
import os
import traceback

EMAIL_ADDRESS = "panchwaghpranav13@gmail.com"
EMAIL_PASSWORD = "rhowsidhhlftvpok"  # 16-digit app password (no spaces)

print("🔍 Checking attachments...")
print("Figure_1.png exists:", os.path.exists("Figure_1.png"))
print("attackers_map.html exists:", os.path.exists("attackers_map.html"))

msg = EmailMessage()
msg['Subject'] = 'Daily Auth Log Report'
msg['From'] = EMAIL_ADDRESS
msg['To'] = 'panchwaghpranav13@gmail.com'
msg.set_content("Attached are today's top failed login IPs and the attacker geo-map.")

# Attach image
if os.path.exists('Figure_1.png'):
    with open('Figure_1.png', 'rb') as f:
        msg.add_attachment(f.read(), maintype='image', subtype='png', filename='Figure_1.png')

# Attach HTML map
if os.path.exists('attackers_map.html'):
    with open('attackers_map.html', 'rb') as f:
        msg.add_attachment(f.read(), maintype='text', subtype='html', filename='attackers_map.html')

try:
    print("📡 Connecting to Gmail SMTP server...")
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        print("✅ Login successful. Sending email...")
        smtp.send_message(msg)
        print("📧 Email sent successfully.")
except Exception as e:
    print("❌ Failed to send email.")
    traceback.print_exc()


#------------ Schedule the script to run daily and email you the report BLOCK END ----------------