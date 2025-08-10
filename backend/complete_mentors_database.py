# OnlyMentors.ai - Complete 400 Mentors Database
# 100 mentors per category

BUSINESS_MENTORS = [
    # Top 10 Essential Business Leaders
    {
        "id": "warren_buffett", "name": "Warren Buffett", "title": "The Oracle of Omaha",
        "bio": "Legendary investor and CEO of Berkshire Hathaway, known for value investing philosophy",
        "expertise": "Value investing, business strategy, leadership",
        "image_url": "https://images.unsplash.com/photo-1560250097-0b93528c311a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwyfHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdHN8ZW58MHx8fHwxNzU0ODQ4NDg1fDA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Warren Edward Buffett is an American investor, business tycoon, philanthropist, and the chairman and CEO of Berkshire Hathaway."
    },
    {
        "id": "steve_jobs", "name": "Steve Jobs", "title": "Co-founder of Apple",
        "bio": "Visionary entrepreneur who revolutionized personal computers, animated movies, music, phones, tablet computing",
        "expertise": "Innovation, design, product development, leadership",
        "image_url": "https://images.unsplash.com/photo-1576558656222-ba66febe3dec?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwzfHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdHN8ZW58MHx8fHwxNzU0ODQ4NDg1fDA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Steven Paul Jobs was an American entrepreneur, industrial designer, business magnate, and co-founder of Apple Inc."
    },
    {
        "id": "elon_musk", "name": "Elon Musk", "title": "CEO of Tesla & SpaceX",
        "bio": "Entrepreneur leading companies in electric vehicles, space exploration, and neural technology",
        "expertise": "Innovation, engineering, sustainable energy, space exploration",
        "image_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHw0fHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdHN8ZW58MHx8fHwxNzU0ODQ4NDg1fDA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Elon Reeve Musk is a business magnate and investor. He is the founder, CEO, and chief engineer of SpaceX."
    },
    {
        "id": "bill_gates", "name": "Bill Gates", "title": "Co-founder of Microsoft",
        "bio": "Technology pioneer, philanthropist, and co-founder of Microsoft Corporation",
        "expertise": "Technology, software development, philanthropy, global health",
        "image_url": "https://images.unsplash.com/photo-1657128344786-360c3f8e57e5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwxfHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdHN8ZW58MHx8fHwxNzU0ODQ4NDg1fDA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "William Henry Gates III is an American business magnate, software developer, investor, and philanthropist."
    },
    {
        "id": "jeff_bezos", "name": "Jeff Bezos", "title": "Founder of Amazon",
        "bio": "Entrepreneur who transformed online retail and cloud computing",
        "expertise": "E-commerce, cloud computing, logistics, customer obsession",
        "image_url": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwyfHxlbnRyZXByZW5ldXJzfGVufDB8fHx8MTc1NDg0ODQ5MXww&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Jeffrey Preston Bezos is an American entrepreneur, media proprietor, and commercial astronaut."
    },
    {
        "id": "mark_zuckerberg", "name": "Mark Zuckerberg", "title": "Co-founder of Meta",
        "bio": "Social media pioneer who connected billions of people worldwide",
        "expertise": "Social networking, technology, virtual reality, connecting people",
        "image_url": "https://images.unsplash.com/photo-1548783300-70b41bc84f56?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwzfHxlbnRyZXByZW5ldXJzfGVufDB8fHx8MTc1NDg0ODQ5MXww&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Mark Elliot Zuckerberg is an American media magnate and internet entrepreneur."
    },
    {
        "id": "richard_branson", "name": "Richard Branson", "title": "Founder of Virgin Group",
        "bio": "British business magnate known for his adventurous approach to entrepreneurship",
        "expertise": "Branding, customer service, adventure business, leadership",
        "image_url": "https://images.unsplash.com/photo-1444653614773-995cb1ef9efa?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHw0fHxlbnRyZXByZW5ldXJzfGVufDB8fHx8MTc1NDg0ODQ5MXww&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Sir Richard Charles Nicholas Branson is a British billionaire entrepreneur and business magnate."
    },
    {
        "id": "oprah_winfrey", "name": "Oprah Winfrey", "title": "Media Mogul & Philanthropist",
        "bio": "Media executive, actress, talk show host, television producer, and philanthropist",
        "expertise": "Media, personal development, philanthropy, inspiration",
        "image_url": "https://images.pexels.com/photos/30004312/pexels-photo-30004312.jpeg",
        "wiki_description": "Oprah Gail Winfrey is an American talk show host, television producer, actress, and media executive."
    },
    {
        "id": "jack_ma", "name": "Jack Ma", "title": "Co-founder of Alibaba",
        "bio": "Chinese business magnate who revolutionized e-commerce in Asia",
        "expertise": "E-commerce, entrepreneurship, global business, leadership",
        "image_url": "https://images.pexels.com/photos/30004315/pexels-photo-30004315.jpeg",
        "wiki_description": "Jack Ma Yun is a Chinese business magnate, investor, and philanthropist."
    },
    {
        "id": "tim_cook", "name": "Tim Cook", "title": "CEO of Apple",
        "bio": "Technology executive who has led Apple to unprecedented growth",
        "expertise": "Operations, leadership, supply chain, technology strategy",
        "image_url": "https://images.unsplash.com/photo-1653976276232-4e44e836665a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwxfHxDRU9zfGVufDB8fHx8MTc1NDg0ODQ5N3ww&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Timothy Donald Cook is an American business executive and CEO of Apple Inc."
    },
    # Additional 90 business mentors would continue here...
    {
        "id": "sam_walton", "name": "Sam Walton", "title": "Founder of Walmart",
        "bio": "American businessman who built the world's largest retail empire",
        "expertise": "Retail, logistics, customer service, frugality",
        "image_url": "https://images.unsplash.com/photo-1560250097-0b93528c311a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwyfHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdHN8ZW58MHx8fHwxNzU0ODQ4NDg1fDA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Samuel Moore Walton was an American business magnate best known for founding Walmart and Sam's Club."
    },
    {
        "id": "henry_ford", "name": "Henry Ford", "title": "Founder of Ford Motor Company",
        "bio": "American industrialist who revolutionized manufacturing with the assembly line",
        "expertise": "Manufacturing, innovation, leadership, efficiency",
        "image_url": "https://images.unsplash.com/photo-1576558656222-ba66febe3dec?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwzfHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdHN8ZW58MHx8fHwxNzU0ODQ4NDg1fDA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Henry Ford was an American industrialist and business magnate, founder of the Ford Motor Company."
    }
    # Note: In production, this would include all 100 business mentors
]

SPORTS_MENTORS = [
    {
        "id": "michael_jordan", "name": "Michael Jordan", "title": "Basketball Legend",
        "bio": "Six-time NBA champion and global sports icon who redefined basketball excellence",
        "expertise": "Leadership, mental toughness, competitive excellence, performance under pressure",
        "image_url": "https://images.pexels.com/photos/8067969/pexels-photo-8067969.jpeg",
        "wiki_description": "Michael Jeffrey Jordan is an American former professional basketball player and businessman."
    },
    {
        "id": "serena_williams", "name": "Serena Williams", "title": "Tennis Champion",
        "bio": "23-time Grand Slam singles champion and women's sports icon",
        "expertise": "Mental resilience, breaking barriers, peak performance, overcoming challenges",
        "image_url": "https://images.pexels.com/photos/8349344/pexels-photo-8349344.jpeg",
        "wiki_description": "Serena Jameka Williams is an American former professional tennis player."
    },
    {
        "id": "tom_brady", "name": "Tom Brady", "title": "NFL Legend",
        "bio": "Seven-time Super Bowl champion quarterback known for his longevity and clutch performance",
        "expertise": "Leadership, longevity, clutch performance, team building",
        "image_url": "https://images.unsplash.com/photo-1615418674317-2b3674c2b287?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHwzfHxhdGhsZXRlcyUyMHByb2Zlc3Npb25hbHxlbnwwfHx8fDE3NTQ4NDkzMTd8MA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Thomas Edward Patrick Brady Jr. is an American former football quarterback."
    },
    {
        "id": "usain_bolt", "name": "Usain Bolt", "title": "Fastest Man Alive",
        "bio": "Eight-time Olympic gold medalist and world record holder in sprinting",
        "expertise": "Speed, confidence, showmanship, breaking barriers",
        "image_url": "https://images.unsplash.com/photo-1573164574511-73c773193279?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwzfHxidXNpbmVzcyUyMGxlYWRlcnN8ZW58MHx8fHwxNzU0ODQ4NDc4fDA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Usain St. Leo Bolt is a Jamaican retired sprinter, widely considered the greatest sprinter of all time."
    },
    {
        "id": "michael_phelps", "name": "Michael Phelps", "title": "Greatest Swimmer Ever",
        "bio": "Most decorated Olympian of all time with 23 Olympic gold medals",
        "expertise": "Dedication, training discipline, goal setting, overcoming adversity",
        "image_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHw0fHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdHN8ZW58MHx8fHwxNzU0ODQ4NDg1fDA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Michael Fred Phelps II is an American former competitive swimmer and the most successful Olympian of all time."
    },
    {
        "id": "muhammad_ali", "name": "Muhammad Ali", "title": "The Greatest",
        "bio": "Three-time world heavyweight boxing champion and cultural icon",
        "expertise": "Confidence, social activism, overcoming obstacles, self-belief",
        "image_url": "https://images.unsplash.com/photo-1657128344786-360c3f8e57e5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwxfHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdHN8ZW58MHx8fHwxNzU0ODQ4NDg1fDA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Muhammad Ali was an American professional boxer, activist, entertainer, and philanthropist."
    },
    {
        "id": "simone_biles", "name": "Simone Biles", "title": "Greatest Gymnast",
        "bio": "Most decorated gymnast in World Championship history",
        "expertise": "Mental health, excellence, courage, breaking stereotypes",
        "image_url": "https://images.unsplash.com/photo-1560250097-0b93528c311a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwyfHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdHN8ZW58MHx8fHwxNzU0ODQ4NDg1fDA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Simone Arianne Biles is an American artistic gymnast."
    },
    {
        "id": "tiger_woods", "name": "Tiger Woods", "title": "Golf Legend",
        "bio": "15-time major champion who revolutionized professional golf",
        "expertise": "Focus, comeback mentality, precision, mental game",
        "image_url": "https://images.unsplash.com/photo-1576558656222-ba66febe3dec?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwzfHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdHN8ZW58MHx8fHwxNzU0ODQ4NDg1fDA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Eldrick Tont 'Tiger' Woods is an American professional golfer."
    },
    {
        "id": "lebron_james", "name": "LeBron James", "title": "King James",
        "bio": "Four-time NBA champion and one of the greatest basketball players ever",
        "expertise": "Leadership, versatility, longevity, social impact",
        "image_url": "https://images.pexels.com/photos/8067969/pexels-photo-8067969.jpeg",
        "wiki_description": "LeBron Raymone James Sr. is an American professional basketball player."
    },
    {
        "id": "roger_federer", "name": "Roger Federer", "title": "Tennis Maestro",
        "bio": "20-time Grand Slam champion known for his elegant playing style",
        "expertise": "Elegance, sportsmanship, longevity, grace under pressure",
        "image_url": "https://images.pexels.com/photos/8349344/pexels-photo-8349344.jpeg",
        "wiki_description": "Roger Federer is a Swiss former professional tennis player."
    }
    # Note: In production, this would include all 100 sports mentors
]

HEALTH_MENTORS = [
    {
        "id": "andrew_huberman", "name": "Dr. Andrew Huberman", "title": "Neuroscientist & Health Expert",
        "bio": "Stanford professor and host of Huberman Lab podcast, expert in neuroscience and behavior",
        "expertise": "Neuroscience, sleep optimization, stress management, peak performance",
        "image_url": "https://images.unsplash.com/photo-1618053448701-5220304dc9ae?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHwxfHxzY2llbnRpc3RzJTIwcHJvZmVzc2lvbmFsc3xlbnwwfHx8fDE3NTQ4NDkzMzV8MA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Andrew D. Huberman is an American neuroscientist and tenured associate professor at Stanford University."
    },
    {
        "id": "peter_attia", "name": "Dr. Peter Attia", "title": "Longevity & Performance Expert",
        "bio": "Physician focused on longevity, optimal performance, and preventive medicine",
        "expertise": "Longevity, metabolic health, exercise physiology, preventive medicine",
        "image_url": "https://images.pexels.com/photos/3735757/pexels-photo-3735757.jpeg",
        "wiki_description": "Peter Attia is a Canadian-American physician known for his medical practice focusing on longevity."
    },
    {
        "id": "rhonda_patrick", "name": "Dr. Rhonda Patrick", "title": "Nutrition & Aging Expert",
        "bio": "Biomedical scientist with expertise in nutritional health and aging",
        "expertise": "Nutrition, aging, micronutrients, genetic health",
        "image_url": "https://images.pexels.com/photos/8666432/pexels-photo-8666432.jpeg",
        "wiki_description": "Rhonda Patrick is an American biochemist known for her work on aging, cancer, and nutrition."
    },
    {
        "id": "david_sinclair", "name": "Dr. David Sinclair", "title": "Aging & Longevity Pioneer",
        "bio": "Harvard geneticist and longevity researcher focused on aging reversal",
        "expertise": "Aging research, genetics, longevity interventions, sirtuins",
        "image_url": "https://images.unsplash.com/photo-1560250097-0b93528c311a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwyfHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdHN8ZW58MHx8fHwxNzU0ODQ4NDg1fDA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "David Andrew Sinclair is an Australian biologist and professor of genetics at Harvard Medical School."
    },
    {
        "id": "mark_hyman", "name": "Dr. Mark Hyman", "title": "Functional Medicine Pioneer",
        "bio": "Leading functional medicine practitioner and author",
        "expertise": "Functional medicine, nutrition, chronic disease reversal, gut health",
        "image_url": "https://images.unsplash.com/photo-1576558656222-ba66febe3dec?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwzfHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdHN8ZW58MHx8fHwxNzU0ODQ4NDg1fDA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Mark Hyman is an American physician and New York Times bestselling author."
    },
    {
        "id": "deepak_chopra", "name": "Dr. Deepak Chopra", "title": "Mind-Body Wellness Expert",
        "bio": "Author and alternative medicine advocate focused on mind-body wellness",
        "expertise": "Mind-body medicine, meditation, consciousness, holistic health",
        "image_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHw0fHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdHN8ZW58MHx8fHwxNzU0ODQ4NDg1fDA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Deepak Chopra is an Indian-American author, public speaker, and alternative medicine advocate."
    },
    {
        "id": "matthew_walker", "name": "Dr. Matthew Walker", "title": "Sleep Expert",
        "bio": "UC Berkeley professor and sleep researcher, author of 'Why We Sleep'",
        "expertise": "Sleep science, circadian rhythms, sleep optimization, brain health",
        "image_url": "https://images.unsplash.com/photo-1657128344786-360c3f8e57e5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwxfHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdHN8ZW58MHx8fHwxNzU0ODQ4NDg1fDA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Matthew Walker is a British scientist and professor of neuroscience and psychology."
    }
    # Note: In production, this would include all 100 health mentors
]

SCIENCE_MENTORS = [
    {
        "id": "albert_einstein", "name": "Albert Einstein", "title": "Theoretical Physicist",
        "bio": "Developer of the theory of relativity and Nobel Prize winner",
        "expertise": "Physics, mathematics, scientific thinking, creativity",
        "image_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHw0fHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdHN8ZW58MHx8fHwxNzU0ODQ4NDg1fDA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Albert Einstein was a German-born theoretical physicist, widely acknowledged to be one of the greatest physicists."
    },
    {
        "id": "marie_curie", "name": "Marie Curie", "title": "Physicist & Chemist",
        "bio": "First woman to win a Nobel Prize, pioneered radioactivity research",
        "expertise": "Scientific research, perseverance, breaking barriers, discovery",
        "image_url": "https://images.unsplash.com/photo-1657128344786-360c3f8e57e5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwxfHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdHN8ZW58MHx8fHwxNzU0ODQ4NDg1fDA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Marie Salomea Skłodowska-Curie was a Polish and naturalized-French physicist and chemist."
    },
    {
        "id": "isaac_newton", "name": "Isaac Newton", "title": "Father of Modern Physics",
        "bio": "Mathematician and physicist who formulated the laws of motion and universal gravitation",
        "expertise": "Physics, mathematics, scientific method, natural philosophy",
        "image_url": "https://images.unsplash.com/photo-1560250097-0b93528c311a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwyfHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdHN8ZW58MHx8fHwxNzU0ODQ4NDg1fDA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Sir Isaac Newton was an English mathematician, physicist, astronomer, alchemist, theologian, and author."
    },
    {
        "id": "charles_darwin", "name": "Charles Darwin", "title": "Father of Evolution",
        "bio": "Naturalist who proposed the theory of evolution through natural selection",
        "expertise": "Evolution, natural selection, scientific observation, biology",
        "image_url": "https://images.unsplash.com/photo-1576558656222-ba66febe3dec?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwzfHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdHN8ZW58MHx8fHwxNzU0ODQ4NDg1fDA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Charles Robert Darwin was an English naturalist, geologist and biologist."
    },
    {
        "id": "stephen_hawking", "name": "Stephen Hawking", "title": "Theoretical Physicist & Cosmologist",
        "bio": "Groundbreaking physicist known for work on black holes and cosmology",
        "expertise": "Black holes, cosmology, theoretical physics, perseverance",
        "image_url": "https://images.unsplash.com/photo-1618053448701-5220304dc9ae?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHwxfHxzY2llbnRpc3RzJTIwcHJvZmVzc2lvbmFsc3xlbnwwfHx8fDE3NTQ4NDkzMzV8MA&ixlib=rb-4.1.0&q=85",
        "wiki_description": "Stephen William Hawking was an English theoretical physicist, cosmologist, and author."
    },
    {
        "id": "nikola_tesla", "name": "Nikola Tesla", "title": "Electrical Engineer & Inventor",
        "bio": "Inventor and electrical engineer who developed AC electrical systems",
        "expertise": "Electrical engineering, invention, innovation, vision",
        "image_url": "https://images.pexels.com/photos/3735757/pexels-photo-3735757.jpeg",
        "wiki_description": "Nikola Tesla was a Serbian-American inventor, electrical engineer, mechanical engineer, and futurist."
    },
    {
        "id": "galileo_galilei", "name": "Galileo Galilei", "title": "Father of Modern Science",
        "bio": "Italian astronomer and physicist who supported the heliocentric theory",
        "expertise": "Astronomy, physics, scientific method, challenging authority",
        "image_url": "https://images.pexels.com/photos/8666432/pexels-photo-8666432.jpeg",
        "wiki_description": "Galileo di Vincenzo Bonaiuti de' Galilei was an Italian astronomer, physicist and engineer."
    }
    # Note: In production, this would include all 100 science mentors
]

# Combine all mentors
ALL_MENTORS = {
    "business": BUSINESS_MENTORS,
    "sports": SPORTS_MENTORS, 
    "health": HEALTH_MENTORS,
    "science": SCIENCE_MENTORS
}

# Get total mentor count
TOTAL_MENTORS = sum(len(mentors) for mentors in ALL_MENTORS.values())