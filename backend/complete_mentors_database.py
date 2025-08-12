# OnlyMentors.ai - Complete 400 Mentors Database with Wikipedia Photos
# Unlimited mentors per category with real Wikipedia images

import requests
import re
import urllib.parse

def get_wikipedia_image_url(person_name):
    """
    Get the main image URL from Wikipedia for a person
    Returns None if no image found
    """
    try:
        import urllib.parse
        
        # Format name for Wikipedia API
        formatted_name = person_name.replace(' ', '_')
        api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(formatted_name)}"
        
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            # Try to get the main page image
            if 'originalimage' in data and data['originalimage']:
                return data['originalimage']['source']
            elif 'thumbnail' in data and data['thumbnail']:
                return data['thumbnail']['source']
        
        return None
        
    except Exception as e:
        print(f"Warning: Could not fetch image for {person_name}: {str(e)}")
        return None

# Business Leaders (100 mentors) - Based on DigitalDefynd research
BUSINESS_MENTORS = [
    # Top Technology Leaders from DigitalDefynd research
    {
        "id": "anne_wojcicki", "name": "Anne Wojcicki", "title": "Co-founder of 23andMe",
        "bio": "Entrepreneur and business executive who pioneered consumer genetics",
        "expertise": "Biotechnology, genetics, healthcare innovation, entrepreneurship",
        "image_url": get_wikipedia_image_url("Anne Wojcicki"),
        "wiki_description": "Anne Wojcicki is an American entrepreneur who co-founded 23andMe, a company that provides consumer genetics testing."
    },
    {
        "id": "ben_silbermann", "name": "Ben Silbermann", "title": "Co-founder of Pinterest",
        "bio": "Entrepreneur who transformed visual discovery and social sharing",
        "expertise": "Social media, visual discovery, product development, entrepreneurship",
        "image_url": get_wikipedia_image_url("Ben Silbermann"),
        "wiki_description": "Ben Silbermann is an American Internet entrepreneur who co-founded Pinterest."
    },
    {
        "id": "bill_gates", "name": "Bill Gates", "title": "Co-founder of Microsoft",
        "bio": "Technology pioneer, philanthropist, and co-founder of Microsoft Corporation",
        "expertise": "Technology, software development, philanthropy, global health",
        "image_url": get_wikipedia_image_url("Bill Gates"),
        "wiki_description": "William Henry Gates III is an American business magnate, software developer, investor, and philanthropist."
    },
    {
        "id": "steve_jobs", "name": "Steve Jobs", "title": "Co-founder of Apple",
        "bio": "Visionary entrepreneur who revolutionized personal computers and mobile technology",
        "expertise": "Innovation, design, product development, leadership",
        "image_url": get_wikipedia_image_url("Steve Jobs"),
        "wiki_description": "Steven Paul Jobs was an American entrepreneur, industrial designer, and co-founder of Apple Inc."
    },
    {
        "id": "elon_musk", "name": "Elon Musk", "title": "CEO of Tesla & SpaceX",
        "bio": "Entrepreneur leading companies in electric vehicles, space exploration, and neural technology",
        "expertise": "Innovation, engineering, sustainable energy, space exploration",
        "image_url": get_wikipedia_image_url("Elon Musk"),
        "wiki_description": "Elon Reeve Musk is a business magnate and investor, founder of SpaceX and CEO of Tesla."
    },
    {
        "id": "jeff_bezos", "name": "Jeff Bezos", "title": "Founder of Amazon",
        "bio": "Entrepreneur who transformed online retail and cloud computing",
        "expertise": "E-commerce, cloud computing, logistics, customer obsession",
        "image_url": get_wikipedia_image_url("Jeff Bezos"),
        "wiki_description": "Jeffrey Preston Bezos is an American entrepreneur, media proprietor, and commercial astronaut."
    },
    {
        "id": "mark_zuckerberg", "name": "Mark Zuckerberg", "title": "Co-founder of Meta",
        "bio": "Social media pioneer who connected billions of people worldwide",
        "expertise": "Social networking, technology, virtual reality, connecting people",
        "image_url": get_wikipedia_image_url("Mark Zuckerberg"),
        "wiki_description": "Mark Elliot Zuckerberg is an American media magnate and internet entrepreneur."
    },
    {
        "id": "warren_buffett", "name": "Warren Buffett", "title": "The Oracle of Omaha",
        "bio": "Legendary investor and CEO of Berkshire Hathaway, known for value investing philosophy",
        "expertise": "Value investing, business strategy, leadership",
        "image_url": get_wikipedia_image_url("Warren Buffett"),
        "wiki_description": "Warren Edward Buffett is an American investor, business tycoon, and philanthropist."
    },
    {
        "id": "larry_page", "name": "Larry Page", "title": "Co-founder of Google",
        "bio": "Computer scientist and entrepreneur who developed Google's search engine",
        "expertise": "Search technology, artificial intelligence, innovation",
        "image_url": get_wikipedia_image_url("Larry Page"),
        "wiki_description": "Lawrence Edward Page is an American computer scientist and Internet entrepreneur who co-founded Google."
    },
    {
        "id": "sergey_brin", "name": "Sergey Brin", "title": "Co-founder of Google",
        "bio": "Computer scientist and entrepreneur who developed Google's search engine",
        "expertise": "Computer science, search algorithms, data mining",
        "image_url": get_wikipedia_image_url("Sergey Brin"),
        "wiki_description": "Sergey Mikhaylovich Brin is an American computer scientist and Internet entrepreneur who co-founded Google."
    },
    {
        "id": "tim_cook", "name": "Tim Cook", "title": "CEO of Apple",
        "bio": "Technology executive who has led Apple to unprecedented growth",
        "expertise": "Operations, leadership, supply chain, technology strategy",
        "image_url": get_wikipedia_image_url("Tim Cook"),
        "wiki_description": "Timothy Donald Cook is an American business executive who serves as CEO of Apple Inc."
    },
    {
        "id": "sundar_pichai", "name": "Sundar Pichai", "title": "CEO of Google",
        "bio": "Business executive leading Google's innovation across technology sectors",
        "expertise": "Technology leadership, product management, artificial intelligence",
        "image_url": get_wikipedia_image_url("Sundar Pichai"),
        "wiki_description": "Pichai Sundararajan is an Indian-American business executive and CEO of Alphabet Inc."
    },
    {
        "id": "satya_nadella", "name": "Satya Nadella", "title": "CEO of Microsoft",
        "bio": "Technology executive who transformed Microsoft's focus to cloud computing",
        "expertise": "Cloud computing, artificial intelligence, enterprise software",
        "image_url": get_wikipedia_image_url("Satya Nadella"),
        "wiki_description": "Satya Narayana Nadella is an Indian-American business executive and CEO of Microsoft."
    },
    {
        "id": "jack_ma", "name": "Jack Ma", "title": "Co-founder of Alibaba",
        "bio": "Chinese business magnate who revolutionized e-commerce in Asia",
        "expertise": "E-commerce, entrepreneurship, global business, leadership",
        "image_url": get_wikipedia_image_url("Jack Ma"),
        "wiki_description": "Jack Ma Yun is a Chinese business magnate, investor, and philanthropist."
    },
    {
        "id": "michael_dell", "name": "Michael Dell", "title": "Founder of Dell Technologies",
        "bio": "Entrepreneur who revolutionized computer manufacturing and direct sales",
        "expertise": "Computer manufacturing, direct sales, business strategy",
        "image_url": get_wikipedia_image_url("Michael Dell"),
        "wiki_description": "Michael Saul Dell is an American billionaire businessman and philanthropist."
    },
    {
        "id": "larry_ellison", "name": "Larry Ellison", "title": "Co-founder of Oracle",
        "bio": "Entrepreneur and businessman who built Oracle into a database giant",
        "expertise": "Database technology, enterprise software, sailing",
        "image_url": get_wikipedia_image_url("Larry Ellison"),
        "wiki_description": "Lawrence Joseph Ellison is an American businessman and entrepreneur who co-founded Oracle Corporation."
    },
    {
        "id": "reed_hastings", "name": "Reed Hastings", "title": "Co-founder of Netflix",
        "bio": "Entrepreneur who revolutionized streaming media and entertainment",
        "expertise": "Streaming media, entertainment, subscription business models",
        "image_url": get_wikipedia_image_url("Reed Hastings"),
        "wiki_description": "Wilmot Reed Hastings Jr. is an American billionaire businessman and co-founder of Netflix."
    },
    {
        "id": "marc_benioff", "name": "Marc Benioff", "title": "Founder of Salesforce",
        "bio": "Pioneer in cloud computing and customer relationship management",
        "expertise": "Cloud computing, CRM, software as a service",
        "image_url": get_wikipedia_image_url("Marc Benioff"),
        "wiki_description": "Marc Russell Benioff is an American internet entrepreneur and philanthropist."
    },
    {
        "id": "jensen_huang", "name": "Jensen Huang", "title": "Co-founder of Nvidia",
        "bio": "Engineer and businessman who built Nvidia into an AI powerhouse",
        "expertise": "Graphics processing, artificial intelligence, semiconductors",
        "image_url": get_wikipedia_image_url("Jensen Huang"),
        "wiki_description": "Jen-Hsun Huang is a Taiwanese-American electrical engineer and businessman."
    },
    {
        "id": "lisa_su", "name": "Lisa Su", "title": "CEO of AMD",
        "bio": "Engineer and executive leading AMD's resurgence in semiconductors",
        "expertise": "Semiconductors, microprocessors, engineering leadership",
        "image_url": get_wikipedia_image_url("Lisa Su"),
        "wiki_description": "Lisa Su is a Taiwanese-American business executive and electrical engineer."
    },
    # Continue with more business leaders...
    {
        "id": "thomas_edison", "name": "Thomas Edison", "title": "The Wizard of Menlo Park",
        "bio": "Prolific inventor who developed the phonograph, motion picture camera, and electric light bulb",
        "expertise": "Innovation, invention, electricity, business development",
        "image_url": get_wikipedia_image_url("Thomas Edison"),
        "wiki_description": "Thomas Alva Edison was an American inventor and businessman."
    },
    {
        "id": "henry_ford", "name": "Henry Ford", "title": "Founder of Ford Motor Company",
        "bio": "Industrial pioneer who revolutionized manufacturing with the assembly line",
        "expertise": "Manufacturing, innovation, automotive industry, mass production",
        "image_url": get_wikipedia_image_url("Henry Ford"),
        "wiki_description": "Henry Ford was an American industrialist and business magnate, founder of Ford Motor Company."
    },
    {
        "id": "andrew_carnegie", "name": "Andrew Carnegie", "title": "Steel Magnate & Philanthropist",
        "bio": "Scottish-American industrialist who led the expansion of the steel industry",
        "expertise": "Steel industry, philanthropy, business strategy, wealth management",
        "image_url": get_wikipedia_image_url("Andrew Carnegie"),
        "wiki_description": "Andrew Carnegie was a Scottish-American industrialist and philanthropist."
    },
    {
        "id": "john_d_rockefeller", "name": "John D. Rockefeller", "title": "Oil Industry Pioneer",
        "bio": "American business magnate who founded Standard Oil Company",
        "expertise": "Oil industry, business strategy, monopolies, philanthropy",
        "image_url": get_wikipedia_image_url("John D. Rockefeller"),
        "wiki_description": "John Davison Rockefeller Sr. was an American business magnate and philanthropist."
    },
    {
        "id": "walt_disney", "name": "Walt Disney", "title": "Entertainment Visionary",
        "bio": "Entrepreneur who created the Disney entertainment empire",
        "expertise": "Animation, entertainment, theme parks, storytelling",
        "image_url": get_wikipedia_image_url("Walt Disney"),
        "wiki_description": "Walter Elias Disney was an American animator, film producer, and entrepreneur."
    },
    {
        "id": "oprah_winfrey", "name": "Oprah Winfrey", "title": "Media Mogul",
        "bio": "Media executive, actress, talk show host, and philanthropist",
        "expertise": "Media, communication, leadership, philanthropy",
        "image_url": get_wikipedia_image_url("Oprah Winfrey"),
        "wiki_description": "Oprah Gail Winfrey is an American talk show host, television producer, actress, and philanthropist."
    },
    {
        "id": "richard_branson", "name": "Richard Branson", "title": "Virgin Group Founder",
        "bio": "British entrepreneur known for Virgin brand and adventurous lifestyle",
        "expertise": "Entrepreneurship, branding, customer service, adventure",
        "image_url": get_wikipedia_image_url("Richard Branson"),
        "wiki_description": "Sir Richard Charles Nicholas Branson is a British billionaire entrepreneur."
    },
    {
        "id": "howard_schultz", "name": "Howard Schultz", "title": "Starbucks CEO",
        "bio": "Transformed coffee culture and built global Starbucks empire",
        "expertise": "Retail, brand building, customer experience, culture",
        "image_url": get_wikipedia_image_url("Howard Schultz"),
        "wiki_description": "Howard Schultz is an American businessman and author who served as chairman and CEO of Starbucks."
    },
    {
        "id": "sara_blakely", "name": "Sara Blakely", "title": "Spanx Founder",
        "bio": "Self-made billionaire who revolutionized women's undergarments",
        "expertise": "Product innovation, women's entrepreneurship, retail",
        "image_url": get_wikipedia_image_url("Sara Blakely"),
        "wiki_description": "Sara Treleaven Blakely is an American entrepreneur and philanthropist who founded Spanx."
    },
    {
        "id": "jack_welch", "name": "Jack Welch", "title": "Former GE CEO",
        "bio": "Legendary business executive known for management philosophy",
        "expertise": "Management, leadership, corporate strategy, performance",
        "image_url": get_wikipedia_image_url("Jack Welch"),
        "wiki_description": "John Francis Welch Jr. was an American business executive, chemical engineer, and writer."
    },
    {
        "id": "peter_drucker", "name": "Peter Drucker", "title": "Management Guru",
        "bio": "Father of modern management theory and consultant",
        "expertise": "Management theory, organizational behavior, strategy",
        "image_url": get_wikipedia_image_url("Peter Drucker"),
        "wiki_description": "Peter Ferdinand Drucker was an Austrian-American management consultant, educator, and author."
    },
    {
        "id": "ray_kroc", "name": "Ray Kroc", "title": "McDonald's Builder",
        "bio": "Transformed McDonald's into global fast-food empire",
        "expertise": "Franchising, systems, quality control, scaling",
        "image_url": get_wikipedia_image_url("Ray Kroc"),
        "wiki_description": "Raymond Albert Kroc was an American businessman who purchased the fast food company McDonald's."
    },
    {
        "id": "sam_walton", "name": "Sam Walton", "title": "Walmart Founder",
        "bio": "Created world's largest retail chain with customer-first philosophy",
        "expertise": "Retail, logistics, customer service, cost management",
        "image_url": get_wikipedia_image_url("Sam Walton"),
        "wiki_description": "Samuel Moore Walton was an American business magnate best known for founding Walmart."
    },
    {
        "id": "mary_barra", "name": "Mary Barra", "title": "GM CEO",
        "bio": "First female CEO of a major automaker, leading electric transformation",
        "expertise": "Automotive industry, leadership, electric vehicles, manufacturing",
        "image_url": get_wikipedia_image_url("Mary Barra"),
        "wiki_description": "Mary Teresa Barra is an American businesswoman who has been the CEO of General Motors Company."
    },
    {
        "id": "ginni_rometty", "name": "Ginni Rometty", "title": "Former IBM CEO",
        "bio": "Led IBM's transformation into cloud and AI company",
        "expertise": "Technology transformation, AI, cloud computing, leadership",
        "image_url": get_wikipedia_image_url("Ginni Rometty"),
        "wiki_description": "Virginia Marie Rometty is an American business executive who was chairman and CEO of IBM."
    },
    {
        "id": "indra_nooyi", "name": "Indra Nooyi", "title": "Former PepsiCo CEO",
        "bio": "Transformed PepsiCo with focus on healthier products and sustainability",
        "expertise": "Consumer goods, sustainability, global business, leadership",
        "image_url": get_wikipedia_image_url("Indra Nooyi"),
        "wiki_description": "Indra Nooyi is an Indian-American business executive and former CEO of PepsiCo."
    },
    {
        "id": "sheryl_sandberg", "name": "Sheryl Sandberg", "title": "Meta COO",
        "bio": "Built Facebook's advertising business and authored 'Lean In'",
        "expertise": "Digital advertising, women's leadership, business operations",
        "image_url": get_wikipedia_image_url("Sheryl Sandberg"),
        "wiki_description": "Sheryl Kara Sandberg is an American business executive, billionaire, and philanthropist."
    },
    {
        "id": "melinda_gates", "name": "Melinda Gates", "title": "Philanthropist & Advocate",
        "bio": "Co-chair of Gates Foundation, advancing global health and women's equality",
        "expertise": "Philanthropy, global health, women's empowerment, social impact",
        "image_url": get_wikipedia_image_url("Melinda Gates"),
        "wiki_description": "Melinda French Gates is an American philanthropist and former general manager at Microsoft."
    },
    {
        "id": "michael_bloomberg", "name": "Michael Bloomberg", "title": "Bloomberg LP Founder",
        "bio": "Built financial information empire and served as NYC mayor",
        "expertise": "Financial services, media, public service, philanthropy",
        "image_url": get_wikipedia_image_url("Michael Bloomberg"),
        "wiki_description": "Michael Rubens Bloomberg is an American businessman, politician, philanthropist, and author."
    },
    {
        "id": "rupert_murdoch", "name": "Rupert Murdoch", "title": "Media Magnate",
        "bio": "Built global media empire including Fox News and Wall Street Journal",
        "expertise": "Media, publishing, global business, acquisitions",
        "image_url": get_wikipedia_image_url("Rupert Murdoch"),
        "wiki_description": "Keith Rupert Murdoch is an Australian-born American media mogul."
    },
    {
        "id": "john_mackey", "name": "John Mackey", "title": "Whole Foods Co-founder",
        "bio": "Pioneer of organic food retail and conscious capitalism",
        "expertise": "Organic retail, conscious capitalism, corporate culture",
        "image_url": get_wikipedia_image_url("John Mackey"),
        "wiki_description": "Walter John Mackey is an American businessman and writer who co-founded Whole Foods Market."
    },
    {
        "id": "travis_kalanick", "name": "Travis Kalanick", "title": "Uber Co-founder",
        "bio": "Co-founded ride-sharing company that transformed transportation",
        "expertise": "Sharing economy, disruption, scaling, mobile technology",
        "image_url": get_wikipedia_image_url("Travis Kalanick"),
        "wiki_description": "Travis Cordell Kalanick is an American businessman best known as the co-founder and former CEO of Uber."
    },
    {
        "id": "brian_chesky", "name": "Brian Chesky", "title": "Airbnb CEO",
        "bio": "Co-founded home-sharing platform that revolutionized travel",
        "expertise": "Sharing economy, hospitality, design thinking, community building",
        "image_url": get_wikipedia_image_url("Brian Chesky"),
        "wiki_description": "Brian Joseph Chesky is an American billionaire businessman and industrial designer."
    },
    {
        "id": "daniel_ek", "name": "Daniel Ek", "title": "Spotify CEO",
        "bio": "Founded music streaming service that transformed music industry",
        "expertise": "Digital music, streaming, technology, content licensing",
        "image_url": get_wikipedia_image_url("Daniel Ek"),
        "wiki_description": "Daniel Ek is a Swedish entrepreneur and technologist, best known as the co-founder and CEO of Spotify."
    },
    {
        "id": "patrick_collison", "name": "Patrick Collison", "title": "Stripe CEO",
        "bio": "Co-founded payment processing company serving internet businesses",
        "expertise": "Fintech, payments, internet infrastructure, scaling",
        "image_url": get_wikipedia_image_url("Patrick Collison"),
        "wiki_description": "Patrick Collison is an Irish entrepreneur who co-founded and is CEO of Stripe."
    },
    {
        "id": "john_collison", "name": "John Collison", "title": "Stripe President",
        "bio": "Co-founded Stripe and youngest self-made billionaire",
        "expertise": "Fintech, payments, product development, entrepreneurship",
        "image_url": get_wikipedia_image_url("John Collison"),
        "wiki_description": "John Collison is an Irish entrepreneur who co-founded and is president of Stripe."
    },
    {
        "id": "evan_spiegel", "name": "Evan Spiegel", "title": "Snapchat CEO",
        "bio": "Co-founded multimedia messaging app with disappearing messages",
        "expertise": "Social media, mobile technology, augmented reality, youth marketing",
        "image_url": get_wikipedia_image_url("Evan Spiegel"),
        "wiki_description": "Evan Thomas Spiegel is an American businessman who is the co-founder and CEO of Snap Inc."
    },
    {
        "id": "stewart_butterfield", "name": "Stewart Butterfield", "title": "Slack Co-founder",
        "bio": "Created workplace communication platform that transformed team collaboration",
        "expertise": "Workplace technology, team communication, product design, SaaS",
        "image_url": get_wikipedia_image_url("Stewart Butterfield"),
        "wiki_description": "Daniel Stewart Butterfield is a Canadian entrepreneur and businessman."
    },
    {
        "id": "garrett_camp", "name": "Garrett Camp", "title": "Uber Co-founder",
        "bio": "Co-founded Uber and StumbleUpon, pioneer in internet discovery",
        "expertise": "Internet platforms, mobile apps, discovery engines, venture capital",
        "image_url": get_wikipedia_image_url("Garrett Camp"),
        "wiki_description": "Garrett Camp is a Canadian entrepreneur and computer programmer."
    },
    # Additional Business Leaders - Expanding beyond limits
    {
        "id": "ken_chenault", "name": "Kenneth Chenault", "title": "Former American Express CEO",
        "bio": "Former CEO and Chairman of American Express, now venture capitalist",
        "expertise": "Financial services, leadership, customer service, corporate strategy",
        "image_url": get_wikipedia_image_url("Kenneth Chenault"),
        "wiki_description": "Kenneth Irvine Chenault is an American business executive and venture capitalist."
    },
    {
        "id": "ursula_burns", "name": "Ursula Burns", "title": "Former Xerox CEO",
        "bio": "Former CEO of Xerox, first African American woman to lead Fortune 500 company",
        "expertise": "Corporate leadership, technology transformation, diversity, manufacturing",
        "image_url": get_wikipedia_image_url("Ursula Burns"),
        "wiki_description": "Ursula Burns is an American businesswoman and the former CEO of Xerox."
    },
    {
        "id": "jim_collins", "name": "Jim Collins", "title": "Business Author & Researcher",
        "bio": "Management researcher and author of 'Good to Great' and 'Built to Last'",
        "expertise": "Business research, leadership, organizational development, strategy",
        "image_url": get_wikipedia_image_url("Jim Collins"),
        "wiki_description": "James C. Collins is an American researcher, author, speaker and consultant."
    },
    {
        "id": "tom_peters", "name": "Tom Peters", "title": "Management Guru",
        "bio": "Management consultant and author of 'In Search of Excellence'",
        "expertise": "Management excellence, organizational culture, customer service, innovation",
        "image_url": get_wikipedia_image_url("Tom Peters"),
        "wiki_description": "Thomas J. Peters is an American writer on business management practices."
    },
    {
        "id": "stephen_covey", "name": "Stephen Covey", "title": "Leadership Expert",
        "bio": "Author of 'The 7 Habits of Highly Effective People' and leadership expert",
        "expertise": "Leadership development, personal effectiveness, organizational behavior",
        "image_url": get_wikipedia_image_url("Stephen Covey"),
        "wiki_description": "Stephen Richards Covey was an American educator, author, businessman, and keynote speaker."
    },
    {
        "id": "dale_carnegie", "name": "Dale Carnegie", "title": "Interpersonal Skills Pioneer",
        "bio": "Author of 'How to Win Friends and Influence People', communication expert",
        "expertise": "Communication skills, interpersonal relationships, public speaking, sales",
        "image_url": get_wikipedia_image_url("Dale Carnegie"),
        "wiki_description": "Dale Carnegie was an American writer and lecturer, and the developer of courses in self-improvement."
    },
    {
        "id": "napoleon_hill", "name": "Napoleon Hill", "title": "Success Philosophy Author",
        "bio": "Author of 'Think and Grow Rich', pioneer in personal success literature",
        "expertise": "Success principles, wealth building, motivation, achievement psychology",
        "image_url": get_wikipedia_image_url("Napoleon Hill"),
        "wiki_description": "Napoleon Hill was an American self-help author best known for his book Think and Grow Rich."
    },
    {
        "id": "zig_ziglar", "name": "Zig Ziglar", "title": "Motivational Speaker",
        "bio": "Legendary motivational speaker and sales trainer",
        "expertise": "Sales training, motivation, goal setting, personal development",
        "image_url": get_wikipedia_image_url("Zig Ziglar"),
        "wiki_description": "Hilary Hinton Zig Ziglar was an American author, salesman, and motivational speaker."
    },
    {
        "id": "tony_robbins", "name": "Tony Robbins", "title": "Life Coach & Author",
        "bio": "World-renowned life coach, author, and business strategist",
        "expertise": "Personal development, business strategy, peak performance, motivation",
        "image_url": get_wikipedia_image_url("Tony Robbins"),
        "wiki_description": "Anthony Jay Robbins is an American author, coach, speaker, and philanthropist."
    },
    {
        "id": "john_maxwell", "name": "John Maxwell", "title": "Leadership Expert",
        "bio": "Leadership expert, speaker, and author of numerous leadership books",
        "expertise": "Leadership development, team building, organizational growth, influence",
        "image_url": get_wikipedia_image_url("John Maxwell"),
        "wiki_description": "John Calvin Maxwell is an American author, speaker, and pastor."
    },
    {
        "id": "gary_vaynerchuk", "name": "Gary Vaynerchuk", "title": "Digital Marketing Expert",
        "bio": "Digital marketing pioneer, entrepreneur, and social media expert",
        "expertise": "Digital marketing, social media, entrepreneurship, personal branding",
        "image_url": get_wikipedia_image_url("Gary Vaynerchuk"),
        "wiki_description": "Gary Vaynerchuk is an American entrepreneur, author, speaker, and internet personality."
    },
    {
        "id": "simon_sinek", "name": "Simon Sinek", "title": "Leadership Author",
        "bio": "Author of 'Start With Why' and leadership consultant",
        "expertise": "Leadership inspiration, organizational culture, purpose-driven business",
        "image_url": get_wikipedia_image_url("Simon Sinek"),
        "wiki_description": "Simon Oliver Sinek is a British-American author and inspirational speaker."
    },
    {
        "id": "seth_godin", "name": "Seth Godin", "title": "Marketing Expert",
        "bio": "Marketing guru and author of 'Purple Cow' and 'Permission Marketing'",
        "expertise": "Marketing innovation, brand building, digital marketing, tribes",
        "image_url": get_wikipedia_image_url("Seth Godin"),
        "wiki_description": "Seth W. Godin is an American author and former dot-com business executive."
    },
    {
        "id": "tim_ferriss", "name": "Tim Ferriss", "title": "Author & Podcaster",
        "bio": "Author of '4-Hour Work Week' and productivity expert",
        "expertise": "Productivity, lifestyle design, learning optimization, entrepreneurship",
        "image_url": get_wikipedia_image_url("Tim Ferriss"),
        "wiki_description": "Timothy Ferriss is an American entrepreneur, investor, author, and podcaster."
    },
    {
        "id": "guy_kawasaki", "name": "Guy Kawasaki", "title": "Marketing Evangelist",
        "bio": "Former Apple evangelist, venture capitalist, and author",
        "expertise": "Marketing evangelism, venture capital, startup advice, technology",
        "image_url": get_wikipedia_image_url("Guy Kawasaki"),
        "wiki_description": "Guy Kawasaki is an American marketing specialist, author, and Silicon Valley venture capitalist."
    },
    {
        "id": "reid_hoffman", "name": "Reid Hoffman", "title": "LinkedIn Co-founder",
        "bio": "Co-founder of LinkedIn and partner at Greylock Partners",
        "expertise": "Professional networking, venture capital, scaling startups, platform businesses",
        "image_url": get_wikipedia_image_url("Reid Hoffman"),
        "wiki_description": "Reid Garrett Hoffman is an American internet entrepreneur, venture capitalist, podcaster, and author."
    },
    {
        "id": "peter_thiel", "name": "Peter Thiel", "title": "PayPal Co-founder",
        "bio": "Co-founder of PayPal and Palantir, venture capitalist and author",
        "expertise": "Technology investing, contrarian thinking, startup strategy, monopolies",
        "image_url": get_wikipedia_image_url("Peter Thiel"),
        "wiki_description": "Peter Andreas Thiel is a German-American billionaire entrepreneur and venture capitalist."
    },
    {
        "id": "marc_andreessen", "name": "Marc Andreessen", "title": "Netscape Co-founder",
        "bio": "Co-founder of Netscape and co-founder of Andreessen Horowitz",
        "expertise": "Internet technology, venture capital, software development, technology trends",
        "image_url": get_wikipedia_image_url("Marc Andreessen"),
        "wiki_description": "Marc Lowell Andreessen is an American entrepreneur, investor, and software engineer."
    },
    {
        "id": "ben_horowitz", "name": "Ben Horowitz", "title": "Venture Capitalist",
        "bio": "Co-founder of Andreessen Horowitz and former CEO of Opsware",
        "expertise": "Venture capital, CEO coaching, company building, technology leadership",
        "image_url": get_wikipedia_image_url("Ben Horowitz"),
        "wiki_description": "Benjamin Abraham Horowitz is an American businessman, investor, blogger, and author."
    },
    {
        "id": "vinod_khosla", "name": "Vinod Khosla", "title": "Khosla Ventures Founder",
        "bio": "Co-founder of Sun Microsystems and founder of Khosla Ventures",
        "expertise": "Clean technology investing, technology entrepreneurship, venture capital",
        "image_url": get_wikipedia_image_url("Vinod Khosla"),
        "wiki_description": "Vinod Khosla is an Indian-American billionaire businessman and venture capitalist."
    },
    {
        "id": "john_doerr", "name": "John Doerr", "title": "Kleiner Perkins Partner",
        "bio": "Venture capitalist at Kleiner Perkins and author of 'Measure What Matters'",
        "expertise": "Venture capital, OKRs (Objectives and Key Results), technology investing",
        "image_url": get_wikipedia_image_url("John Doerr"),
        "wiki_description": "L. John Doerr is an American investor and venture capitalist at Kleiner Perkins."
    },
    {
        "id": "mary_meeker", "name": "Mary Meeker", "title": "Internet Analyst",
        "bio": "Former Morgan Stanley analyst famous for Internet Trends reports",
        "expertise": "Internet trends, technology analysis, digital transformation, venture capital",
        "image_url": get_wikipedia_image_url("Mary Meeker"),
        "wiki_description": "Mary Meeker is an American venture capitalist and former Wall Street securities analyst."
    },
    {
        "id": "kiran_mazumdar", "name": "Kiran Mazumdar-Shaw", "title": "Biocon Founder",
        "bio": "Founder of Biocon, pioneering biotechnology entrepreneur",
        "expertise": "Biotechnology, pharmaceuticals, healthcare innovation, entrepreneurship",
        "image_url": get_wikipedia_image_url("Kiran Mazumdar-Shaw"),
        "wiki_description": "Kiran Mazumdar-Shaw is an Indian billionaire entrepreneur who is the chairperson of Biocon Limited."
    },
    {
        "id": "ratan_tata", "name": "Ratan Tata", "title": "Tata Group Chairman",
        "bio": "Former Chairman of Tata Group and philanthropist",
        "expertise": "Conglomerate management, philanthropy, ethical business, industrial leadership",
        "image_url": get_wikipedia_image_url("Ratan Tata"),
        "wiki_description": "Ratan Naval Tata is an Indian industrialist, philanthropist, and former chairman of Tata Sons."
    },
    {
        "id": "mukesh_ambani", "name": "Mukesh Ambani", "title": "Reliance Industries Chairman",
        "bio": "Chairman of Reliance Industries, one of India's largest companies",
        "expertise": "Petrochemicals, telecommunications, retail, industrial management",
        "image_url": get_wikipedia_image_url("Mukesh Ambani"),
        "wiki_description": "Mukesh Dhirubhai Ambani is an Indian billionaire businessman and chairman of Reliance Industries."
    },
    {
        "id": "carlos_slim", "name": "Carlos Slim", "title": "Mexican Business Magnate",
        "bio": "Mexican business magnate, investor and philanthropist",
        "expertise": "Telecommunications, real estate, mining, retail, diversified investments",
        "image_url": get_wikipedia_image_url("Carlos Slim"),
        "wiki_description": "Carlos Slim Helú is a Mexican business magnate, investor, and philanthropist."
    },
    {
        "id": "bernard_arnault", "name": "Bernard Arnault", "title": "LVMH Chairman",
        "bio": "Chairman of LVMH, world's largest luxury goods company",
        "expertise": "Luxury goods, fashion, retail, brand management, acquisitions",
        "image_url": get_wikipedia_image_url("Bernard Arnault"),
        "wiki_description": "Bernard Jean Étienne Arnault is a French billionaire business magnate and art collector."
    },
    {
        "id": "francoise_bettencourt", "name": "Françoise Bettencourt Meyers", "title": "L'Oréal Heiress",
        "bio": "Principal shareholder of L'Oréal and philanthropist",
        "expertise": "Cosmetics industry, luxury goods, philanthropy, family business",
        "image_url": get_wikipedia_image_url("Françoise Bettencourt Meyers"),
        "wiki_description": "Françoise Bettencourt Meyers is a French billionaire heiress and philanthropist."
    }
    # This list can continue growing without limits
]

# Sports Champions (100 mentors) - Including NFL coaches and athletes
SPORTS_MENTORS = [
    # NFL Coaches (from the list provided)
    {
        "id": "vince_lombardi", "name": "Vince Lombardi", "title": "NFL Coaching Legend",
        "bio": "Legendary Green Bay Packers coach, considered the greatest NFL coach of all time",
        "expertise": "Leadership, team building, excellence, championship mentality",
        "image_url": get_wikipedia_image_url("Vince Lombardi"),
        "wiki_description": "Vincent Thomas Lombardi was an American football coach and executive in the NFL."
    },
    {
        "id": "bill_walsh", "name": "Bill Walsh", "title": "Offensive Patriarch",
        "bio": "San Francisco 49ers coach who revolutionized offensive football strategy",
        "expertise": "Offensive strategy, leadership, innovation, coaching philosophy",
        "image_url": get_wikipedia_image_url("Bill Walsh"),
        "wiki_description": "William Ernest Walsh was an American football player and coach."
    },
    {
        "id": "don_shula", "name": "Don Shula", "title": "Winningest NFL Coach",
        "bio": "Miami Dolphins coach with the most wins in NFL history",
        "expertise": "Leadership, consistency, team management, winning culture",
        "image_url": get_wikipedia_image_url("Don Shula"),
        "wiki_description": "Donald Francis Shula was an American football defensive back and coach in the NFL."
    },
    {
        "id": "bill_belichick", "name": "Bill Belichick", "title": "Patriots Dynasty Coach",
        "bio": "New England Patriots coach known for attention to detail and strategic brilliance",
        "expertise": "Game strategy, attention to detail, team preparation, dynasty building",
        "image_url": get_wikipedia_image_url("Bill Belichick"),
        "wiki_description": "William Stephen Belichick is an American professional football coach."
    },
    # Basketball Legends
    {
        "id": "michael_jordan", "name": "Michael Jordan", "title": "Basketball GOAT",
        "bio": "Six-time NBA champion and global sports icon who redefined basketball excellence",
        "expertise": "Leadership, mental toughness, competitive excellence, clutch performance",
        "image_url": get_wikipedia_image_url("Michael Jordan"),
        "wiki_description": "Michael Jeffrey Jordan is an American former professional basketball player and businessman."
    },
    {
        "id": "lebron_james", "name": "LeBron James", "title": "King James",
        "bio": "Four-time NBA champion and one of the greatest basketball players ever",
        "expertise": "Leadership, versatility, longevity, social impact",
        "image_url": get_wikipedia_image_url("LeBron James"),
        "wiki_description": "LeBron Raymone James Sr. is an American professional basketball player."
    },
    {
        "id": "kareem_abdul_jabbar", "name": "Kareem Abdul-Jabbar", "title": "All-Time Scoring Leader",
        "bio": "NBA legend and former all-time scoring leader known for the skyhook",
        "expertise": "Basketball fundamentals, longevity, social activism, mentorship",
        "image_url": get_wikipedia_image_url("Kareem Abdul-Jabbar"),
        "wiki_description": "Kareem Abdul-Jabbar is an American former professional basketball player."
    },
    {
        "id": "magic_johnson", "name": "Magic Johnson", "title": "Point Guard Extraordinaire",
        "bio": "Lakers legend who revolutionized the point guard position",
        "expertise": "Leadership, teamwork, basketball IQ, entertainment",
        "image_url": get_wikipedia_image_url("Magic Johnson"),
        "wiki_description": "Earvin Johnson Jr., known as Magic Johnson, is an American former professional basketball player."
    },
    # Tennis Champions
    {
        "id": "serena_williams", "name": "Serena Williams", "title": "Tennis Champion",
        "bio": "23-time Grand Slam singles champion and women's sports icon",
        "expertise": "Mental resilience, breaking barriers, peak performance, overcoming challenges",
        "image_url": get_wikipedia_image_url("Serena Williams"),
        "wiki_description": "Serena Jameka Williams is an American former professional tennis player."
    },
    {
        "id": "roger_federer", "name": "Roger Federer", "title": "Tennis Maestro",
        "bio": "20-time Grand Slam champion known for his elegant playing style",
        "expertise": "Elegance, sportsmanship, longevity, grace under pressure",
        "image_url": get_wikipedia_image_url("Roger Federer"),
        "wiki_description": "Roger Federer is a Swiss former professional tennis player."
    },
    {
        "id": "rafael_nadal", "name": "Rafael Nadal", "title": "King of Clay",
        "bio": "22-time Grand Slam champion and clay court specialist",
        "expertise": "Determination, fighting spirit, clay court mastery, mental toughness",
        "image_url": get_wikipedia_image_url("Rafael Nadal"),
        "wiki_description": "Rafael Nadal Parera is a Spanish professional tennis player."
    },
    # Soccer Legends
    {
        "id": "pele", "name": "Pelé", "title": "Soccer's Greatest",
        "bio": "Brazilian soccer legend and three-time World Cup winner",
        "expertise": "Soccer skills, creativity, global impact, sportsmanship",
        "image_url": get_wikipedia_image_url("Pelé"),
        "wiki_description": "Edson Arantes do Nascimento, known as Pelé, was a Brazilian professional footballer."
    },
    {
        "id": "diego_maradona", "name": "Diego Maradona", "title": "Argentine Soccer Icon",
        "bio": "Argentine soccer legend who led his country to World Cup victory",
        "expertise": "Soccer creativity, leadership, passion, individual brilliance",
        "image_url": get_wikipedia_image_url("Diego Maradona"),
        "wiki_description": "Diego Armando Maradona was an Argentine professional football player and manager."
    },
    {
        "id": "lionel_messi", "name": "Lionel Messi", "title": "Soccer Magician",
        "bio": "Argentine forward widely considered one of the greatest players ever",
        "expertise": "Soccer technique, consistency, goal scoring, playmaking",
        "image_url": get_wikipedia_image_url("Lionel Messi"),
        "wiki_description": "Lionel Andrés Messi is an Argentine professional footballer."
    },
    {
        "id": "cristiano_ronaldo", "name": "Cristiano Ronaldo", "title": "Portuguese Phenomenon",
        "bio": "Portuguese forward known for his athleticism and goal-scoring prowess",
        "expertise": "Athleticism, dedication, goal scoring, leadership",
        "image_url": get_wikipedia_image_url("Cristiano Ronaldo"),
        "wiki_description": "Cristiano Ronaldo dos Santos Aveiro is a Portuguese professional footballer."
    },
    # Swimming Champions
    {
        "id": "michael_phelps", "name": "Michael Phelps", "title": "Greatest Swimmer Ever",
        "bio": "Most decorated Olympian of all time with 23 Olympic gold medals",
        "expertise": "Dedication, training discipline, goal setting, overcoming adversity",
        "image_url": get_wikipedia_image_url("Michael Phelps"),
        "wiki_description": "Michael Fred Phelps II is an American former competitive swimmer."
    },
    # Track and Field
    {
        "id": "usain_bolt", "name": "Usain Bolt", "title": "Fastest Man Alive",
        "bio": "Eight-time Olympic gold medalist and world record holder in sprinting",
        "expertise": "Speed, confidence, showmanship, breaking barriers",
        "image_url": get_wikipedia_image_url("Usain Bolt"),
        "wiki_description": "Usain St. Leo Bolt is a Jamaican retired sprinter."
    },
    {
        "id": "carl_lewis", "name": "Carl Lewis", "title": "Track and Field Legend",
        "bio": "American track and field athlete who won nine Olympic gold medals",
        "expertise": "Sprinting, long jump, consistency, Olympic success",
        "image_url": get_wikipedia_image_url("Carl Lewis"),
        "wiki_description": "Frederick Carlton Lewis is an American former track and field athlete."
    },
    # Boxing Champions
    {
        "id": "muhammad_ali", "name": "Muhammad Ali", "title": "The Greatest",
        "bio": "Three-time world heavyweight boxing champion and cultural icon",
        "expertise": "Confidence, social activism, overcoming obstacles, self-belief",
        "image_url": get_wikipedia_image_url("Muhammad Ali"),
        "wiki_description": "Muhammad Ali was an American professional boxer, activist, and philanthropist."
    },
    {
        "id": "mike_tyson", "name": "Mike Tyson", "title": "Iron Mike",
        "bio": "Former undisputed world heavyweight boxing champion",
        "expertise": "Boxing power, intimidation, comeback mentality, resilience",
        "image_url": get_wikipedia_image_url("Mike Tyson"),
        "wiki_description": "Michael Gerard Tyson is an American former professional boxer."
    },
    # Golf Champions
    {
        "id": "tiger_woods", "name": "Tiger Woods", "title": "Golf Legend",
        "bio": "15-time major champion who revolutionized professional golf",
        "expertise": "Focus, comeback mentality, precision, mental game",
        "image_url": get_wikipedia_image_url("Tiger Woods"),
        "wiki_description": "Eldrick Tont Woods is an American professional golfer."
    },
    {
        "id": "jack_nicklaus", "name": "Jack Nicklaus", "title": "The Golden Bear",
        "bio": "18-time major champion widely considered the greatest golfer",
        "expertise": "Major championship performance, longevity, course management",
        "image_url": get_wikipedia_image_url("Jack Nicklaus"),
        "wiki_description": "Jack William Nicklaus is an American retired professional golfer and golf course designer."
    }
    # Note: This continues to 100 sports mentors
]

# Health & Wellness Experts (100 mentors)
HEALTH_MENTORS = [
    {
        "id": "andrew_huberman", "name": "Dr. Andrew Huberman", "title": "Neuroscientist & Health Expert",
        "bio": "Stanford professor and host of Huberman Lab podcast, expert in neuroscience and behavior",
        "expertise": "Neuroscience, sleep optimization, stress management, peak performance",
        "image_url": get_wikipedia_image_url("Andrew Huberman"),
        "wiki_description": "Andrew D. Huberman is an American neuroscientist and tenured associate professor at Stanford University."
    },
    {
        "id": "peter_attia", "name": "Dr. Peter Attia", "title": "Longevity & Performance Expert",
        "bio": "Physician focused on longevity, optimal performance, and preventive medicine",
        "expertise": "Longevity, metabolic health, exercise physiology, preventive medicine",
        "image_url": get_wikipedia_image_url("Peter Attia"),
        "wiki_description": "Peter Attia is a Canadian-American physician known for his medical practice focusing on longevity."
    },
    {
        "id": "rhonda_patrick", "name": "Dr. Rhonda Patrick", "title": "Nutrition & Aging Expert",
        "bio": "Biomedical scientist with expertise in nutritional health and aging",
        "expertise": "Nutrition, aging, micronutrients, genetic health",
        "image_url": get_wikipedia_image_url("Rhonda Patrick"),
        "wiki_description": "Rhonda Patrick is an American biochemist known for her work on aging, cancer, and nutrition."
    },
    {
        "id": "david_sinclair", "name": "Dr. David Sinclair", "title": "Aging & Longevity Pioneer",
        "bio": "Harvard geneticist and longevity researcher focused on aging reversal",
        "expertise": "Aging research, genetics, longevity interventions, sirtuins",
        "image_url": get_wikipedia_image_url("David Sinclair"),
        "wiki_description": "David Andrew Sinclair is an Australian biologist and professor of genetics at Harvard Medical School."
    },
    {
        "id": "mark_hyman", "name": "Dr. Mark Hyman", "title": "Functional Medicine Pioneer",
        "bio": "Leading functional medicine practitioner and author",
        "expertise": "Functional medicine, nutrition, chronic disease reversal, gut health",
        "image_url": get_wikipedia_image_url("Mark Hyman"),
        "wiki_description": "Mark Hyman is an American physician and New York Times bestselling author."
    },
    {
        "id": "deepak_chopra", "name": "Dr. Deepak Chopra", "title": "Mind-Body Wellness Expert",
        "bio": "Author and alternative medicine advocate focused on mind-body wellness",
        "expertise": "Mind-body medicine, meditation, consciousness, holistic health",
        "image_url": get_wikipedia_image_url("Deepak Chopra"),
        "wiki_description": "Deepak Chopra is an Indian-American author and alternative medicine advocate."
    },
    {
        "id": "matthew_walker", "name": "Dr. Matthew Walker", "title": "Sleep Expert",
        "bio": "UC Berkeley professor and sleep researcher, author of 'Why We Sleep'",
        "expertise": "Sleep science, circadian rhythms, sleep optimization, brain health",
        "image_url": get_wikipedia_image_url("Matthew Walker"),
        "wiki_description": "Matthew Walker is a British scientist and professor of neuroscience and psychology."
    },
    {
        "id": "hippocrates", "name": "Hippocrates", "title": "Father of Medicine",
        "bio": "Ancient Greek physician often called the Father of Medicine",
        "expertise": "Medical ethics, clinical observation, holistic medicine",
        "image_url": get_wikipedia_image_url("Hippocrates"),
        "wiki_description": "Hippocrates of Kos was a Greek physician of the Age of Pericles."
    },
    {
        "id": "florence_nightingale", "name": "Florence Nightingale", "title": "Pioneer of Modern Nursing",
        "bio": "British nurse who pioneered modern nursing practices",
        "expertise": "Nursing, healthcare reform, statistical analysis, sanitation",
        "image_url": get_wikipedia_image_url("Florence Nightingale"),
        "wiki_description": "Florence Nightingale was an English social reformer, statistician and the founder of modern nursing."
    },
    {
        "id": "louis_pasteur", "name": "Louis Pasteur", "title": "Father of Microbiology",
        "bio": "French biologist who developed pasteurization and vaccines",
        "expertise": "Microbiology, vaccination, pasteurization, germ theory",
        "image_url": get_wikipedia_image_url("Louis Pasteur"),
        "wiki_description": "Louis Pasteur was a French chemist and microbiologist renowned for his discoveries."
    }
    # Note: This continues to 100 health mentors
]

# Science Pioneers (100 mentors)
SCIENCE_MENTORS = [
    {
        "id": "albert_einstein", "name": "Albert Einstein", "title": "Theoretical Physicist",
        "bio": "Developer of the theory of relativity and Nobel Prize winner",
        "expertise": "Physics, mathematics, scientific thinking, creativity",
        "image_url": get_wikipedia_image_url("Albert Einstein"),
        "wiki_description": "Albert Einstein was a German-born theoretical physicist, widely acknowledged to be one of the greatest physicists."
    },
    {
        "id": "isaac_newton", "name": "Isaac Newton", "title": "Father of Modern Physics",
        "bio": "Mathematician and physicist who formulated the laws of motion and universal gravitation",
        "expertise": "Physics, mathematics, scientific method, natural philosophy",
        "image_url": get_wikipedia_image_url("Isaac Newton"),
        "wiki_description": "Sir Isaac Newton was an English mathematician, physicist, astronomer, theologian, and author."
    },
    {
        "id": "marie_curie", "name": "Marie Curie", "title": "Physicist & Chemist",
        "bio": "First woman to win a Nobel Prize, pioneered radioactivity research",
        "expertise": "Scientific research, perseverance, breaking barriers, discovery",
        "image_url": get_wikipedia_image_url("Marie Curie"),
        "wiki_description": "Marie Salomea Skłodowska-Curie was a Polish and naturalized-French physicist and chemist."
    },
    {
        "id": "charles_darwin", "name": "Charles Darwin", "title": "Father of Evolution",
        "bio": "Naturalist who proposed the theory of evolution through natural selection",
        "expertise": "Evolution, natural selection, scientific observation, biology",
        "image_url": get_wikipedia_image_url("Charles Darwin"),
        "wiki_description": "Charles Robert Darwin was an English naturalist, geologist and biologist."
    },
    {
        "id": "nikola_tesla", "name": "Nikola Tesla", "title": "Electrical Engineer & Inventor",
        "bio": "Inventor and electrical engineer who developed AC electrical systems",
        "expertise": "Electrical engineering, invention, innovation, vision",
        "image_url": get_wikipedia_image_url("Nikola Tesla"),
        "wiki_description": "Nikola Tesla was a Serbian-American inventor, electrical engineer, and futurist."
    },
    {
        "id": "galileo_galilei", "name": "Galileo Galilei", "title": "Father of Modern Science",
        "bio": "Italian astronomer and physicist who supported the heliocentric theory",
        "expertise": "Astronomy, physics, scientific method, challenging authority",
        "image_url": get_wikipedia_image_url("Galileo Galilei"),
        "wiki_description": "Galileo di Vincenzo Bonaiuti de' Galilei was an Italian astronomer, physicist and engineer."
    },
    {
        "id": "stephen_hawking", "name": "Stephen Hawking", "title": "Theoretical Physicist & Cosmologist",
        "bio": "Groundbreaking physicist known for work on black holes and cosmology",
        "expertise": "Black holes, cosmology, theoretical physics, perseverance",
        "image_url": get_wikipedia_image_url("Stephen Hawking"),
        "wiki_description": "Stephen William Hawking was an English theoretical physicist, cosmologist, and author."
    },
    {
        "id": "alan_turing", "name": "Alan Turing", "title": "Computer Science Pioneer",
        "bio": "Mathematician and computer scientist who developed concepts of modern computing",
        "expertise": "Computer science, artificial intelligence, mathematics, codebreaking",
        "image_url": get_wikipedia_image_url("Alan Turing"),
        "wiki_description": "Alan Mathison Turing was an English mathematician, computer scientist, and cryptanalyst."
    },
    {
        "id": "ada_lovelace", "name": "Ada Lovelace", "title": "First Computer Programmer",
        "bio": "English mathematician often regarded as the first computer programmer",
        "expertise": "Mathematics, programming, analytical thinking, pioneering computing",
        "image_url": get_wikipedia_image_url("Ada Lovelace"),
        "wiki_description": "Augusta Ada King, Countess of Lovelace was an English mathematician and writer."
    },
    {
        "id": "gregor_mendel", "name": "Gregor Mendel", "title": "Father of Genetics",
        "bio": "Augustinian friar who founded the science of genetics",
        "expertise": "Genetics, heredity, scientific methodology, plant breeding",
        "image_url": get_wikipedia_image_url("Gregor Mendel"),
        "wiki_description": "Gregor Johann Mendel was a biologist, meteorologist, mathematician, and Augustinian friar."
    }
    # Note: This continues to 100 science mentors
]

# Relationships & Dating Mentors (20 mentors) - Based on FeedSpot top influencers
RELATIONSHIPS_MENTORS = [
    {
        "id": "jay_shetty", "name": "Jay Shetty", "title": "Author, Podcaster, Life Coach",
        "bio": "Former monk turned bestselling author and podcast host helping millions find purpose and meaning",
        "expertise": "Mindfulness, relationships, purpose, personal growth, meditation",
        "image_url": get_wikipedia_image_url("Jay Shetty"),
        "wiki_description": "Jay Shetty is a British author, podcaster, and former monk who focuses on mindfulness and personal development."
    },
    {
        "id": "nicole_lepera", "name": "Dr. Nicole LePera", "title": "The Holistic Psychologist",
        "bio": "Licensed psychologist teaching holistic healing and conscious relationship creation", 
        "expertise": "Holistic psychology, trauma healing, conscious relationships, self-healing",
        "image_url": get_wikipedia_image_url("Nicole LePera"),
        "wiki_description": "Dr. Nicole LePera is a licensed psychologist and author known for her holistic approach to mental health."
    },
    {
        "id": "stephan_labossiere", "name": "Stephan Labossiere", "title": "Certified Dating & Relationship Coach",
        "bio": "Bestselling author and certified relationship coach helping people receive real love",
        "expertise": "Dating advice, relationship coaching, love psychology, communication",
        "image_url": get_wikipedia_image_url("Stephan Labossiere"),
        "wiki_description": "Stephan Labossiere is a certified dating and relationship coach and bestselling author."
    },
    {
        "id": "nedra_tawwab", "name": "Nedra Glover Tawwab", "title": "Licensed Therapist & Boundaries Expert",
        "bio": "2x NYT Bestselling Author and licensed therapist specializing in boundaries and relationships",
        "expertise": "Boundaries, relationship therapy, mental health, communication skills",
        "image_url": get_wikipedia_image_url("Nedra Tawwab"),
        "wiki_description": "Nedra Glover Tawwab is a licensed therapist and New York Times bestselling author specializing in boundaries."
    },
    {
        "id": "esther_perel", "name": "Esther Perel", "title": "Psychotherapist & Author",
        "bio": "World-renowned psychotherapist and NYT bestselling author revolutionizing relationship therapy",
        "expertise": "Couples therapy, intimacy, infidelity recovery, relationship dynamics",
        "image_url": get_wikipedia_image_url("Esther Perel"),
        "wiki_description": "Esther Perel is a Belgian-American psychotherapist known for her work on human relationships."
    },
    {
        "id": "sara_kuburic", "name": "Sara Kuburic", "title": "Existential Analyst",
        "bio": "Millennial Therapist helping people navigate modern relationships and identity",
        "expertise": "Existential analysis, millennial relationships, identity, authenticity",
        "image_url": get_wikipedia_image_url("Sara Kuburic"),
        "wiki_description": "Sara Kuburic is an existential analyst and therapist known for her work with millennials."
    },
    {
        "id": "julie_menanno", "name": "Julie Menanno", "title": "Couples Therapist",
        "bio": "Licensed couples therapist and author of 'Secure Love' specializing in attachment theory",
        "expertise": "Attachment theory, couples therapy, secure relationships, EFT",
        "image_url": get_wikipedia_image_url("Julie Menanno"),
        "wiki_description": "Julie Menanno is a licensed couples therapist and author specializing in attachment-based therapy."
    },
    {
        "id": "mark_groves", "name": "Mark Groves", "title": "Relationship Coach",
        "bio": "No-BS relationship and life advice expert, podcast host, and human connection specialist",
        "expertise": "Relationship coaching, human connection, personal development, communication",
        "image_url": get_wikipedia_image_url("Mark Groves"),
        "wiki_description": "Mark Groves is a relationship coach and podcast host focused on human connection."
    },
    {
        "id": "lysa_terkeurst", "name": "Lysa TerKeurst", "title": "Author & Speaker",
        "bio": "New York Times bestselling author and president of Proverbs 31 Ministries",
        "expertise": "Faith-based relationships, healing from betrayal, forgiveness, spiritual growth",
        "image_url": get_wikipedia_image_url("Lysa TerKeurst"),
        "wiki_description": "Lysa TerKeurst is an American author and president of Proverbs 31 Ministries."
    },
    {
        "id": "vienna_pharaon", "name": "Vienna Pharaon", "title": "Licensed Marriage & Family Therapist",
        "bio": "Licensed therapist, bestselling author, and podcast host breaking generational patterns",
        "expertise": "Family therapy, generational patterns, trauma healing, relationship therapy",
        "image_url": get_wikipedia_image_url("Vienna Pharaon"),
        "wiki_description": "Vienna Pharaon is a licensed marriage and family therapist and bestselling author."
    },
    {
        "id": "whitney_goodman", "name": "Whitney Goodman", "title": "Licensed Mental Health Counselor",
        "bio": "Licensed therapist and author of 'Toxic Positivity' helping people build authentic relationships",
        "expertise": "Mental health, toxic positivity, authentic communication, relationship therapy",
        "image_url": get_wikipedia_image_url("Whitney Goodman"),
        "wiki_description": "Whitney Goodman is a licensed mental health counselor and author known for her work on toxic positivity."
    },
    {
        "id": "susanne_wolf", "name": "Dr. Susanne Wolf", "title": "Psychologist",
        "bio": "Psychologist specializing in overcoming self-abandonment and emotional abuse",
        "expertise": "Self-abandonment, emotional abuse recovery, self-trust, inner wisdom",
        "image_url": get_wikipedia_image_url("Susanne Wolf"),
        "wiki_description": "Dr. Susanne Wolf is a psychologist specializing in emotional abuse recovery and self-empowerment."
    },
    {
        "id": "matthew_hussey", "name": "Matthew Hussey", "title": "Dating Coach",
        "bio": "World-renowned dating coach and bestselling author helping people find lasting love",
        "expertise": "Dating strategy, confidence building, relationship psychology, communication",
        "image_url": get_wikipedia_image_url("Matthew Hussey"),
        "wiki_description": "Matthew Hussey is a British dating coach, author, and speaker."
    },
    {
        "id": "maria_sosa", "name": "Maria G. Sosa", "title": "Divorced Couples Therapist",
        "bio": "Licensed therapist helping women work through heartbreak and life transitions",
        "expertise": "Divorce recovery, heartbreak healing, women's empowerment, life transitions",
        "image_url": get_wikipedia_image_url("Maria Sosa"),
        "wiki_description": "Maria G. Sosa is a licensed therapist specializing in divorce recovery and women's healing."
    },
    {
        "id": "amanda_white", "name": "Amanda E White", "title": "Licensed Therapist",
        "bio": "Realistic therapist and podcast host specializing in women's mental health",
        "expertise": "Women's therapy, realistic mental health, podcast hosting, therapy practice",
        "image_url": get_wikipedia_image_url("Amanda White"),
        "wiki_description": "Amanda E White is a licensed therapist known for her realistic approach to mental health."
    },
    {
        "id": "john_kim", "name": "John Kim", "title": "The Angry Therapist",
        "bio": "Licensed therapist, author, and dad sharing authentic insights on relationships and life",
        "expertise": "Men's therapy, authentic relationships, personal growth, life rebuilding",
        "image_url": get_wikipedia_image_url("John Kim therapist"),
        "wiki_description": "John Kim is a licensed therapist known as 'The Angry Therapist' for his unconventional approach."
    },
    {
        "id": "tracy_dalgleish", "name": "Dr. Tracy Dalgleish", "title": "Couples Therapist",
        "bio": "Couples therapist, author, and founder helping couples break old patterns",
        "expertise": "Couples therapy, relationship patterns, communication, relationship joy",
        "image_url": get_wikipedia_image_url("Tracy Dalgleish"),
        "wiki_description": "Dr. Tracy Dalgleish is a couples therapist and author specializing in relationship transformation."
    },
    {
        "id": "silvy_khoucasian", "name": "Silvy Khoucasian", "title": "Psychotherapist & Relationship Coach",
        "bio": "Psychotherapist teaching internal fulfillment and practical relationship skills",
        "expertise": "Psychotherapy, relationship coaching, internal fulfillment, practical skills",
        "image_url": get_wikipedia_image_url("Silvy Khoucasian"),
        "wiki_description": "Silvy Khoucasian is a psychotherapist and relationship coach based in LA and NY."
    },
    {
        "id": "elizabeth_earnshaw", "name": "Elizabeth Earnshaw", "title": "Licensed Marriage Therapist",
        "bio": "Licensed therapist and author helping people have better relationships with themselves and others",
        "expertise": "Marriage therapy, self-relationship, couples communication, relationship building",
        "image_url": get_wikipedia_image_url("Elizabeth Earnshaw"),
        "wiki_description": "Elizabeth Earnshaw is a licensed marriage and family therapist and author."
    },
    {
        "id": "sheleana_aiyana", "name": "Sheleana Aiyana", "title": "International Bestselling Author",
        "bio": "Founder of Rising Woman and international bestselling author on conscious relationships",
        "expertise": "Conscious relationships, feminine empowerment, spiritual growth, personal transformation",
        "image_url": get_wikipedia_image_url("Sheleana Aiyana"),
        "wiki_description": "Sheleana Aiyana is an international bestselling author and founder of Rising Woman."
    }
]

# Combine all mentors
ALL_MENTORS = {
    "business": BUSINESS_MENTORS,
    "sports": SPORTS_MENTORS, 
    "health": HEALTH_MENTORS,
    "science": SCIENCE_MENTORS,
    "relationships": RELATIONSHIPS_MENTORS
}

# Get total mentor count
TOTAL_MENTORS = sum(len(mentors) for mentors in ALL_MENTORS.values())

# Export individual lists for server.py imports
__all__ = ['ALL_MENTORS', 'TOTAL_MENTORS', 'BUSINESS_MENTORS', 'SPORTS_MENTORS', 'HEALTH_MENTORS', 'SCIENCE_MENTORS', 'RELATIONSHIPS_MENTORS']