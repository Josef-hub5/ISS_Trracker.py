import requests
from datetime import datetime
import smtplib
import time

MY_EMAIL = "YOUR EMAIL"
MY_PASSWORD = "APP PASSWORD"  # Gmail app password
MY_LAT = 48.888288
MY_LONG = 16.157713

def is_iss_overhead():
    try:
        response = requests.get("http://api.open-notify.org/iss-now.json", timeout=10)
        response.raise_for_status()
        data = response.json()
        iss_latitude = float(data["iss_position"]["latitude"])
        iss_longitude = float(data["iss_position"]["longitude"])
        print(f"ISS souřadnice: Lat: {iss_latitude}, Long: {iss_longitude}")

        # Ověřte, zda je ISS nad vámi
        if MY_LAT - 5 <= iss_latitude <= MY_LAT + 5 and MY_LONG - 5 <= iss_longitude <= MY_LONG + 5:
            print("ISS je nad vámi.")
            return True
        else:
            print("ISS není nad vámi.")
            return False
    except Exception as e:
        print(f"Chyba při získávání polohy ISS: {e}")
        return False

def is_night():
    try:
        parameters = {
            "lat": MY_LAT,
            "lng": MY_LONG,
            "formatted": 0,
        }
        response = requests.get("https://api.sunrise-sunset.org/json", params=parameters, timeout=10)
        response.raise_for_status()
        data = response.json()

        sunrise_utc = datetime.fromisoformat(data["results"]["sunrise"]).hour
        sunset_utc = datetime.fromisoformat(data["results"]["sunset"]).hour

        time_now_utc = datetime.utcnow().hour
        print(f"Sunrise UTC: {sunrise_utc}, Sunset UTC: {sunset_utc}, Current UTC time: {time_now_utc}")
        if time_now_utc >= sunset_utc or time_now_utc <= sunrise_utc:
            print("Je noc.")
            return True
        else:
            print("Není noc.")
            return False
    except Exception as e:
        print(f"Chyba při získávání informací o východu/západu slunce: {e}")
        return False

while True:
    time.sleep(60)  # Počkáme 60 sekund
    if is_iss_overhead() and is_night():
        try:
            print("Podmínky splněny, odesílám e-mail...")
            # Odesílání e-mailu
            with smtplib.SMTP("smtp.gmail.com", 587) as connection:
                connection.starttls()
                connection.login(MY_EMAIL, MY_PASSWORD)
                connection.sendmail(
                    from_addr=MY_EMAIL,
                    to_addrs=MY_EMAIL,
                    msg="Subject:Look Up!\n\nThe ISS is above you in the sky"
                )
            print("E-mail byl úspěšně odeslán!")
        except Exception as e:
            print(f"Chyba při odesílání e-mailu: {e}")
    else:
        print("Podmínky pro odeslání e-mailu nejsou splněny.")