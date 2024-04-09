from dotenv import load_dotenv
import os

load_dotenv()

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

print(f"{username} : {password}")