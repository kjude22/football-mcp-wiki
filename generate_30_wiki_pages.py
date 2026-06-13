import os
from datetime import datetime

WIKI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wiki")
os.makedirs(WIKI_DIR, exist_ok=True)

# Define 30 Famous Football Keywords
DATABASE = {
    # 1. PLAYERS (12)
    "son_heung_min": {
        "title": "Son Heung-min",
        "tags": ["player", "forward", "tottenham", "south-korea"],
        "links": ["/wiki/tottenham_hotspur.md", "/wiki/premier_league.md", "/wiki/gegenpressing.md"],
        "content": "Son Heung-min is a South Korean professional footballer who plays as a forward and captains Premier League club Tottenham Hotspur and the South Korea national team. Widely regarded as one of the best wingers in the world, he is celebrated for his two-footed shooting, explosive speed, and direct playmaking. He won the Premier League Golden Boot in the 2021-22 season."
    },
    "lionel_messi": {
        "title": "Lionel Messi",
        "tags": ["player", "forward", "barcelona", "argentina"],
        "links": ["/wiki/barcelona.md", "/wiki/la_liga.md", "/wiki/false_nine.md", "/wiki/tiki_taka.md"],
        "content": "Lionel Messi is an Argentine professional footballer who plays as a forward. Having spent the majority of his career at Barcelona, he is widely regarded as one of the greatest players of all time. Messi is famous for his dribbling close control, playmaking vision, and prolific goalscoring records, frequently dropping deep to play as a False Nine in Pep Guardiola's legendary Barcelona setup."
    },
    "cristiano_ronaldo": {
        "title": "Cristiano Ronaldo",
        "tags": ["player", "forward", "real-madrid", "portuguese"],
        "links": ["/wiki/real_madrid.md", "/wiki/la_liga.md", "/wiki/premier_league.md", "/wiki/serie_a.md"],
        "content": "Cristiano Ronaldo is a Portuguese professional footballer who plays as a forward. He won five Ballon d'Or awards and became Real Madrid's all-time leading goal scorer. Ronaldo is known for his unmatched aerial ability, athleticism, physical power, and clutch goalscoring in the UEFA Champions League, dominating English, Spanish, and Italian football."
    },
    "kylian_mbappe": {
        "title": "Kylian Mbappe",
        "tags": ["player", "forward", "real-madrid", "france"],
        "links": ["/wiki/real_madrid.md", "/wiki/paris_saint_germain.md", "/wiki/la_liga.md"],
        "content": "Kylian Mbappé is a French professional footballer who plays as a forward for Real Madrid and the France national team. Renowned for his explosive acceleration, dribbling skills, and clinical finishing, he became the all-time top scorer for Paris Saint-Germain before his high-profile transfer to Real Madrid in 2024."
    },
    "erling_haaland": {
        "title": "Erling Haaland",
        "tags": ["player", "forward", "manchester-city", "norway"],
        "links": ["/wiki/manchester_city.md", "/wiki/premier_league.md", "/wiki/bayern_munich.md"],
        "content": "Erling Haaland is a Norwegian professional footballer who plays as a striker for Premier League club Manchester City. He is widely considered one of the best strikers in world football due to his raw pace, physical strength, positioning, and clinical box finishing, breaking the Premier League single-season scoring record in his debut year."
    },
    "kevin_de_bruyne": {
        "title": "Kevin De Bruyne",
        "tags": ["player", "midfielder", "manchester-city", "belgium"],
        "links": ["/wiki/manchester_city.md", "/wiki/premier_league.md", "/wiki/false_nine.md"],
        "content": "Kevin De Bruyne is a Belgian professional footballer who plays as a midfielder for Manchester City. Regarded as one of the best midfielders of his generation, De Bruyne is celebrated for his exceptional passing range, crossing precision, tactical intelligence, and long-range shooting ability, acting as the primary playmaker in City's tactical systems."
    },
    "harry_kane": {
        "title": "Harry Kane",
        "tags": ["player", "forward", "bayern-munich", "england"],
        "links": ["/wiki/bayern_munich.md", "/wiki/tottenham_hotspur.md", "/wiki/premier_league.md"],
        "content": "Harry Kane is an English professional footballer who plays as a striker for Bundesliga club Bayern Munich and captains the England national team. Kane is a prolific goalscorer who is also renowned for his deep playmaking vision, passing capability, and holdup play, having previously played as Tottenham Hotspur's legendary talisman."
    },
    "jude_bellingham": {
        "title": "Jude Bellingham",
        "tags": ["player", "midfielder", "real-madrid", "england"],
        "links": ["/wiki/real_madrid.md", "/wiki/la_liga.md", "/wiki/false_nine.md"],
        "content": "Jude Bellingham is an English professional footballer who plays as a midfielder for Real Madrid and the England national team. An dynamic box-to-box midfielder with exceptional ball-carrying, defensive work rate, and late box arrivals, he transitioned into a high-scoring False Nine role during his debut season in Spain, winning La Liga."
    },
    "mohamed_salah": {
        "title": "Mohamed Salah",
        "tags": ["player", "forward", "liverpool", "egypt"],
        "links": ["/wiki/liverpool.md", "/wiki/premier_league.md", "/wiki/gegenpressing.md"],
        "content": "Mohamed Salah is an Egyptian professional footballer who plays as a forward for Premier League club Liverpool. Famous for his blistering speed, dribbling cuts from the right wing, and clinical goalscoring, he is a core piece of Jurgen Klopp's high-intensity Gegenpressing tactical setup, winning both Premier League and Champions League titles."
    },
    "virgil_van_dijk": {
        "title": "Virgil van Dijk",
        "tags": ["player", "defender", "liverpool", "netherlands"],
        "links": ["/wiki/liverpool.md", "/wiki/premier_league.md", "/wiki/gegenpressing.md"],
        "content": "Virgil van Dijk is a Dutch professional footballer who plays as a center-back and captains both Liverpool and the Netherlands national team. Renowned for his strength, aerial dominance, leadership, pace, and reading of the game, he is widely regarded as one of the best defenders of the modern era, playing a critical role in high-line defensive structures."
    },
    "neymar_jr": {
        "title": "Neymar Jr",
        "tags": ["player", "forward", "barcelona", "brazil"],
        "links": ["/wiki/barcelona.md", "/wiki/paris_saint_germain.md", "/wiki/tiki_taka.md"],
        "content": "Neymar Jr is a Brazilian professional footballer who plays as a winger and playmaker. Famous for his creative flair, dribbling skills, and playmaking improvisation, he formed the iconic 'MSN' attacking trio at Barcelona alongside Lionel Messi and Luis Suarez, winning the historic continental treble in 2015."
    },
    "robert_lewandowski": {
        "title": "Robert Lewandowski",
        "tags": ["player", "forward", "barcelona", "poland"],
        "links": ["/wiki/barcelona.md", "/wiki/bayern_munich.md", "/wiki/la_liga.md", "/wiki/gegenpressing.md"],
        "content": "Robert Lewandowski is a Polish professional footballer who plays as a striker for La Liga club Barcelona. Celebrated for his positioning, clinical finishing, and technical hold-up play, he enjoyed record-breaking seasons at Bayern Munich under Gegenpressing and possession systems before moving to Spain."
    },
    
    # 2. CLUBS (10)
    "tottenham_hotspur": {
        "title": "Tottenham Hotspur",
        "tags": ["club", "tottenham", "london", "premier-league"],
        "links": ["/wiki/son_heung_min.md", "/wiki/harry_kane.md", "/wiki/premier_league.md", "/wiki/gegenpressing.md"],
        "content": "Tottenham Hotspur is an English professional football club based in London that competes in the Premier League. Spurs are known for playing offensive, high-pressing football, historically utilizing variations of Gegenpressing to recover possession in advanced zones, captained by South Korea's Son Heung-min."
    },
    "real_madrid": {
        "title": "Real Madrid",
        "tags": ["club", "madrid", "spain", "la-liga"],
        "links": ["/wiki/cristiano_ronaldo.md", "/wiki/jude_bellingham.md", "/wiki/kylian_mbappe.md", "/wiki/la_liga.md"],
        "content": "Real Madrid is a professional football club based in Madrid, Spain, that competes in La Liga. The most successful club in European football history with a record number of Champions League titles, they are known for their galactico recruitment philosophy, counter-attacking efficiency, and winning mentality."
    },
    "barcelona": {
        "title": "Barcelona",
        "tags": ["club", "barcelona", "spain", "la-liga"],
        "links": ["/wiki/lionel_messi.md", "/wiki/neymar_jr.md", "/wiki/robert_lewandowski.md", "/wiki/la_liga.md", "/wiki/tiki_taka.md", "/wiki/false_nine.md"],
        "content": "FC Barcelona is a professional football club based in Barcelona, Catalonia, Spain. Globally famous for their youth academy La Masia and positional play principles, the club pioneered the Tiki-Taka tactical system under Pep Guardiola, creating one of the most dominant possession teams in football history."
    },
    "manchester_city": {
        "title": "Manchester City",
        "tags": ["club", "manchester", "england", "premier-league"],
        "links": ["/wiki/erling_haaland.md", "/wiki/kevin_de_bruyne.md", "/wiki/premier_league.md", "/wiki/false_nine.md", "/wiki/tiki_taka.md"],
        "content": "Manchester City is an English football club based in Manchester, competing in the Premier League. Guided by manager Pep Guardiola, the team has dominated modern English football using high-possession positional concepts, utilizing playmakers like Kevin De Bruyne and elite finishers like Erling Haaland."
    },
    "liverpool": {
        "title": "Liverpool",
        "tags": ["club", "liverpool", "england", "premier-league"],
        "links": ["/wiki/mohamed_salah.md", "/wiki/virgil_van_dijk.md", "/wiki/premier_league.md", "/wiki/gegenpressing.md"],
        "content": "Liverpool Football Club is a professional football club based in Liverpool, England. Under Jürgen Klopp, the club became globally famous for its intense, full-throttle Gegenpressing football style, relying on high-line pressing, overlapping fullbacks, and rapid transitions to capture domestic and European titles."
    },
    "manchester_united": {
        "title": "Manchester United",
        "tags": ["club", "manchester", "england", "premier-league"],
        "links": ["/wiki/cristiano_ronaldo.md", "/wiki/premier_league.md", "/wiki/park_the_bus.md"],
        "content": "Manchester United is a professional football club based in Old Trafford, Greater Manchester, England. One of the most supported and successful clubs globally, the club achieved legendary status under Sir Alex Ferguson, known for dynamic wing play, tactical flexibility, and famous comebacks."
    },
    "bayern_munich": {
        "title": "Bayern Munich",
        "tags": ["club", "munich", "germany", "bundesliga"],
        "links": ["/wiki/harry_kane.md", "/wiki/robert_lewandowski.md", "/wiki/gegenpressing.md"],
        "content": "FC Bayern Munich is a German professional sports club based in Munich, Bavaria. The dominant force in German football, the club relies on high-intensity pressing and wing-focused attacking systems, having secured multiple historic European trebles and signing star striker Harry Kane in 2023."
    },
    "paris_saint_germain": {
        "title": "Paris Saint Germain",
        "tags": ["club", "paris", "france", "ligue-1"],
        "links": ["/wiki/kylian_mbappe.md", "/wiki/neymar_jr.md"],
        "content": "Paris Saint-Germain is a professional football club based in Paris, France. Competing in Ligue 1, they are France's most successful modern club, famous for assembling world-class attacking lines featuring global stars like Kylian Mbappé, Neymar Jr, and Lionel Messi."
    },
    "arsenal": {
        "title": "Arsenal",
        "tags": ["club", "london", "england", "premier-league"],
        "links": ["/wiki/premier_league.md", "/wiki/tiki_taka.md"],
        "content": "Arsenal Football Club is a professional football club based in Islington, London, England. Historically famous for the 'Invincibles' season under Arsene Wenger playing fluid attacking football, the club currently utilizes modern positional play setups focused on high pressing and numerical overloads."
    },
    "chelsea": {
        "title": "Chelsea",
        "tags": ["club", "london", "england", "premier-league"],
        "links": ["/wiki/premier_league.md", "/wiki/catenaccio.md", "/wiki/park_the_bus.md"],
        "content": "Chelsea Football Club is a professional football club based in West London, England. The club rose to global dominance under Jose Mourinho's defensive solidity and has won multiple Champions League titles, historically utilizing compact, disciplined defensive systems like Park the Bus."
    },
    
    # 3. TACTICS (5)
    "gegenpressing": {
        "title": "Gegenpressing",
        "tags": ["tactics", "gegenpressing", "system", "pressing"],
        "links": ["/wiki/index.md", "/wiki/tottenham_hotspur.md", "/wiki/liverpool.md", "/wiki/premier_league.md", "/wiki/bayern_munich.md"],
        "content": "Gegenpressing (German for counter-pressing) is a tactical philosophy where a team, upon losing possession, immediately attempts to win the ball back rather than falling back into a defensive shape. Popularized by managers like Jurgen Klopp, it restricts opponent transition spaces and triggers instant offensive moves."
    },
    "tiki_taka": {
        "title": "Tiki Taka",
        "tags": ["tactics", "tiki-taka", "possession", "spain"],
        "links": ["/wiki/index.md", "/wiki/barcelona.md", "/wiki/manchester_city.md", "/wiki/la_liga.md", "/wiki/false_nine.md"],
        "content": "Tiki-Taka is a style of play in football characterized by short passing, high possession, and fluid movement. It is heavily associated with Pep Guardiola's Barcelona and the Spain national team, aiming to control the tempo of the game, tire out opponents, and create openings through constant triangular passes."
    },
    "catenaccio": {
        "title": "Catenaccio",
        "tags": ["tactics", "catenaccio", "defense", "italy"],
        "links": ["/wiki/index.md", "/wiki/serie_a.md", "/wiki/park_the_bus.md"],
        "content": "Catenaccio is a tactical system in football with a strong emphasis on defense. Originating in Switzerland and refined in Italy, it utilizes a defensive line with a sweeper (libero) behind the defenders, aiming to nullify opponent attacks and secure narrow victories via structured counter-attacks."
    },
    "park_the_bus": {
        "title": "Park the Bus",
        "tags": ["tactics", "defense", "low-block"],
        "links": ["/wiki/index.md", "/wiki/chelsea.md", "/wiki/manchester_united.md", "/wiki/catenaccio.md"],
        "content": "Park the Bus is a colloquial term describing an extremely defensive low-block tactical setup where almost all outfield players remain behind the ball deep in their own half. Made famous by managers like Jose Mourinho at Chelsea, it aims to shut down all space, frustrate high-scoring opponents, and defend a lead."
    },
    "false_nine": {
        "title": "False Nine",
        "tags": ["tactics", "forward", "playmaking"],
        "links": ["/wiki/index.md", "/wiki/lionel_messi.md", "/wiki/kevin_de_bruyne.md", "/wiki/jude_bellingham.md", "/wiki/tiki_taka.md"],
        "content": "A False Nine is an unconventional striker who drops deep into the midfield space rather than staying forward. This tactical movement drags opposing center-backs out of position, creating space for wingers to run into, while adding an extra passing option in midfield to dominate possession."
    },
    
    # 4. LEAGUES (3)
    "premier_league": {
        "title": "Premier League",
        "tags": ["league", "england", "premier-league"],
        "links": ["/wiki/index.md", "/wiki/son_heung_min.md", "/wiki/tottenham_hotspur.md", "/wiki/manchester_city.md", "/wiki/liverpool.md", "/wiki/gegenpressing.md"],
        "content": "The Premier League is the top level of the English football league system. Famous worldwide for its fast, physical, and high-intensity style, it heavily features aggressive pressing systems like Gegenpressing, driven by elite clubs and global superstars."
    },
    "la_liga": {
        "title": "La Liga",
        "tags": ["league", "spain", "la-liga"],
        "links": ["/wiki/index.md", "/wiki/lionel_messi.md", "/wiki/cristiano_ronaldo.md", "/wiki/real_madrid.md", "/wiki/barcelona.md", "/wiki/tiki_taka.md"],
        "content": "La Liga is the top professional football division of the Spanish football league system. Renowned for its technical play, tactical intelligence, and possession-based styles, it hosted the legendary Messi-Ronaldo El Clasico era and pioneered the dominance of Tiki-Taka."
    },
    "serie_a": {
        "title": "Serie A",
        "tags": ["league", "italy", "serie-a"],
        "links": ["/wiki/index.md", "/wiki/cristiano_ronaldo.md", "/wiki/catenaccio.md"],
        "content": "Serie A is a professional league competition for football clubs located at the top of the Italian football league system. Historically famous for its tactical discipline, strategic defensive masterclasses like Catenaccio, and legendary defenders."
    }
}

# Write 30 Files
print(f"Generating 30 Football Wiki pages in '{WIKI_DIR}'...")
for filename, page in DATABASE.items():
    path = os.path.join(WIKI_DIR, f"{filename}.md")
    
    # Structure YAML frontmatter
    yaml_header = [
        "---",
        f'title: "{page["title"]}"',
        f'tags: {page["tags"]}',
        f'last_updated: {datetime.now().strftime("%Y-%m-%d")}',
        f'links: {page["links"]}',
        f'version: 1.0',
        "---",
        ""
    ]
    
    full_content = "\n".join(yaml_header) + f"# {page['title']}\n\n{page['content']}\n"
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(full_content)
    print(f" - Created: {filename}.md")

# Create Main index.md referencing all 30 pages
print("\nRebuilding navigation index in wiki/index.md...")
index_path = os.path.join(WIKI_DIR, "index.md")

links_list = [f"/wiki/{f}.md" for f in DATABASE.keys()]
links_str = ", ".join(f'"{l}"' for l in links_list)

index_yaml = [
    "---",
    'title: "Football Tactics & Player Wiki"',
    'tags: ["football", "tactics", "index", "database"]',
    f'last_updated: {datetime.now().strftime("%Y-%m-%d")}',
    f'links: [{links_str}]',
    'version: 1.0',
    "---",
    ""
]

index_content = [
    "# Football Tactics & Player Wiki",
    "",
    "Welcome to the **Football Tactics & Player Wiki**, a persistent, pre-compiled knowledge base documenting modern football tactics, clubs, players, and leagues.",
    "",
    "---",
    "",
    "## 🗺️ Navigation Map",
    "",
    "### 🏃‍♂️ Players",
]

for filename, page in DATABASE.items():
    if "player" in page["tags"]:
        desc = page["content"][:100] + "..."
        index_content.append(f"- [{page['title']}](/wiki/{filename}.md) -- {desc}")

index_content.append("")
index_content.append("### 🛡️ Clubs & Leagues")
for filename, page in DATABASE.items():
    if "club" in page["tags"] or "league" in page["tags"]:
        desc = page["content"][:100] + "..."
        index_content.append(f"- [{page['title']}](/wiki/{filename}.md) -- {desc}")

index_content.append("")
index_content.append("### 💡 Tactical Systems")
for filename, page in DATABASE.items():
    if "tactics" in page["tags"]:
        desc = page["content"][:100] + "..."
        index_content.append(f"- [{page['title']}](/wiki/{filename}.md) -- {desc}")

full_index = "\n".join(index_yaml) + "\n".join(index_content) + "\n"

with open(index_path, "w", encoding="utf-8") as f:
    f.write(full_index)
print("Successfully compiled and updated wiki/index.md!")
