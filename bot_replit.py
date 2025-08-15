import discord
from discord.ext import commands
from discord import app_commands
import random, time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple
from io import BytesIO
import aiohttp
import os
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def _run_web():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=_run_web, daemon=True)
    t.start()



intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree
start_time = time.time()

# Data
EIGHTBALL = [
    "It is certain.",
    "Without a doubt.",
    "Yes – definitely.",
    "Reply hazy, try again.",
    "Ask again later.",
    "Don't count on it.",
    "My reply is no.",
    "Very doubtful.",
    "Absolutely!",
    "Not in a million years.",
    "Possibly.",
    "The future is unclear.",
    "Yes, in due time.",
    "You may rely on it.",
    "Concentrate and ask again.",
    "Cannot predict now.",
    "Outlook good.",
    "Signs point to yes.",
    "Better not tell you now.",
    "Outlook not so good.",
    "Yes – if you believe.",
    "Chances are high.",
    "It is decidedly so.",
    "Ask and it shall be revealed.",
    "Definitely not.",
    "I’m leaning towards yes.",
    "I’m leaning towards no.",
    "The answer is yes.",
    "The answer is no.",
    "Possibly, but unlikely.",
    "You will have to wait and see.",
    "Absolutely not.",
    "Focus and try again.",
    "Yes, but with caution.",
    "No, but try again later.",
    "All signs say yes.",
    "All signs say no.",
    "Your future looks bright.",
    "Your future is cloudy.",
    "It is likely.",
    "It is unlikely.",
    "Yes, without hesitation.",
    "No, without hesitation.",
    "Concentrate… Yes.",
    "Concentrate… No.",
    "Yes, for certain.",
    "No, for certain.",
    "It is unclear at the moment.",
    "Yes, but be careful.",
    "No, but things may change.",
    "Definitely yes.",
    "Definitely no.",
    "Cannot answer now.",
    "Perhaps.",
    "Possibly not.",
    "It is doubtful.",
    "It is likely to happen.",
    "The stars say yes.",
    "The stars say no.",
    "Yes, but only if you try.",
    "No, unless you change your approach.",
    "Ask again after some time.",
    "It may happen.",
    "It may not happen.",
    "Yes, absolutely.",
    "No, absolutely not.",
    "The outcome is positive.",
    "The outcome is negative.",
    "Yes, without a doubt.",
    "No, without a doubt.",
    "Signs point to uncertainty.",
    "Yes, the odds are in your favor.",
    "No, the odds are against you.",
    "You can count on it.",
    "You cannot count on it.",
    "Yes, the answer is clear.",
    "No, the answer is clear.",
    "It is probable.",
    "It is improbable.",
    "Yes, for sure.",
    "No, for sure.",
    "All will be revealed soon.",
    "Not at this time.",
    "Yes, with confidence.",
    "No, with confidence.",
    "Focus on your question again.",
    "Yes, as expected.",
    "No, as expected.",
    "It is written in the stars.",
    "The answer may surprise you.",
    "Yes, the timing is right.",
    "No, the timing is wrong.",
    "Yes, but patience is required.",
    "No, but persistence pays.",
    "It is favored.",
    "It is not favored.",
    "Yes, without hesitation or doubt.",
    "No, without hesitation or doubt.",
    "The outcome is promising.",
    "The outcome is discouraging.",
    "Yes, the universe agrees.",
    "No, the universe disagrees.",
    "Yes, in every way.",
    "No, in every way."
]

QUOTES = [
    "The best way to get started is to quit talking and begin doing.",
    "Dream bigger. Do bigger.",
    "Push yourself, because no one else is going to do it for you.",
    "Success is not in what you have, but who you are.",
    "Opportunities don't happen, you create them.",
    "Believe you can and you're halfway there.",
    "Don’t watch the clock; do what it does. Keep going.",
    "The harder you work for something, the greater you’ll feel when you achieve it.",
    "Don’t stop when you’re tired. Stop when you’re done.",
    "Little things make big days.",
    "It always seems impossible until it’s done.",
    "Don’t wait for opportunity. Create it.",
    "Sometimes we’re tested not to show our weaknesses, but to discover our strengths.",
    "Great things never come from comfort zones.",
    "Dream it. Wish it. Do it.",
    "Push yourself because no one else is going to do it for you.",
    "Success doesn’t just find you. You have to go out and get it.",
    "The key to success is to focus on goals, not obstacles.",
    "Don’t limit your challenges. Challenge your limits.",
    "Believe in yourself and all that you are.",
    "Do something today that your future self will thank you for.",
    "Success is the sum of small efforts repeated day in and day out.",
    "The only way to achieve the impossible is to believe it is possible.",
    "Don’t wait for the right moment. Take the moment and make it right.",
    "Success is not final, failure is not fatal: it is the courage to continue that counts.",
    "Wake up with determination. Go to bed with satisfaction.",
    "You don’t have to be great to start, but you have to start to be great.",
    "If you believe it will work out, you’ll see opportunities.",
    "The secret of getting ahead is getting started.",
    "You are stronger than you think.",
    "Start where you are. Use what you have. Do what you can.",
    "Don’t be pushed around by the fears in your mind. Be led by the dreams in your heart.",
    "Work hard in silence. Let success make the noise.",
    "Your limitation—it’s only your imagination.",
    "Sometimes later becomes never. Do it now.",
    "Don’t count the days. Make the days count.",
    "The best revenge is massive success.",
    "Your life does not get better by chance, it gets better by change.",
    "It’s going to be hard, but hard does not mean impossible.",
    "The pain you feel today will be the strength you feel tomorrow.",
    "Do what you can with all you have, wherever you are.",
    "Don’t wait. The time will never be just right.",
    "Hustle until your haters ask if you’re hiring.",
    "Great things take time.",
    "Do one thing every day that scares you.",
    "Small steps in the right direction can turn out to be the biggest step of your life.",
    "Success usually comes to those who are too busy to be looking for it.",
    "If you want it, work for it.",
    "The only place where success comes before work is in the dictionary.",
    "Don’t stop until you’re proud.",
    "Work hard, stay positive, and get up early. It’s the best part of the day.",
    "Be the energy you want to attract.",
    "Your dreams don’t work unless you do.",
    "Fall seven times and stand up eight.",
    "Don’t wish it were easier. Wish you were better.",
    "Be fearless in the pursuit of what sets your soul on fire.",
    "Do what is right, not what is easy nor what is popular.",
    "Your mind is a powerful thing. When you fill it with positive thoughts, your life will start to change.",
    "Don’t let yesterday take up too much of today.",
    "The future belongs to those who believe in the beauty of their dreams.",
    "You are capable of more than you know.",
    "It’s never too late to be what you might have been.",
    "Work until your idols become rivals.",
    "Doubt kills more dreams than failure ever will.",
    "Opportunities are usually disguised as hard work.",
    "The harder the conflict, the greater the triumph.",
    "Do what you love and you’ll never work a day in your life.",
    "Your passion is waiting for your courage to catch up.",
    "Magic is believing in yourself. If you can make that happen, you can make anything happen.",
    "Success is liking yourself, liking what you do, and liking how you do it.",
    "The only limit to our realization of tomorrow is our doubts of today.",
    "Don’t be afraid to give up the good to go for the great.",
    "Success is walking from failure to failure with no loss of enthusiasm.",
    "Believe in the power of yet. You’re not there yet, but you will be.",
    "The best way to predict the future is to create it.",
    "You don’t have to see the whole staircase, just take the first step.",
    "Motivation is what gets you started. Habit is what keeps you going.",
    "Success isn’t always about greatness. It’s about consistency.",
    "Start each day with a positive thought and a grateful heart.",
    "Don’t let what you cannot do interfere with what you can do.",
    "Hustle in silence and let your success make the noise.",
    "A year from now you may wish you had started today.",
    "Action is the foundational key to all success.",
    "What you get by achieving your goals is not as important as what you become by achieving your goals.",
    "You don’t need to be perfect to be amazing.",
    "Do not wait to strike till the iron is hot; but make it hot by striking.",
    "Push yourself to do better than yesterday.",
    "Success is the result of preparation, hard work, and learning from failure.",
    "Don’t be busy, be productive.",
    "The way to get started is to quit talking and begin doing.",
    "Your attitude, not your aptitude, will determine your altitude.",
    "Make each day your masterpiece.",
    "What seems to us as bitter trials are often blessings in disguise.",
    "The harder you fall, the higher you bounce.",
    "Opportunities don’t happen. You create them.",
    "Do not wait; the time will never be ‘just right.’",
    "Keep going. Everything you need will come to you at the perfect time.",
    "Believe in your infinite potential.",
    "Failure is not the opposite of success. It’s part of success.",
    "Success is not in what you have, but who you are.",
    "Don’t fear failure. Fear being in the exact same place next year as you are today.",
    "Great things never come from comfort zones.",
    "Dream it. Wish it. Do it.",
    "Push yourself because no one else is going to do it for you."
]

TRIVIA = [
    ("What’s the capital of France?", "Paris"),
    ("What year did the Titanic sink?", "1912"),
    ("Who wrote 'Hamlet'?", "William Shakespeare"),
    ("What is the smallest prime number?", "2"),
    ("How many continents are there?", "7"),
    ("What is the largest planet in our solar system?", "Jupiter"),
    ("What is the chemical symbol for water?", "H2O"),
    ("Who painted the Mona Lisa?", "Leonardo da Vinci"),
    ("Which element has the atomic number 1?", "Hydrogen"),
    ("What is the fastest land animal?", "Cheetah"),
    ("Who discovered penicillin?", "Alexander Fleming"),
    ("What is the square root of 64?", "8"),
    ("What year did World War II end?", "1945"),
    ("Which country is known as the Land of the Rising Sun?", "Japan"),
    ("What is the currency of the United Kingdom?", "Pound Sterling"),
    ("Who wrote '1984'?", "George Orwell"),
    ("What is the largest ocean on Earth?", "Pacific Ocean"),
    ("Which planet is known as the Red Planet?", "Mars"),
    ("Who invented the telephone?", "Alexander Graham Bell"),
    ("What is the hardest natural substance?", "Diamond"),
    ("Which country has the largest population?", "China"),
    ("What is the capital of Italy?", "Rome"),
    ("What gas do plants absorb from the atmosphere?", "Carbon Dioxide"),
    ("Who was the first president of the United States?", "George Washington"),
    ("Which organ purifies blood in the human body?", "Kidney"),
    ("What is the tallest mountain in the world?", "Mount Everest"),
    ("Which continent is the Sahara Desert located in?", "Africa"),
    ("Who wrote 'Pride and Prejudice'?", "Jane Austen"),
    ("What is the boiling point of water in Celsius?", "100"),
    ("Which planet has the most moons?", "Saturn"),
    ("Who painted the ceiling of the Sistine Chapel?", "Michelangelo"),
    ("What is the main ingredient in guacamole?", "Avocado"),
    ("Which animal is known as the Ship of the Desert?", "Camel"),
    ("What is the chemical symbol for gold?", "Au"),
    ("Who discovered gravity when an apple fell on his head?", "Isaac Newton"),
    ("What is the largest mammal in the world?", "Blue Whale"),
    ("Which country gifted the Statue of Liberty to the USA?", "France"),
    ("Who is known as the Father of Computers?", "Charles Babbage"),
    ("Which element is represented by 'O' on the periodic table?", "Oxygen"),
    ("What is the longest river in the world?", "Nile"),
    ("Which planet is closest to the sun?", "Mercury"),
    ("Who wrote 'The Odyssey'?", "Homer"),
    ("What is the primary language spoken in Brazil?", "Portuguese"),
    ("Which organ is responsible for pumping blood?", "Heart"),
    ("What is the largest desert in the world?", "Antarctic Desert"),
    ("Which country is famous for the kangaroo?", "Australia"),
    ("What is the smallest country in the world?", "Vatican City"),
    ("Which continent is India located in?", "Asia"),
    ("Who painted 'Starry Night'?", "Vincent van Gogh"),
    ("What is the chemical formula for table salt?", "NaCl"),
    ("Which planet is known for its rings?", "Saturn"),
    ("Who invented the light bulb?", "Thomas Edison"),
    ("What is the capital of Germany?", "Berlin"),
    ("Which gas do humans inhale to survive?", "Oxygen"),
    ("Who wrote 'To Kill a Mockingbird'?", "Harper Lee"),
    ("What is the largest island in the world?", "Greenland"),
    ("Which blood type is known as the universal donor?", "O negative"),
    ("Which country is known for the Eiffel Tower?", "France"),
    ("What is the largest bone in the human body?", "Femur"),
    ("Which planet is known as the Morning Star?", "Venus"),
    ("Who discovered electricity using a kite?", "Benjamin Franklin"),
    ("What is the chemical symbol for iron?", "Fe"),
    ("Which country is known for sushi?", "Japan"),
    ("Who was the first person to walk on the Moon?", "Neil Armstrong"),
    ("What is the fastest bird in the world?", "Peregrine Falcon"),
    ("Which element has the atomic number 79?", "Gold"),
    ("What is the tallest building in the world?", "Burj Khalifa"),
    ("Who wrote 'The Catcher in the Rye'?", "J.D. Salinger"),
    ("Which continent has the most countries?", "Africa"),
    ("What is the most spoken language in the world?", "English"),
    ("Which ocean is the smallest?", "Arctic Ocean"),
    ("Who painted 'The Last Supper'?", "Leonardo da Vinci"),
    ("What is the main gas found in the Earth's atmosphere?", "Nitrogen"),
    ("Which planet is farthest from the sun?", "Neptune"),
    ("Who is the Greek god of the sea?", "Poseidon"),
    ("What is the freezing point of water in Celsius?", "0"),
    ("Which country is known as the Land of the Midnight Sun?", "Norway"),
    ("Who wrote 'Macbeth'?", "William Shakespeare"),
    ("Which mammal lays eggs?", "Platypus"),
    ("What is the capital of Canada?", "Ottawa"),
    ("Which organ is used for hearing?", "Ear"),
    ("Who discovered America?", "Christopher Columbus"),
    ("Which planet is called the Blue Planet?", "Earth"),
    ("What is the chemical symbol for silver?", "Ag"),
    ("Which country is famous for the Great Wall?", "China"),
    ("Who is known as the Bard of Avon?", "William Shakespeare"),
    ("What is the speed of light in vacuum (km/s)?", "299792"),
    ("Which organ produces insulin?", "Pancreas"),
    ("Which gas do humans exhale?", "Carbon Dioxide"),
    ("Who invented the printing press?", "Johannes Gutenberg"),
    ("What is the capital of Australia?", "Canberra"),
    ("Which planet is famous for its Great Red Spot?", "Jupiter"),
    ("Who is the author of 'Harry Potter' series?", "J.K. Rowling"),
    ("What is the chemical formula for carbon dioxide?", "CO2"),
    ("Which animal is known for its black-and-white stripes?", "Zebra"),
    ("What is the largest volcano in the world?", "Mauna Loa"),
    ("Who painted 'Girl with a Pearl Earring'?", "Johannes Vermeer"),
    ("Which country has the maple leaf on its flag?", "Canada"),
    ("Which metal has the highest melting point?", "Tungsten"),
    ("Who is the Norse god of thunder?", "Thor"),
    ("Which river flows through Egypt?", "Nile"),
    ("What is the chemical symbol for potassium?", "K"),
    ("Which bird is a symbol of peace?", "Dove"),
    ("Who wrote 'The Iliad'?", "Homer"),
    ("Which continent is also a country?", "Australia"),
    ("Which animal is known as the King of the Jungle?", "Lion")
]

FACTS = [
    "Bananas are berries, but strawberries aren’t.",
    "Octopuses have three hearts.",
    "Honey never spoils.",
    "Sharks existed before trees.",
    "A day on Venus is longer than its year.",
    "There are more stars in the universe than grains of sand on Earth.",
    "Sloths can hold their breath longer than dolphins.",
    "Water can boil and freeze at the same time under certain conditions.",
    "A group of flamingos is called a 'flamboyance'.",
    "Butterflies can taste with their feet.",
    "Sea otters hold hands while sleeping to keep from drifting apart.",
    "Wombat poop is cube-shaped.",
    "Cows have best friends and get stressed when separated.",
    "There are more fake flamingos in the world than real ones.",
    "The unicorn is the national animal of Scotland.",
    "A day on Mercury lasts about 59 Earth days.",
    "Pineapples take about two years to grow.",
    "Sharks can live up to 500 years.",
    "Sloths can rotate their heads almost all the way around.",
    "The fingerprints of a koala are so similar to humans that they can confuse crime scene investigators.",
    "A group of crows is called a 'murder'.",
    "Octopuses have three hearts and blue blood.",
    "There’s enough DNA in the human body to stretch from the sun to Pluto and back.",
    "Butterflies can see red, green, and yellow but also can detect ultraviolet light.",
    "Tardigrades can survive in space.",
    "An ostrich’s eye is bigger than its brain.",
    "Sharks existed before trees did.",
    "Some turtles can breathe through their butts.",
    "The heart of a shrimp is located in its head.",
    "Sloths can turn their heads almost 270 degrees.",
    "There’s a species of jellyfish that is immortal.",
    "Elephants can’t jump.",
    "Cats have fewer toes on their back paws.",
    "Giraffes have no vocal cords.",
    "Koalas sleep up to 22 hours a day.",
    "A day on Saturn lasts about 10.7 hours.",
    "Rats laugh when tickled.",
    "Otters have a favorite rock they use to crack open shells.",
    "The largest snowflake ever recorded was 15 inches wide.",
    "There are more trees on Earth than stars in the Milky Way.",
    "Sea cucumbers fight off predators by ejecting their internal organs.",
    "Crows can recognize human faces.",
    "Dolphins have names for each other.",
    "Some fish can climb trees.",
    "Humans share 60% of their DNA with bananas.",
    "A bolt of lightning contains enough energy to toast 100,000 slices of bread.",
    "The longest-living animal is the quahog clam, which can live over 500 years.",
    "Sharks can detect one drop of blood in 25 gallons of water.",
    "Sloths can hold their breath for up to 40 minutes.",
    "A group of owls is called a 'parliament'.",
    "Sea slugs can incorporate other animals’ stinging cells into their own bodies.",
    "Butterflies can see smells.",
    "The tongue of a blue whale weighs as much as an elephant.",
    "Some frogs can freeze solid and thaw alive.",
    "An adult human has fewer bones than a baby.",
    "The Eiffel Tower can be 15 cm taller during the summer.",
    "Penguins propose with pebbles.",
    "Sharks existed before trees.",
    "Honeybees can recognize human faces.",
    "Octopuses have nine brains.",
    "A snail can sleep for three years.",
    "The fingerprints of a koala are almost identical to humans.",
    "Sloths are excellent swimmers.",
    "Elephants can communicate through infrasound.",
    "The human nose can detect over 1 trillion scents.",
    "Some plants can move on their own without soil.",
    "Sharks can go into a trance if flipped upside down.",
    "Sea stars can regenerate lost arms.",
    "Wombats can run up to 40 km/h.",
    "A cockroach can live for weeks without its head.",
    "Dolphins sleep with one eye open.",
    "Some lizards can squirt blood from their eyes.",
    "Cows can produce more milk when listening to music.",
    "Sloths can hold their breath longer than dolphins.",
    "The world's largest desert is Antarctica.",
    "Owls can rotate their heads 270 degrees.",
    "Some species of bamboo can grow over 3 feet in 24 hours.",
    "Elephants are pregnant for nearly 2 years.",
    "A hummingbird’s heart can beat up to 1,260 times per minute.",
    "The fingerprints of a koala are so similar to humans they can confuse investigators.",
    "Sharks are older than trees.",
    "Pineapples were named for their resemblance to pine cones.",
    "Sea otters have a pouch under their forearm to store food.",
    "The giant squid has the largest eyes in the animal kingdom.",
    "Some turtles can breathe through their butts.",
    "Octopuses can change color in the blink of an eye.",
    "Sloths can turn their heads almost all the way around.",
    "Honey never spoils.",
    "A group of flamingos is called a 'flamboyance'.",
    "Octopuses have three hearts.",
    "Sharks existed before trees.",
    "A day on Venus is longer than its year.",
    "Bananas are berries, but strawberries aren’t.",
    "The longest recorded flight of a chicken is 13 seconds.",
    "There are more stars in the universe than grains of sand on Earth.",
    "Sloths can hold their breath longer than dolphins.",
    "Water can boil and freeze at the same time under certain conditions.",
    "Butterflies can taste with their feet.",
    "Sea otters hold hands while sleeping.",
    "Wombat poop is cube-shaped.",
    "Cows have best friends and get stressed when separated.",
    "The unicorn is the national animal of Scotland.",
    "A day on Mercury lasts about 59 Earth days.",
    "Pineapples take about two years to grow.",
    "Sharks can live up to 500 years.",
    "Sloths can rotate their heads almost all the way around."
]

ROASTS = [
    "I’d explain it to you, but I left my crayons at home.",
    "You bring everyone so much joy… when you leave the room.",
    "You have something that no one else has. A lot of bad luck.",
    "Sorry, I can’t think of an insult dumb enough for you to understand.",
    "There’s somebody out there for everybody. For you, it’s a psychiatrist.",
    "I consider you my sun. Now please get 93 million miles away from here.",
    "Stupidity isn’t a crime, so you’re free to go.",
    "You must have been born on a highway because that’s where most accidents happen.",
    "Mirrors can’t talk. Lucky for you, they can’t laugh, either.",
    "I’ve seen salads that dress better than you.",
    "I have 90 billion nerves, and you’ve gotten on every single one of them.",
    "You don’t need to fear success. There is really nothing for you to worry about."
]


# DM session storage
active_dm_sessions: Dict[int, discord.User] = {}
session_transcripts: Dict[Tuple[int, int], List[str]] = {}

def session_key(a: int, b: int) -> Tuple[int, int]:
    return (a, b) if a < b else (b, a)

def ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

# ---------------- Slash Commands ---------------- #

@tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! `{latency}ms`")

@tree.command(name="eightball", description="Ask the magic 8-ball")
async def eightball(interaction: discord.Interaction, question: str):
    await interaction.response.send_message(f"🎱 {random.choice(EIGHTBALL)}")

@tree.command(name="quote", description="Send a random inspirational quote")
async def quote(interaction: discord.Interaction):
    await interaction.response.send_message(f"💬 {random.choice(QUOTES)}")

@tree.command(name="trivia", description="Ask a trivia question")
async def trivia(interaction: discord.Interaction):
    q, a = random.choice(TRIVIA)
    await interaction.response.send_message(f"❓ {q}\n||Answer: {a}||")

@tree.command(name="dailyfact", description="Share a random fact")
async def dailyfact(interaction: discord.Interaction):
    await interaction.response.send_message(f"📅 {random.choice(FACTS)}")

@tree.command(name="ship", description="Compatibility score between two users")
async def ship(interaction: discord.Interaction, user1: discord.Member, user2: discord.Member):
    score = random.randint(0, 100)
    await interaction.response.send_message(f"💖 {user1.mention} + {user2.mention} = **{score}%**")

@tree.command(name="roast", description="Send a random roast to a user")
async def roast(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(f"🔥 {member.mention}, {random.choice(ROASTS)}")

@tree.command(name="uptime", description="Show bot uptime")
async def uptime(interaction: discord.Interaction):
    delta = time.time() - start_time
    hrs, rem = divmod(int(delta), 3600)
    mins, secs = divmod(rem, 60)
    await interaction.response.send_message(f"⏱️ Uptime: {hrs}h {mins}m {secs}s")

# ---------------- Invite ---------------- #

import discord
from discord.ext import commands
import re

@tree.command(name="invite", description="Send a server invite to someone via DM")
async def invite(interaction: discord.Interaction, user: discord.User):
    if user.id == interaction.user.id:
        return await interaction.response.send_message("❌ You cannot invite yourself.", ephemeral=True)

    # Case 1: Command used in a guild
    if interaction.guild:
        try:
            invite_link = await interaction.channel.create_invite(max_age=3600, max_uses=1, unique=True)
        except discord.Forbidden:
            return await interaction.response.send_message("❌ I don't have permission to create invites.", ephemeral=True)
        
        try:
            await user.send(f"📩 **{interaction.user.display_name}** invited you to **{interaction.guild.name}**!\nInvite (1 hour, single-use): {invite_link.url}")
            await interaction.response.send_message(f"✅ Invite sent to **{user.display_name}** via DM.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("⚠️ Could not DM the user — they may have DMs disabled.", ephemeral=True)

    # Case 2: Command used outside a guild (DM)
    else:
        await interaction.response.send_message(
            "⚠️ You are not in a server. Please provide a server invite code or full link to send to the user.",
            ephemeral=True
        )

        def check(m):
            return m.author == interaction.user and isinstance(m.channel, discord.DMChannel)

        try:
            msg = await interaction.client.wait_for("message", check=check, timeout=60)
            invite_input = msg.content.strip()

            # Extract invite code if user provided full link
            match = re.search(r"(?:https?://)?discord\.gg/([A-Za-z0-9]+)", invite_input)
            invite_code = match.group(1) if match else invite_input

            invite_link = f"https://discord.gg/{invite_code}"

            # Validate the invite code
            try:
                await interaction.client.fetch_invite(invite_code)
                await user.send(f"📩 **{interaction.user.display_name}** sent you a server invite!\nInvite: {invite_link}")
                await interaction.followup.send(f"✅ Invite sent to **{user.display_name}** via DM.", ephemeral=True)
            except discord.NotFound:
                await interaction.followup.send("❌ The provided invite code is invalid or has expired.", ephemeral=True)
        except Exception:
            await interaction.followup.send("❌ Failed to send invite. Make sure the code or link is correct.", ephemeral=True)



from discord.ui import Button, View
from io import BytesIO

# ---------------- DM Mode ---------------- #
@tree.command(name="dm", description="Request a DM session with someone")
async def dm(interaction: discord.Interaction, user: discord.User):
    if user.id == interaction.user.id:
        return await interaction.response.send_message(
            "❌ You cannot start a DM session with yourself.", ephemeral=True
        )
    if interaction.user.id in active_dm_sessions:
        return await interaction.response.send_message(
            "ℹ️ You are already in a DM session.", ephemeral=True
        )
    if user.id in active_dm_sessions:
        return await interaction.response.send_message(
            f"ℹ️ {user.display_name} is already in a DM session.", ephemeral=True
        )

    # Create accept/decline buttons
    accept_button = Button(label="Accept", style=discord.ButtonStyle.green)
    decline_button = Button(label="Decline", style=discord.ButtonStyle.red)
    view = View()
    view.add_item(accept_button)
    view.add_item(decline_button)

    # Callback when accepted
    async def accept_callback(i: discord.Interaction):
        active_dm_sessions[interaction.user.id] = user
        active_dm_sessions[user.id] = interaction.user
        key = session_key(interaction.user.id, user.id)
        session_transcripts.setdefault(key, []).append(
            f"[{ts()}] — Session started between {interaction.user} and {user}"
        )

        await interaction.followup.send(
            f"✅ DM mode started with **{user.display_name}**. Use **/stopdm** to end.", ephemeral=True
        )
        await i.response.send_message(
            f"✅ You accepted the DM session with **{interaction.user.display_name}**.", ephemeral=True
        )

    # Callback when declined
    async def decline_callback(i: discord.Interaction):
        await i.response.send_message(
            f"❌ You declined the DM session request from **{interaction.user.display_name}**.", ephemeral=True
        )
        await interaction.followup.send(
            f"❌ **{user.display_name}** declined your DM session request.", ephemeral=True
        )

    accept_button.callback = accept_callback
    decline_button.callback = decline_callback

    try:
        await user.send(
            f"💬 **{interaction.user.display_name}** wants to start a DM session with you. Accept to start, or decline to cancel.",
            view=view
        )
        await interaction.response.send_message(
            f"ℹ️ DM request sent to **{user.display_name}**. Waiting for them to accept.", ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            f"⚠️ Could not send DM to **{user.display_name}** — they may have DMs disabled.", ephemeral=True
        )

# ---------------- Stop DM ---------------- #
@tree.command(name="stopdm", description="End your DM session and receive a transcript of your conversation")
async def stopdm(interaction: discord.Interaction):
    partner = active_dm_sessions.pop(interaction.user.id, None)
    if not partner:
        return await interaction.response.send_message(
            "ℹ️ You are not currently in a DM session.", ephemeral=True
        )

    # Remove partner's session too
    active_dm_sessions.pop(partner.id, None)

    # Get the transcript
    key = session_key(interaction.user.id, partner.id)
    lines = session_transcripts.pop(key, [])
    lines.append(f"[{ts()}] — Session ended by {interaction.user}")

    # Send transcript as a file
    content = "\n".join(lines)
    buf = BytesIO()
    buf.write(content.encode("utf-8"))
    buf.seek(0)
    file = discord.File(buf, filename="dm_transcript.txt")

    for u in [interaction.user, partner]:
        try:
            await u.send(file=file)
        except discord.Forbidden:
            pass

    await interaction.response.send_message(
        "✅ DM mode ended.", ephemeral=True
    )

# ---------------- Dismiss All ---------------- #
@tree.command(name="dismissall", description="Dismiss all ephemeral-style messages in your DMs")
async def dismissall(interaction: discord.Interaction):
    try:
        # Fetch the last 100 messages in the user's DM with the bot
        dm_channel = interaction.user.dm_channel
        if not dm_channel:
            dm_channel = await interaction.user.create_dm()

        deleted_count = 0
        async for msg in dm_channel.history(limit=100):
            # Only delete messages sent by the bot that have a View with Buttons
            if msg.author == interaction.client.user and msg.components:
                await msg.delete()
                deleted_count += 1

        await interaction.response.send_message(
            f"✅ Dismissed {deleted_count} message(s) in your DMs.", ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"⚠️ Failed to dismiss messages: {e}", ephemeral=True
        )

# ---------------- Info ---------------- #

from discord import Embed

@tree.command(name="info", description="Show all available bot commands")
async def info(interaction: discord.Interaction):
    embed = Embed(
        title="📖 Bot Command Guide",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )

    # 🎮 Fun / Interactive
    embed.add_field(
        name="🎮 Fun / Interactive",
        value=(
            "🎱 /eightball — Ask the magic 8-ball\n"
            "📜 /quote — Send a random inspirational quote\n"
            "🧠 /trivia — Ask a trivia question\n"
            "📚 /dailyfact — Share a random fact\n"
            "🚢 /ship — Compatibility score between two users\n"
            "🔥 /roast — Send a random roast to a user\n"
            "🔥 /roastdm — Send a DM roast to a user"
        ),
        inline=False
    )

    # 🧰 Utility / Tools
    embed.add_field(
        name="🧰 Utility / Tools",
        value=(
            "✉️ /invite — Send a server invite to someone via DM\n"
            "💬 /dm — Start DM mode with someone\n"
            "🛑 /stopdm — End your DM session and receive a transcript\n"
            "🏓 /ping — Check bot latency\n"
            "⏱️ /uptime — Show bot uptime\n"
            "🗑️ /dismissall — Dismiss all ephemeral-style messages in your DMs\n"
            "🧹 /clear — Delete a number of recent messages from this channel\n"
            "👤 /userinfo — Show detailed information about a user\n"
            "🌐 /serverinfo — Show information about this server\n"
            "🖼️ /avatar — Show a user's avatar"
        ),
        inline=False
    )

    # 🛡️ Moderation / Server Management
    embed.add_field(
        name="🛡️ Moderation / Server Management",
        value=(
            "⚠️ /warn — Warn a user with a reason\n"
            "📋 /warnpanel — View all current warnings\n"
            "🧽 /removewarn — Remove all warnings for a user\n"
            "🔨 /obliterate — Ban a user with optional reason\n"
            "👢 /boot — Kick a user with optional reason"
        ),
        inline=False
    )

    # ℹ️ Bot Info
    embed.add_field(
        name="ℹ️ Bot Info",
        value="📘 /info — Show all available bot commands",
        inline=False
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)


# ---------------- Clear Messages ---------------- #
@tree.command(name="clear", description="Delete a number of recent messages")
@app_commands.describe(amount="Number of messages to delete (max 100)")
async def clear(interaction: discord.Interaction, amount: int):
    if amount < 1 or amount > 100:
        return await interaction.response.send_message(
            "⚠️ Please provide a number between 1 and 100.", ephemeral=True
        )

    # Case 1: Command used in a guild
    if interaction.guild:
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message(
                "❌ You don't have permission to manage messages.", ephemeral=True
            )
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(
            f"✅ Deleted {len(deleted)} message(s).", ephemeral=True
        )

    # Case 2: Command used in DMs
    else:
        def is_bot(m):
            return m.author == interaction.client.user

        deleted = []
        async for msg in interaction.channel.history(limit=amount):
            if is_bot(msg):
                deleted.append(msg)
                await msg.delete()
        await interaction.response.send_message(
            f"✅ Deleted {len(deleted)} bot message(s).\n⚠️ The bot cannot delete your messages in DMs.", ephemeral=True
        )
BOT_LOGS_ID = 1405214678983905440

async def log_action(interaction: discord.Interaction, log_text: str):
    log_channel = interaction.guild.get_channel(BOT_LOGS_ID)
    if log_channel:
        await log_channel.send(log_text)

# ---------------- Obliterate (BAN) ---------------- #
@tree.command(name="obliterate", description="Ban a user with optional reason")
async def obliterate(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ You don’t have permission to ban members.", ephemeral=True)
    try:
        await member.ban(reason=reason)
        await interaction.response.send_message(
            f"🔨 {member.mention} has been banned. Reason: {reason or 'No reason provided.'}"
        )
        await log_action(interaction, f"[OBLITERATE_LOG] {interaction.guild.id} {member.id} {reason or 'No reason'}")
    except discord.Forbidden:
        await interaction.response.send_message("⚠️ I cannot ban this user.", ephemeral=True)

# ---------------- Boot (KICK) ---------------- #
@tree.command(name="boot", description="Kick a user with optional reason")
async def boot(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ You don’t have permission to kick members.", ephemeral=True)
    try:
        await member.kick(reason=reason)
        await interaction.response.send_message(
            f"👢 {member.mention} has been kicked. Reason: {reason or 'No reason provided.'}"
        )
        await log_action(interaction, f"[BOOT_LOG] {interaction.guild.id} {member.id} {reason or 'No reason'}")
    except discord.Forbidden:
        await interaction.response.send_message("⚠️ I cannot kick this user.", ephemeral=True)

# ---------------- Warning System ---------------- #
# This dictionary stores warnings in memory: { user_id: [reasons...] }
warnings: Dict[int, List[str]] = {}

# Helper: Get the guild's bot-log channel or default to current channel
def get_guild_log_channel(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    log_channel_id = guild_settings.get(guild_id, {}).get("bot_logs")
    if log_channel_id and log_channel_id != "none":
        return interaction.guild.get_channel(int(log_channel_id))
    return interaction.channel

# Helper: Log an action to bot-logs or fallback channel
async def log_action(interaction: discord.Interaction, log_text: str):
    log_channel = get_guild_log_channel(interaction)
    if log_channel:
        await log_channel.send(log_text)

# ---------------- Warning System ---------------- #

warnings: Dict[int, List[str]] = {}

async def rebuild_warnings(guild: discord.Guild):
    guild_id = str(guild.id)
    log_channel_id = guild_settings.get(guild_id, {}).get("bot_logs")
    if not log_channel_id or log_channel_id == "none":
        return
    log_channel = guild.get_channel(int(log_channel_id))
    if not log_channel:
        return

    temp_warnings = {}
    async for msg in log_channel.history(limit=None):
        if msg.content.startswith("[WARN_LOG]"):
            _, g_id, target_id, *rest = msg.content.split()
            if g_id == str(guild.id):
                reason = " ".join(rest[:-1])
                issued_by = rest[-1]
                temp_warnings.setdefault(int(target_id), []).append(f"{reason} (by <@{issued_by}>)")
        elif msg.content.startswith("[REMOVEWARN_LOG]"):
            _, g_id, target_id = msg.content.split()
            if g_id == str(guild.id) and int(target_id) in temp_warnings:
                del temp_warnings[int(target_id)]
    warnings.update(temp_warnings)

async def log_action(interaction: discord.Interaction, log_text: str):
    guild_id = str(interaction.guild.id)
    log_channel_id = guild_settings.get(guild_id, {}).get("bot_logs")
    log_channel = interaction.guild.get_channel(int(log_channel_id)) if log_channel_id and log_channel_id != "none" else interaction.channel
    if log_channel:
        await log_channel.send(log_text)

@tree.command(name="warn", description="Warn a user with a reason")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("❌ You don't have permission to warn members.", ephemeral=True)
    
    warnings.setdefault(member.id, []).append(f"{reason} (by {interaction.user})")
    await interaction.response.send_message(f"⚠️ {member.mention} has been warned. Reason: {reason}")
    await log_action(interaction, f"[WARN_LOG] {interaction.guild.id} {member.id} {reason} {interaction.user.id}")

@tree.command(name="removewarn", description="Remove all warnings for a user")
async def removewarn(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("❌ You don't have permission to remove warnings.", ephemeral=True)
    
    if member.id in warnings:
        del warnings[member.id]
        await interaction.response.send_message(f"🧽 All warnings for {member.mention} have been removed.")
        await log_action(interaction, f"[REMOVEWARN_LOG] {interaction.guild.id} {member.id}")
    else:
        await interaction.response.send_message(f"ℹ️ {member.mention} has no warnings.", ephemeral=True)

@tree.command(name="warnpanel", description="View all current warnings")
async def warnpanel(interaction: discord.Interaction):
    if not warnings:
        return await interaction.response.send_message("ℹ️ No warnings have been issued.", ephemeral=True)
    
    embed = discord.Embed(title="📋 Warning Panel", color=discord.Color.orange())
    for user_id, reasons in warnings.items():
        member = interaction.guild.get_member(user_id)
        name = member.display_name if member else f"User ID {user_id}"
        embed.add_field(name=name, value="\n".join(reasons), inline=False)
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_ready():
    for guild in bot.guilds:
        await rebuild_warnings(guild)
    print(f"✅ Logged in as {bot.user}")

# ---------------- On Ready: Rebuild Warnings ---------------- #
@bot.event
async def on_ready():
    for guild in bot.guilds:
        await rebuild_warnings(guild)
    print(f"✅ Logged in as {bot.user}")

# ---------------- On Ready: Rebuild Warnings ---------------- #
@bot.event
async def on_ready():
    for guild in bot.guilds:
        await rebuild_warnings(guild)
    print(f"✅ Logged in as {bot.user}")


from datetime import datetime

# ---------------- Command Logging (Embed with Severity Colors) ---------------- #
SERIOUS_COMMANDS = ["warn", "removewarn", "warnpanel", "boot", "obliterate", "unobliterate", 
                    "mute", "unmute", "lock", "unlock", "slowmode", "cleardms"]

@bot.event
async def on_interaction(interaction: discord.Interaction):
    log_channel = bot.get_channel(1405214678983905440)
    if not log_channel:
        return

    if interaction.type != discord.InteractionType.application_command:
        return

    command_name = interaction.command.name if interaction.command else "Unknown"

    # Gather arguments
    args = []
    if interaction.data.get("options"):
        for opt in interaction.data["options"]:
            name = opt.get("name")
            value = opt.get("value")
            args.append(f"{name}={value}")
    args_text = ", ".join(args) if args else "No arguments"

    # Determine embed color
    member = interaction.user
    color = discord.Color.blue()  # default for normal users

    if isinstance(member, discord.Member):
        is_admin = member.guild_permissions.administrator or member.guild_permissions.manage_guild
        if command_name.lower() in SERIOUS_COMMANDS:
            color = discord.Color.red()  # serious commands
        elif is_admin:
            color = discord.Color.orange()  # admin normal commands

    embed = discord.Embed(
        title="📌 Command Used",
        color=color,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
    embed.add_field(name="Command", value=f"/{command_name}", inline=False)
    embed.add_field(name="Arguments", value=args_text, inline=False)
    embed.add_field(name="Channel", value=f"{interaction.channel} ({interaction.channel.id})", inline=False)

    await log_channel.send(embed=embed)







# ---------------- Utility & Tools ---------------- #

@tree.command(name="userinfo", description="Show detailed information about a user")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(
        title=f"👤 User Info - {member}",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Username", value=f"{member} ({member.id})", inline=False)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.add_field(name="Roles", value=", ".join([role.mention for role in member.roles[1:]]) or "None", inline=False)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    await interaction.response.send_message(embed=embed)

@tree.command(name="serverinfo", description="Show information about this server")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(
        title=f"🌐 Server Info - {guild.name}",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Server ID", value=guild.id, inline=False)
    embed.add_field(name="Owner", value=guild.owner, inline=False)
    embed.add_field(name="Members", value=guild.member_count, inline=False)
    embed.add_field(name="Roles", value=len(guild.roles), inline=False)
    embed.add_field(name="Channels", value=len(guild.channels), inline=False)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    await interaction.response.send_message(embed=embed)

@tree.command(name="avatar", description="Show a user's avatar")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(
        title=f"🖼️ Avatar - {member}",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    embed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)
    await interaction.response.send_message(embed=embed)


from discord.ui import Button, View

# ---------------- Say Command (Admin Only) ---------------- #
@tree.command(name="say", description="Have the bot say your next message in a specific channel")
@app_commands.describe(channel="The channel where the bot will send your message")
async def say(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(
            "❌ You must be an administrator to use this command.", ephemeral=True
        )

    # Create a dismiss button
    dismiss_button = Button(label="Dismiss", style=discord.ButtonStyle.gray)
    view = View()
    view.add_item(dismiss_button)

    async def dismiss_callback(i: discord.Interaction):
        await i.message.delete()
        await i.response.send_message("❌ Say command canceled.", ephemeral=True)

    dismiss_button.callback = dismiss_callback

    await interaction.response.send_message(
        f"ℹ️ Your next message will be sent by the bot in {channel.mention}. Type your message here in this chat or press 'Dismiss' to cancel.",
        ephemeral=True,
        view=view
    )

    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    msg = await interaction.client.wait_for("message", check=check)

    # Ask for confirmation
    confirm_button = Button(label="Send", style=discord.ButtonStyle.green)
    cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)
    confirm_view = View()
    confirm_view.add_item(confirm_button)
    confirm_view.add_item(cancel_button)

    async def send_callback(i: discord.Interaction):
        files = [await a.to_file() for a in msg.attachments] if msg.attachments else None
        await channel.send(content=msg.content or None, files=files)
        await i.response.edit_message(content=f"✅ Message sent to {channel.mention}.", view=None)

    async def cancel_callback(i: discord.Interaction):
        await i.response.edit_message(content="❌ Message sending canceled.", view=None)

    confirm_button.callback = send_callback
    cancel_button.callback = cancel_callback

    await interaction.followup.send(
        f"⚠️ Confirm sending your message to {channel.mention}:",
        ephemeral=True,
        view=confirm_view
    )

# ---------------- Archive Channel Command ---------------- #

@tree.command(name="archive", description="Archive a channel to the archive category")
@app_commands.describe(channel="The channel to archive")
async def archive(interaction: discord.Interaction, channel: discord.TextChannel):
    config = load_config()
    guild_config = config.get(str(interaction.guild.id))

    if not guild_config:
        return await interaction.response.send_message(
            "⚠️ This server has not run `/start` yet. Please run it first to configure archive settings.",
            ephemeral=True
        )

    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ You don't have permission to archive channels.", ephemeral=True)

    archive_category_id = guild_config.get("archive_category")
    log_channel_id = guild_config.get("bot_logs")

    if not archive_category_id:
        return await interaction.response.send_message(
            "⚠️ No archive category has been set. Please run `/start` to configure it.",
            ephemeral=True
        )

    archive_category = interaction.guild.get_channel(archive_category_id)
    if not archive_category or not isinstance(archive_category, discord.CategoryChannel):
        return await interaction.response.send_message(
            "⚠️ The archive category ID is invalid. Please re-run `/start`.",
            ephemeral=True
        )

    # Move channel to archive category
    try:
        await channel.edit(category=archive_category, sync_permissions=True)
        await interaction.response.send_message(f"📦 {channel.mention} has been archived.", ephemeral=True)

        # Log archive with special recognition code for unarchive
        log_message = f"[ARCHIVE_LOG] {channel.id}"
        if log_channel_id:
            log_channel = interaction.guild.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(f"📦 Channel {channel.mention} archived.\n`{log_message}`")
    except discord.Forbidden:
        await interaction.response.send_message("⚠️ I don't have permission to move that channel.", ephemeral=True)


# ---------------- Unarchive Channel Command ---------------- #

@tree.command(name="unarchive", description="Unarchive a channel and restore its previous category")
@app_commands.describe(channel="The channel you want to unarchive")
async def unarchive(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.guild:
        return await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)

    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ You don't have permission to manage channels.", ephemeral=True)

    log_channel = interaction.guild.get_channel(1405214678983905440)
    if not log_channel:
        return await interaction.response.send_message("❌ Bot logs channel not found.", ephemeral=True)

    async for msg in log_channel.history(limit=200):
        if msg.content.startswith("[ARCHIVE_LOG]"):
            parts = msg.content.split()
            if len(parts) == 4:
                _, guild_id, channel_id, old_category_id = parts
                if str(channel.id) == channel_id:
                    if old_category_id == "None":
                        old_category = None
                    else:
                        old_category = discord.utils.get(interaction.guild.categories, id=int(old_category_id))

                    await channel.edit(category=old_category)
                    await interaction.response.send_message(
                        f"✅ {channel.mention} has been unarchived.", ephemeral=True
                    )
                    return

    await interaction.response.send_message("❌ No archive log found for this channel.", ephemeral=True)

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ---------------- MOD PANEL ---------------- #
from discord import Embed, Interaction
from discord.ui import View, Button, Modal, TextInput
from discord.ext import commands

@tree.command(name="modpanel", description="Open the moderation control panel")
async def modpanel(interaction: Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ You must be an admin to use the mod panel.", ephemeral=True)

    embed = Embed(title="🛡️ Moderation Panel", description="Click a button to perform an action.", color=discord.Color.blue())
    view = View(timeout=None)

    # ---------------- First row ---------------- #
    # Kick
    kick_btn = Button(label="Kick", style=discord.ButtonStyle.danger)
    async def kick_callback(btn_inter):
        modal = Modal(title="Kick User")
        user_input = TextInput(label="User ID or mention", placeholder="Enter the user to kick", required=True)
        reason_input = TextInput(label="Reason", placeholder="Reason for the kick", required=False)
        modal.add_item(user_input)
        modal.add_item(reason_input)

        async def modal_submit(modal_inter):
            try:
                member = await btn_inter.guild.fetch_member(int(user_input.value.strip("<@!>")))
                await member.kick(reason=reason_input.value or None)
                await modal_inter.response.send_message(f"👢 {member.mention} has been kicked.", ephemeral=True)
                await log_action(btn_inter, f"[BOOT_LOG] {btn_inter.guild.id} {member.id} {reason_input.value or 'No reason'}")
            except:
                await modal_inter.response.send_message("⚠️ Could not kick this user.", ephemeral=True)
        modal.on_submit = modal_submit
        await btn_inter.response.send_modal(modal)
    kick_btn.callback = kick_callback
    view.add_item(kick_btn)

    # Ban
    ban_btn = Button(label="Ban", style=discord.ButtonStyle.danger)
    async def ban_callback(btn_inter):
        modal = Modal(title="Ban User")
        user_input = TextInput(label="User ID or mention", placeholder="Enter the user to ban", required=True)
        reason_input = TextInput(label="Reason", placeholder="Reason for the ban", required=False)
        modal.add_item(user_input)
        modal.add_item(reason_input)

        async def modal_submit(modal_inter):
            try:
                member = await btn_inter.guild.fetch_member(int(user_input.value.strip("<@!>")))
                await member.ban(reason=reason_input.value or None)
                await modal_inter.response.send_message(f"🔨 {member.mention} has been banned.", ephemeral=True)
                await log_action(btn_inter, f"[OBLITERATE_LOG] {btn_inter.guild.id} {member.id} {reason_input.value or 'No reason'}")
            except:
                await modal_inter.response.send_message("⚠️ Could not ban this user.", ephemeral=True)
        modal.on_submit = modal_submit
        await btn_inter.response.send_modal(modal)
    ban_btn.callback = ban_callback
    view.add_item(ban_btn)

    # View Bans
    viewbans_btn = Button(label="View Bans", style=discord.ButtonStyle.success)
    async def viewbans_callback(btn_inter):
        bans = await btn_inter.guild.bans()
        if not bans:
            return await btn_inter.response.send_message("ℹ️ No banned members.", ephemeral=True)
        embed_bans = Embed(title=f"🚫 Banned Members in {btn_inter.guild.name}", color=discord.Color.red())
        for b in bans:
            embed_bans.add_field(name=str(b.user), value=b.reason or "No reason", inline=False)
        msg = await btn_inter.response.send_message(embed=embed_bans, ephemeral=True, view=View(timeout=None))
        
        # Add Unban buttons to the ephemeral message
        ban_view = View(timeout=None)
        for b in bans:
            unban_btn = Button(label=f"Unban {b.user.name}", style=discord.ButtonStyle.green)
            async def unban_callback(unban_inter, target=b.user):
                await btn_inter.guild.unban(target)
                await unban_inter.response.send_message(f"✅ {target} has been unbanned.", ephemeral=True)
                await log_action(btn_inter, f"[UNBAN_LOG] {btn_inter.guild.id} {target.id}")
            unban_btn.callback = unban_callback
            ban_view.add_item(unban_btn)
        await btn_inter.followup.send("Manage individual bans:", view=ban_view, ephemeral=True)
    viewbans_btn.callback = viewbans_callback
    view.add_item(viewbans_btn)

    # ---------------- Second row ---------------- #
    # Archive
    archive_btn = Button(label="Archive Channel", style=discord.ButtonStyle.secondary)
    async def archive_callback(btn_inter):
        modal = Modal(title="Archive Channel")
        channel_input = TextInput(label="Channel ID or mention", placeholder="Enter channel to archive", required=True)
        modal.add_item(channel_input)

        async def modal_submit(modal_inter):
            try:
                channel = await btn_inter.guild.fetch_channel(int(channel_input.value.strip("<#>")))
                category_id = guild_settings.get(str(btn_inter.guild.id), {}).get("archive_category")
                if category_id:
                    category = btn_inter.guild.get_channel(int(category_id))
                    await channel.edit(category=category)
                    await modal_inter.response.send_message(f"📦 {channel.mention} archived to {category.name}.", ephemeral=True)
                    await log_action(btn_inter, f"[ARCHIVE_LOG] {btn_inter.guild.id} {channel.id}")
                else:
                    await modal_inter.response.send_message("⚠️ No archive category set.", ephemeral=True)
            except:
                await modal_inter.response.send_message("⚠️ Invalid channel.", ephemeral=True)
        modal.on_submit = modal_submit
        await btn_inter.response.send_modal(modal)
    archive_btn.callback = archive_callback
    view.add_item(archive_btn)

    # Unarchive
    unarchive_btn = Button(label="Unarchive Channel", style=discord.ButtonStyle.secondary)
    async def unarchive_callback(btn_inter):
        await btn_inter.response.send_message("📤 Use `/unarchive [channel]` to restore the original category.", ephemeral=True)
    unarchive_btn.callback = unarchive_callback
    view.add_item(unarchive_btn)

    # ---------------- Third row ---------------- #
    # Warn
    warn_btn = Button(label="Warn", style=discord.ButtonStyle.primary)
    async def warn_callback(btn_inter):
        modal = Modal(title="Warn User")
        user_input = TextInput(label="User ID or mention", placeholder="Enter the user to warn", required=True)
        reason_input = TextInput(label="Reason", placeholder="Reason for the warning", required=True, style=discord.TextStyle.long)
        modal.add_item(user_input)
        modal.add_item(reason_input)

        async def modal_submit(modal_inter):
            try:
                member = await btn_inter.guild.fetch_member(int(user_input.value.strip("<@!>")))
            except:
                return await modal_inter.response.send_message("❌ Invalid user ID.", ephemeral=True)
            warnings.setdefault(member.id, []).append(f"{reason_input.value} (by {btn_inter.user})")
            await modal_inter.response.send_message(f"⚠️ {member.mention} has been warned.", ephemeral=True)
            await log_action(btn_inter, f"[WARN_LOG] {btn_inter.guild.id} {member.id} {reason_input.value} {btn_inter.user.id}")
        modal.on_submit = modal_submit
        await btn_inter.response.send_modal(modal)
    warn_btn.callback = warn_callback
    view.add_item(warn_btn)

    # Warn Panel
    warnpanel_btn = Button(label="Warn Panel", style=discord.ButtonStyle.secondary)
    async def warnpanel_callback(btn_inter):
        if not warnings:
            return await btn_inter.response.send_message("ℹ️ No warnings have been issued.", ephemeral=True)
        embed_panel = Embed(title="📋 Warning Panel", color=discord.Color.orange())
        for user_id, reasons in warnings.items():
            member = btn_inter.guild.get_member(user_id)
            name = member.display_name if member else f"User ID {user_id}"
            embed_panel.add_field(name=name, value="\n".join(reasons), inline=False)
        await btn_inter.response.send_message(embed=embed_panel, ephemeral=True)
    warnpanel_btn.callback = warnpanel_callback
    view.add_item(warnpanel_btn)

    # ---------------- Send modpanel ---------------- #
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# ---------------- Start (QUESTIONS) ---------------- #

import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import asyncio

CONFIG_FILE = "bot_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

async def ask_question(interaction, question, check, timeout=120):
    await interaction.followup.send(question)
    try:
        msg = await interaction.client.wait_for("message", check=check, timeout=timeout)
        if msg.content.lower() == "cancel":
            await interaction.followup.send("❌ Setup cancelled.", ephemeral=True)
            return None
        return msg
    except asyncio.TimeoutError:
        await interaction.followup.send("⏳ Setup timed out. Please run `/start` again.", ephemeral=True)
        return None

@tree.command(name="start", description="Run the bot setup wizard")
async def start(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ You must be an administrator to run setup.", ephemeral=True)

    await interaction.response.send_message("⚙️ Setup started! You can type `cancel` at any time to stop.", ephemeral=True)
    config = load_config()
    guild_id = str(interaction.guild.id)
    config[guild_id] = {}

    def check(m):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    # --- Bot Logs Channel ---
    msg = await ask_question(
        interaction,
        "📜 What is the **Channel ID** for bot-logs?\nType an ID, `none`, or `create` to let the bot make one.",
        check
    )
    if msg is None: return

    if msg.content.lower() == "none":
        config[guild_id]["bot_logs"] = None
        log_channel = interaction.channel
    elif msg.content.lower() == "create":
        log_channel = await interaction.guild.create_text_channel("bot-logs")
        config[guild_id]["bot_logs"] = log_channel.id
    else:
        try:
            log_channel = interaction.guild.get_channel(int(msg.content))
            if not log_channel:
                await interaction.followup.send("⚠️ Channel not found. Defaulting to this channel.")
                log_channel = interaction.channel
            config[guild_id]["bot_logs"] = log_channel.id
        except ValueError:
            await interaction.followup.send("⚠️ Invalid ID. Defaulting to this channel.")
            log_channel = interaction.channel
            config[guild_id]["bot_logs"] = log_channel.id

    # --- Archive Category ---
    msg = await ask_question(
        interaction,
        "📦 What is the **Category ID** for archived channels?\nType an ID, `none`, or `create` to let the bot make one.",
        check
    )
    if msg is None: return

    if msg.content.lower() == "none":
        config[guild_id]["archive_category"] = None
    elif msg.content.lower() == "create":
        category = await interaction.guild.create_category("Archived Channels")
        config[guild_id]["archive_category"] = category.id
    else:
        try:
            category = interaction.guild.get_channel(int(msg.content))
            if isinstance(category, discord.CategoryChannel):
                config[guild_id]["archive_category"] = category.id
            else:
                await interaction.followup.send("⚠️ That ID doesn’t belong to a category. Setting to None.")
                config[guild_id]["archive_category"] = None
        except ValueError:
            await interaction.followup.send("⚠️ Invalid ID. Setting to None.")
            config[guild_id]["archive_category"] = None

    save_config(config)

    await log_channel.send(
        embed=discord.Embed(
            title="✅ Setup Complete",
            description=f"Bot is now configured for `{interaction.guild.name}`.\n\n"
            f"**Bot Logs Channel:** {config[guild_id]['bot_logs'] or 'None'}\n"
            f"**Archive Category:** {config[guild_id]['archive_category'] or 'None'}",
            color=discord.Color.green()
        )
    )
# ---------------- #---------------- #---------------- #---------------- #---------------- #---------------- #---------------- #---------------- #---------------- #---------------- #---------------- #---------------- #

from discord import Embed, app_commands, Interaction, User
from discord.ext import commands
from discord.ui import View, Button

# ---------------- /users ---------------- #
@tree.command(name="users", description="List all server members")
async def users(interaction: Interaction):
    members = interaction.guild.members
    if not members:
        return await interaction.response.send_message("ℹ️ No members found.", ephemeral=True)

    member_list = "\n".join([f"{m.display_name} — {m.id}" for m in members])
    embed = Embed(title=f"👥 Members in {interaction.guild.name}", description=member_list[:4000], color=discord.Color.blue())
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ---------------- /usersearch ---------------- #
@tree.command(name="usersearch", description="Search for a user by name")
@app_commands.describe(query="Partial or full username to search")
async def usersearch(interaction: Interaction, query: str):
    query_lower = query.lower()
    matches = [m for m in interaction.guild.members if m.display_name.lower().startswith(query_lower)]

    if not matches:
        return await interaction.response.send_message(f"⚠️ No users found starting with '{query}'.", ephemeral=True)

    embed = Embed(title=f"Search results for '{query}'", color=discord.Color.green())
    view = View(timeout=None)

    for user in matches[:25]:  # Max 25 buttons
        btn = Button(label=user.display_name, style=discord.ButtonStyle.primary)

        async def userinfo_callback(btn_inter, user=user):
            roles = ", ".join([r.name for r in user.roles if r.name != "@everyone"]) or "None"
            embed_info = Embed(title=f"👤 {user.display_name}", color=discord.Color.gold())
            embed_info.add_field(name="ID", value=user.id, inline=False)
            embed_info.add_field(name="Username", value=str(user), inline=False)
            embed_info.add_field(name="Joined At", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S") if user.joined_at else "Unknown", inline=False)
            embed_info.add_field(name="Roles", value=roles, inline=False)
            await btn_inter.response.send_message(embed=embed_info, ephemeral=True)

        btn.callback = userinfo_callback
        view.add_item(btn)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)




# ---------------- Bot Ready ---------------- #

@bot.event
async def on_ready():
    print(f"✅ Successfully started the bot; Logged in as {bot.user} (ID: {bot.user.id})")
    await tree.sync()
    print("🌐 Slash commands successfully synced! - 🤖 Bot is fully operational {Ctrl + C to terminate the bot}")

# ---------------- Run Bot ---------------- #
print("🤖 Starting bot..")
token = os.getenv("BOT_TOKEN")
if not token:
    raise SystemExit("Please set BOT_TOKEN environment variable in Replit Secrets.")
keep_alive()
bot.run(token)
