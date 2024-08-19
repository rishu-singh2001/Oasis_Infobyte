import pyttsx3
import speech_recognition as sr
import smtplib
from email.message import EmailMessage
import requests
import threading
import time

# Initialize text-to-speech engine
engine = pyttsx3.init()


def speak(text):
    engine.say(text)
    engine.runAndWait()


def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"Command: {command}")
            return command
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand that.")
            return None
        except sr.RequestError:
            speak("Sorry, I'm having trouble connecting to the service.")
            return None


def send_email(to_email, subject, body):
    EMAIL_ADDRESS = "your_email@example.com"
    EMAIL_PASSWORD = "your_password"

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.example.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            speak("Email sent successfully.")
    except Exception as e:
        speak(f"Failed to send email: {e}")


def get_weather(city):
    API_KEY = "your_openweathermap_api_key"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if data.get("cod") != 200:
        speak("Sorry, I couldn't get the weather information.")
        return

    weather = data["weather"][0]["description"]
    temperature = data["main"]["temp"]
    speak(f"The current weather in {city} is {weather} with a temperature of {temperature} degrees Celsius.")


def set_reminder(reminder_time, message):
    def reminder():
        time.sleep(reminder_time * 60)
        speak(f"Reminder: {message}")

    threading.Thread(target=reminder).start()


def handle_command(command):
    if "send email" in command:
        speak("Who should I send the email to?")
        to_email = listen()
        if to_email:
            speak("What is the subject of the email?")
            subject = listen()
            if subject:
                speak("What is the body of the email?")
                body = listen()
                if body:
                    send_email(to_email, subject, body)
    elif "weather" in command:
        speak("Which city?")
        city = listen()
        if city:
            get_weather(city)
    elif "set reminder" in command:
        speak("What should the reminder say?")
        message = listen()
        if message:
            speak("In how many minutes should I remind you?")
            try:
                reminder_time = int(listen())
                set_reminder(reminder_time, message)
            except (ValueError, TypeError):
                speak("Please provide a valid number of minutes.")
    elif "stop" in command:
        speak("Goodbye!")
        return False
    else:
        speak("Sorry, I didn't understand that.")
    return True


def main():
    speak("Hello! How can I assist you today?")
    while True:
        command = listen()
        if command:
            if not handle_command(command.lower()):
                break


if __name__ == "__main__":
    main()
