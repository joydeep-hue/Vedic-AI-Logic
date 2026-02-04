import time
import random

# THE INTEGRATED VEDIC SYSTEM (WEEK 2 FINAL)

class PAI_Oracle:
    def __init__(self, key):
        self.key = key
        self.memory = [None] * 3 # Akashic Buffer (Size 3)
        self.ptr = 0

    def encrypt_data(self, text): # Maya-Mask
        return "".join(chr(ord(c) + (self.key % 5)) for c in text)

    def karma_check(self, effort, result): # Karma-Engine
        score = result / (effort + 1)
        return "HIGH DHARMA" if score > 1 else "LOW ENERGY"

    def run_cycle(self, task_name, effort, result):
        print(f"\n--- Processing: {task_name} ---")
        
        # 1. Evaluate Karma
        status = self.karma_check(effort, result)
        
        # 2. Encrypt the Result
        secret_log = self.encrypt_data(f"{task_name}: {status}")
        
        # 3. Store in Akasha
        self.memory[self.ptr] = secret_log
        self.ptr = (self.ptr + 1) % len(self.memory)
        
        print(f"Status: {status} | Encrypted Log Saved to Akasha.")

# --- LAUNCH THE SYSTEM ---
my_oracle = PAI_Oracle(key=108)

# Simulating 3 days of work
my_oracle.run_cycle("Coding Vedic AI", effort=2, result=10)
time.sleep(1)
my_oracle.run_cycle("Social Media Scrolling", effort=4, result=1)
time.sleep(1)
my_oracle.run_cycle("Morning Meditation", effort=1, result=5)

print("\n--- FINAL AKASHIC BUFFER (ENCRYPTED) ---")
print(my_oracle.memory)
