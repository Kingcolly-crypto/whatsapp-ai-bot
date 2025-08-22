import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API key. Please add it to your .env file.")

# -------------------------------
# Initialize OpenAI client
# -------------------------------
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_ai_response(prompt: str) -> str:
    """Generate a response using OpenAI GPT model."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful WhatsApp assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating response: {str(e)}"

# -------------------------------
# Selenium Setup for WhatsApp Web
# -------------------------------
def setup_driver():
    """Set up Selenium WebDriver and open WhatsApp Web."""
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=whatsapp_profile")  # keeps login session
    driver = webdriver.Chrome(options=options)
    driver.get("https://web.whatsapp.com")
    print("🔑 Scan the QR code in the browser to log in to WhatsApp Web...")
    time.sleep(15)  # Wait for login
    return driver

# -------------------------------
# Main Bot Loop
# -------------------------------
def whatsapp_bot(target_name: str):
    """Continuously monitor and reply to a specific contact."""
    driver = setup_driver()

    print(f"🤖 Monitoring messages from: {target_name}")
    
    try:
        while True:
            try:
                # Find chat by contact name
                chat = driver.find_element(By.XPATH, f'//span[@title="{target_name}"]')
                chat.click()
                time.sleep(2)

                # Get last message
                messages = driver.find_elements(By.CSS_SELECTOR, "span.selectable-text")
                if messages:
                    last_message = messages[-1].text
                    print(f"{target_name}: {last_message}")

                    # Generate AI response
                    ai_reply = generate_ai_response(last_message)
                    print(f"Bot: {ai_reply}")

                    # Send reply
                    input_box = driver.find_element(By.XPATH, '//div[@title="Type a message"]')
                    input_box.send_keys(ai_reply + Keys.ENTER)
                    time.sleep(3)
            except Exception as e:
                print("⚠️ Error inside loop:", e)
                time.sleep(5)
    except KeyboardInterrupt:
        print("🛑 Bot stopped manually.")
    finally:
        driver.quit()

# -------------------------------
# Run the bot
# -------------------------------
if __name__ == "__main__":
    contact_name = "Lady Nyx"  # 🔹 Change to the person you want to auto-reply to
    whatsapp_bot(contact_name)
