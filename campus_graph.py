"""
Campus Knowledge Graph & Architectural Blueprint
Manipal University Jaipur (MUJ)
Includes exact user landmarks:
- AB1, AB2, AB3, AB4 (Academic Blocks 1-4 with detailed 3-floor architectural maps)
- Incubation Center
- Central Library & New Library
- Grand Stairs, Flap Gates, Main Exit, Parking
- Seminar Halls, Football Ground, Sports Complex, Cricket Ground
- Cafeteria, Auditorium, Admin Block, Hostel Village, Amphitheatre

Every block contains:
- 3 Complete Floors (Floor 1 Ground, Floor 2, Floor 3)
- Detailed Elevator/Lift positioning: Left side, Right side, or Both sides
- Staircases: Central stairwells, Emergency stairwells, Grand Stairs
- Balconies: Floor balconies, Quad-viewing corridors, Terrace verandas
- Floor-specific labs, cabins, and amenities
"""

import math
from typing import Dict, List, Any, Optional

# Complete Campus Landmarks with Deep Architectural Blueprint Metadata
CAMPUS_NODES: Dict[str, Dict[str, Any]] = {
    # 1. Main Gate & Entry Corridor
    "MAIN_EXIT": {
        "id": "MAIN_EXIT",
        "name": "Campus Main Exit & Grand Portal",
        "short_name": "Main Exit",
        "category": "transit",
        "zone": "Front Plaza",
        "x": 500,
        "y": 60,
        "description": "Primary vehicle and pedestrian egress with 24/7 security booth, taxi bays, and visitor registration.",
        "icon": "shield-check",
        "has_floors": False,
        "floors_count": 1,
        "amenities": ["Security Desk", "Visitor Badge Kiosk", "Taxi Bay", "CCTV Post"]
    },
    "PARKING": {
        "id": "PARKING",
        "name": "Central Campus Parking & EV Hub",
        "short_name": "Parking",
        "category": "transit",
        "zone": "North Perimeter",
        "x": 280,
        "y": 90,
        "description": "Multi-tier parking area with dedicated solar EV charging stalls, two-wheeler bays, and faculty parking.",
        "icon": "truck",
        "has_floors": False,
        "floors_count": 1,
        "amenities": ["12x EV Fast Chargers", "Two-Wheeler Zone", "Shaded Solar Canopy"]
    },
    "FLAP_GATES": {
        "id": "FLAP_GATES",
        "name": "Biometric Smart Flap Gates",
        "short_name": "Flap Gates",
        "category": "transit",
        "zone": "North Quad Entrance",
        "x": 500,
        "y": 140,
        "description": "High-throughput RFID card swipe and facial recognition smart optical turnstiles leading to academic core.",
        "icon": "check-circle",
        "has_floors": False,
        "floors_count": 1,
        "amenities": ["RFID Sensors", "Facial Scanners", "Hand Sanitizer Station", "Guard Kiosk"]
    },

    # 2. Academic Block 1 (AB1)
    "AB1": {
        "id": "AB1",
        "name": "Academic Block 1 (AB1)",
        "short_name": "AB1",
        "category": "academic",
        "zone": "West Academic Wing",
        "x": 300,
        "y": 210,
        "description": "Houses Pure Sciences, First Year Engineering, and Department of Computer Science.",
        "icon": "book",
        "has_floors": True,
        "floors_count": 3,
        "lift_side": "left",
        "lift_summary": "High-speed 12-passenger elevator located on the LEFT side of the main foyer (adjacent to Room 102).",
        "stairs_summary": "Main Central Staircase on left wing; Emergency Fire Exit staircase at the Far Right corridor.",
        "balcony_summary": "Spacious open balcony on Floors 2 & 3 overlooking the North Lawn and Parking area.",
        "floors": {
            1: {
                "floor_name": "Ground Floor (Floor 1)",
                "lift": {"side": "left", "details": "Left-hand foyer elevator (Cabin A1, access to Floors 1-3)"},
                "stairs": {"location": "North-West main stairwell (Left of lobby) + East emergency exit stairs"},
                "balcony": {"location": "West Ground Patio & Shaded Veranda opening to green garden"},
                "key_rooms": ["Dean Office", "Physics & Chemistry Labs", "Classrooms 101-106", "Restrooms (Left Wing)"]
            },
            2: {
                "floor_name": "Floor 2",
                "lift": {"side": "left", "details": "Left wing elevator landing directly opposite the Computer Vision Lab"},
                "stairs": {"location": "Central Left stairwell with wide turning landing; South emergency stairs"},
                "balcony": {"location": "Expansive North Balcony with panoramic views of the Parking & Front Gate"},
                "key_rooms": ["AI & Data Mining Lab", "Computer Programming Lab 201-204", "Faculty Cabins (Left)"]
            },
            3: {
                "floor_name": "Floor 3",
                "lift": {"side": "left", "details": "Left wing elevator terminus (Floor 3 exit facing Seminar Room 301)"},
                "stairs": {"location": "Left stairwell continuing to terrace; Right wing fire exit escape door"},
                "balcony": {"location": "Elevated Sunset Balcony with open-air student discussion benches"},
                "key_rooms": ["Advanced Cyber Security Lab", "High-Performance GPU Cluster Suite", "Conference Hall 302"]
            }
        },
        "amenities": ["Elevator (Left)", "Air Conditioned Labs", "Water Dispenser", "Fire Alarms"]
    },

    # 3. Academic Block 2 (AB2)
    "AB2": {
        "id": "AB2",
        "name": "Academic Block 2 (AB2)",
        "short_name": "AB2",
        "category": "academic",
        "zone": "East Academic Wing",
        "x": 700,
        "y": 210,
        "description": "Department of Electronics, Communication, and Embedded Systems Engineering.",
        "icon": "cpu",
        "has_floors": True,
        "floors_count": 3,
        "lift_side": "right",
        "lift_summary": "Elevator bank situated on the RIGHT side of the entrance corridor (next to Lab 110).",
        "stairs_summary": "Central marble staircase in main atrium; spiral iron fire stairs on Left exterior wing.",
        "balcony_summary": "East-facing balconies on Floors 2 & 3 looking toward the Cricket Ground and Pavilion.",
        "floors": {
            1: {
                "floor_name": "Ground Floor (Floor 1)",
                "lift": {"side": "right", "details": "Right-hand atrium lift (Cabins B1 & B2, voice-assisted)"},
                "stairs": {"location": "Grand Atrium Center Stairs + Left wing exterior metal fire escape"},
                "balcony": {"location": "East Sunken Garden Porch with seating for 30 students"},
                "key_rooms": ["Digital Electronics Lab", "Microprocessor Systems Lab", "Classrooms 107-112"]
            },
            2: {
                "floor_name": "Floor 2",
                "lift": {"side": "right", "details": "Right-hand landing beside the VLSI Design Research Center"},
                "stairs": {"location": "Central staircase landing with student notice boards; Left emergency stairs"},
                "balcony": {"location": "East Promenade Balcony overlooking University Cricket Ground"},
                "key_rooms": ["VLSI Design Center", "RF & Microwave Lab", "Faculty Cabins (Right Wing)"]
            },
            3: {
                "floor_name": "Floor 3",
                "lift": {"side": "right", "details": "Right-hand lift landing directly in front of the Robotics Arena"},
                "stairs": {"location": "Central staircase to Floor 3 + rooftop maintenance access hatch"},
                "balcony": {"location": "High-altitude Observation Balcony facing East Horizon and Cricket Oval"},
                "key_rooms": ["Autonomous Robotics Bay", "Embedded IoT Lab", "Department Library"]
            }
        },
        "amenities": ["Elevator (Right)", "Prototyping Tools", "Locker Area", "Restrooms (Right)"]
    },

    # 4. Academic Block 3 (AB3)
    "AB3": {
        "id": "AB3",
        "name": "Academic Block 3 (AB3)",
        "short_name": "AB3",
        "category": "academic",
        "zone": "West Central Quad",
        "x": 300,
        "y": 380,
        "description": "Mechanical, Mechatronics, and Civil Engineering complex with manufacturing workshops.",
        "icon": "zap",
        "has_floors": True,
        "floors_count": 3,
        "lift_side": "both",
        "lift_summary": "Dual elevators on BOTH SIDES: Left elevator for passengers; Right heavy-duty service elevator.",
        "stairs_summary": "Dual symmetrical staircases on both Left & Right wings + Central Grand Stairs connection.",
        "balcony_summary": "Long connecting corridors with open-air balustrades overlooking the Central Grand Stairs.",
        "floors": {
            1: {
                "floor_name": "Ground Floor (Floor 1)",
                "lift": {"side": "both", "details": "Left passenger lift + Right heavy-load freight elevator (workshop access)"},
                "stairs": {"location": "North Left stairwell + South Right stairwell with wide landings"},
                "balcony": {"location": "Covered Courtyard Arcade opening to Grand Central Stairs"},
                "key_rooms": ["CNC Machine Shop", "Fluid Mechanics Lab", "Materials Testing Lab 101-105"]
            },
            2: {
                "floor_name": "Floor 2",
                "lift": {"side": "both", "details": "Dual elevator access (Left and Right wings)"},
                "stairs": {"location": "Left & Right wing staircases with cross-corridor connection"},
                "balcony": {"location": "Central Viewing Balcony directly framing the Grand Central Stairs"},
                "key_rooms": ["CAD / CAM Design Suite", "Thermodynamics Simulation Lab", "Lecture Theatres 201-204"]
            },
            3: {
                "floor_name": "Floor 3",
                "lift": {"side": "both", "details": "Both elevators reach Floor 3; Right lift opens to Mechatronics Bay"},
                "stairs": {"location": "Left & Right stairways reaching upper level faculty suites"},
                "balcony": {"location": "Panoramic Terraced Balcony overlooking Central Plaza and Grand Stairs"},
                "key_rooms": ["Mechatronics & Automation Bay", "Aeronautical Modelling Suite", "Senior Project Studios"]
            }
        },
        "amenities": ["Dual Elevators (Both Sides)", "Heavy Load Lift", "Maker Spaces", "Filtered Water Stations"]
    },

    # 5. Academic Block 4 (AB4)
    "AB4": {
        "id": "AB4",
        "name": "Academic Block 4 (AB4)",
        "short_name": "AB4",
        "category": "academic",
        "zone": "East Central Quad",
        "x": 700,
        "y": 380,
        "description": "School of Management, Design Arts, Computational Mathematics, and Soft Computing.",
        "icon": "layers",
        "has_floors": True,
        "floors_count": 3,
        "lift_side": "left",
        "lift_summary": "Modern glass-walled scenic elevator situated on the LEFT wing overlooking the indoor atrium.",
        "stairs_summary": "Sweeping central architectural staircase with timber treads + Right wing fire exit stairs.",
        "balcony_summary": "Glass-railed architectural balconies on Floors 2 & 3 facing the Central Lawn.",
        "floors": {
            1: {
                "floor_name": "Ground Floor (Floor 1)",
                "lift": {"side": "left", "details": "Left glass scenic elevator (Cabin C1, panoramic glass facade)"},
                "stairs": {"location": "Central geometric open stairs + Right corridor fire stairwell"},
                "balcony": {"location": "Ground Level Sun Deck with outdoor wooden tables and umbrellas"},
                "key_rooms": ["Design Thinking Studio", "FinTech Trading Terminal", "Classrooms 115-120"]
            },
            2: {
                "floor_name": "Floor 2",
                "lift": {"side": "left", "details": "Left scenic lift landing with indoor lounge and charging dock"},
                "stairs": {"location": "Central floating staircase landing + Right wing exit stairs"},
                "balcony": {"location": "Open Glass Balcony overlooking the Grand Stairs & Central Fountain"},
                "key_rooms": ["Soft Computing & Neural Networks Lab", "Case Study Rooms", "Faculty Cabins (Left)"]
            },
            3: {
                "floor_name": "Floor 3",
                "lift": {"side": "left", "details": "Left scenic elevator top terminus"},
                "stairs": {"location": "Central staircase access to top level; Right stairwell to roof"},
                "balcony": {"location": "Rooftop Sky Lounge Balcony with scenic views across the Sports Complex"},
                "key_rooms": ["Executive Boardroom", "Digital Media & Animation Lab", "Analytics Suite 305"]
            }
        },
        "amenities": ["Scenic Elevator (Left)", "Media Suites", "High Speed Wi-Fi 6", "Restrooms (Both Wings)"]
    },

    # 6. Grand Stairs & Central Plaza
    "GRAND_STAIRS": {
        "id": "GRAND_STAIRS",
        "name": "The Grand Central Stairs & Sunken Plaza",
        "short_name": "Grand Stairs",
        "category": "life",
        "zone": "Central Core",
        "x": 500,
        "y": 360,
        "description": "Monumental wide stone amphitheatre-style stairs connecting upper academic boulevard to sunken fountain plaza.",
        "icon": "trending-up",
        "has_floors": False,
        "floors_count": 1,
        "amenities": ["Seating Steps", "Solar Charging Benches", "Sunken Garden", "Outdoor Lighting"]
    },

    # 7. Central Library & New Library
    "CENTRAL_LIB": {
        "id": "CENTRAL_LIB",
        "name": "Central University Library",
        "short_name": "Central Library",
        "category": "academic",
        "zone": "Central Core",
        "x": 500,
        "y": 240,
        "description": "The heritage central repository with 250,000 print books, research archives, and silent reading halls.",
        "icon": "book-open",
        "has_floors": True,
        "floors_count": 3,
        "lift_side": "right",
        "lift_summary": "Silent whisper-quiet hydraulic elevator on the RIGHT side of the circulation desk.",
        "stairs_summary": "Majestic central spiral mahogany staircase + Left wing secondary staircase.",
        "balcony_summary": "Floor 2 & 3 quiet study balconies overlooking the North Quad gardens.",
        "floors": {
            1: {
                "floor_name": "Ground Floor (Floor 1)",
                "lift": {"side": "right", "details": "Right corridor lift beside the main book return counter"},
                "stairs": {"location": "Central Grand Spiral Staircase + Left wing rear stairs"},
                "balcony": {"location": "Front Garden Portico with outdoor newspaper reading desks"},
                "key_rooms": ["Circulation Desk", "Periodicals & Journals", "Reference Section", "Baggage Counter"]
            },
            2: {
                "floor_name": "Floor 2",
                "lift": {"side": "right", "details": "Right lift landing near Engineering & Science Stacks"},
                "stairs": {"location": "Central spiral stairs landing with silent carpeted floor; Left stairs"},
                "balcony": {"location": "North Silent Reading Balcony with individual acoustic pods"},
                "key_rooms": ["Engineering & Computer Science Stacks", "Silent Study Hall A", "Digital Kiosks"]
            },
            3: {
                "floor_name": "Floor 3",
                "lift": {"side": "right", "details": "Right lift landing at Research & Theses Archive"},
                "stairs": {"location": "Central stairs termination + Left stairwell for emergency access"},
                "balcony": {"location": "Upper Terrace Balcony with panoramic views of AB1 and AB2"},
                "key_rooms": ["Doctoral Theses Archive", "Rare Manuscript Vault", "Group Discussion Rooms (1-6)"]
            }
        },
        "amenities": ["Elevator (Right)", "Silent Study Pods", "Self-Checkout RFID", "Digital Archives"]
    },

    "NEW_LIB": {
        "id": "NEW_LIB",
        "name": "New Digital Library & Learning Commons",
        "short_name": "New Library",
        "category": "academic",
        "zone": "East Tech Quad",
        "x": 860,
        "y": 240,
        "description": "Ultra-modern glass pavilion equipped with VR research cubes, 100+ digital workstations, and collaborative pods.",
        "icon": "monitor",
        "has_floors": True,
        "floors_count": 3,
        "lift_side": "both",
        "lift_summary": "Elevators available on BOTH SIDES: Left elevator serves public floors; Right serves staff & faculty.",
        "stairs_summary": "Cantilevered glass staircase in central lightwell; rear fire exit stairs.",
        "balcony_summary": "Wraparound modern glass terrace balcony on Floor 3 with views of the Cricket Ground.",
        "floors": {
            1: {
                "floor_name": "Ground Floor (Floor 1)",
                "lift": {"side": "both", "details": "Left public elevator + Right staff/service elevator"},
                "stairs": {"location": "Central cantilevered glass stairs + East fire exit stairwell"},
                "balcony": {"location": "Ground Terrace Café & outdoor reading pavilion"},
                "key_rooms": ["24/7 Digital Cyber Lounge", "E-Resource Helpdesk", "VR Research Sandbox"]
            },
            2: {
                "floor_name": "Floor 2",
                "lift": {"side": "both", "details": "Dual elevator landings on Left and Right wings"},
                "stairs": {"location": "Central glass staircase + East fire escape door"},
                "balcony": {"location": "East Promenade Balcony overlooking University Cricket Ground"},
                "key_rooms": ["Interactive Collaboration Pods", "Data Visualization Wall", "Kindle & E-Reader Zone"]
            },
            3: {
                "floor_name": "Floor 3",
                "lift": {"side": "both", "details": "Both elevators reach Floor 3 Executive Research Suites"},
                "stairs": {"location": "Glass staircase termination point with skylight dome above"},
                "balcony": {"location": "Panoramic Rooftop Sky-Balcony with botanical potted gardens"},
                "key_rooms": ["Faculty Research Suites", "Video Conferencing Studio", "Silent Scholar Cubicles"]
            }
        },
        "amenities": ["Dual Elevators (Both Sides)", "VR Sandbox", "24/7 Access", "Espresso Bar"]
    },

    # 8. Incubation Center & Seminar Halls
    "INCUBATION": {
        "id": "INCUBATION",
        "name": "Nova Venture & Incubation Center",
        "short_name": "Incubation",
        "category": "academic",
        "zone": "West Tech Quad",
        "x": 140,
        "y": 260,
        "description": "Student startup accelerator, prototyping lab, patent filing cell, and venture capital meeting suites.",
        "icon": "lightbulb",
        "has_floors": True,
        "floors_count": 3,
        "lift_side": "left",
        "lift_summary": "Elevator on LEFT side next to the startup pitch arena.",
        "stairs_summary": "Open industrial staircase with steel balustrade in center; rear fire exit stairs.",
        "balcony_summary": "Makers balcony on Floor 2 overlooking the botanical tree canopy.",
        "floors": {
            1: {
                "floor_name": "Ground Floor (Floor 1)",
                "lift": {"side": "left", "details": "Left wing elevator (direct access to Co-Working spaces)"},
                "stairs": {"location": "Center industrial open staircase + North fire stairs"},
                "balcony": {"location": "Ground Green Courtyard Patio with coffee bar"},
                "key_rooms": ["Pitch Auditorium", "Maker Space & 3D Printers", "Visitor Reception"]
            },
            2: {
                "floor_name": "Floor 2",
                "lift": {"side": "left", "details": "Left elevator opens directly into Startup Co-Working Bay"},
                "stairs": {"location": "Center stairs + North exit staircase"},
                "balcony": {"location": "Makers Balcony overlooking West Botanical Garden"},
                "key_rooms": ["Hot-Desk Co-Working Hall", "Meeting Pods (A-F)", "Legal & IPR Cell"]
            },
            3: {
                "floor_name": "Floor 3",
                "lift": {"side": "left", "details": "Left elevator top landing"},
                "stairs": {"location": "Center stairs + roof access door"},
                "balcony": {"location": "Venture Terrace Balcony with outdoor barbecue and lounge"},
                "key_rooms": ["Angel Investor Lounge", "Executive Boardroom", "Incubatee Private Offices"]
            }
        },
        "amenities": ["Elevator (Left)", "3D Printing Farm", "Pitch Deck Screen", "High-Speed Wi-Fi"]
    },

    "SEMINAR_HALLS": {
        "id": "SEMINAR_HALLS",
        "name": "MUJ Executive Seminar Halls Complex",
        "short_name": "Seminar Halls",
        "category": "academic",
        "zone": "Central South Core",
        "x": 500,
        "y": 480,
        "description": "Tiered multimedia lecture theatres equipped for international symposia and academic conventions.",
        "icon": "mic",
        "has_floors": True,
        "floors_count": 3,
        "lift_side": "both",
        "lift_summary": "Dual high-capacity elevators on BOTH SIDES of the registration lobby.",
        "stairs_summary": "Wide ceremonial twin staircases on left & right of main lobby.",
        "balcony_summary": "Mezzanine VIP balconies on Floors 2 & 3 overlooking the central banquet foyer.",
        "floors": {
            1: {
                "floor_name": "Ground Floor (Floor 1)",
                "lift": {"side": "both", "details": "Dual elevators (Left & Right of Grand Reception)"},
                "stairs": {"location": "Twin ceremonial stairways + Rear speaker stage stairs"},
                "balcony": {"location": "Front Banquet Foyer Veranda opening to Central Quad"},
                "key_rooms": ["Main Seminar Hall 1 (400 capacity)", "Speaker Green Room", "Registration Foyer"]
            },
            2: {
                "floor_name": "Floor 2",
                "lift": {"side": "both", "details": "Dual elevator access to Mezzanine and Hall 2"},
                "stairs": {"location": "Twin staircases landing at Mezzanine Lounge"},
                "balcony": {"location": "Mezzanine Foyer Balcony overlooking lower reception"},
                "key_rooms": ["Seminar Hall 2 (250 capacity)", "Press & Media Room", "Speaker Dining Hall"]
            },
            3: {
                "floor_name": "Floor 3",
                "lift": {"side": "both", "details": "Dual elevators servicing top-tier colloquium suites"},
                "stairs": {"location": "Stairwell access to Hall 3 and audio-visual control booths"},
                "balcony": {"location": "Upper Promenade Balcony with full view of Central Amphitheatre"},
                "key_rooms": ["Colloquium Hall 3 (150 capacity)", "Simultaneous Translation Booths", "VIP Suite"]
            }
        },
        "amenities": ["Dual Elevators (Both Sides)", "Acoustic Audio Systems", "VIP Lounges", "Live Webcast Suites"]
    },

    # 9. Sports Precinct: Football Ground, Sports Complex, Cricket Ground
    "FOOTBALL_GROUND": {
        "id": "FOOTBALL_GROUND",
        "name": "Championship Football Ground & 400m Track",
        "short_name": "Football Ground",
        "category": "sports",
        "zone": "South-West Sports",
        "x": 260,
        "y": 590,
        "description": "FIFA-standard synthetic turf football stadium with 400m all-weather rubberized athletic running track.",
        "icon": "flag",
        "has_floors": False,
        "floors_count": 1,
        "amenities": ["Floodlights", "Spectator Grandstand (1,500 seats)", "Locker Rooms", "Referee Box"]
    },
    "SPORTS_COMPLEX": {
        "id": "SPORTS_COMPLEX",
        "name": "Olympic Indoor Sports Complex & Gym",
        "short_name": "Sports Complex",
        "category": "sports",
        "zone": "South Sports",
        "x": 500,
        "y": 620,
        "description": "Multi-sport indoor arena housing maple-wood basketball courts, badminton courts, table tennis, and 3-tier fitness gym.",
        "icon": "activity",
        "has_floors": True,
        "floors_count": 3,
        "lift_side": "right",
        "lift_summary": "Heavy-duty athlete & equipment elevator on the RIGHT side of the sports lobby.",
        "stairs_summary": "Wide open concrete steps leading directly to second floor spectator stands.",
        "balcony_summary": "Spectator viewing gallery balconies overlooking the central basketball arena.",
        "floors": {
            1: {
                "floor_name": "Ground Floor (Floor 1)",
                "lift": {"side": "right", "details": "Right-side elevator with wheelchair and gurney accessibility"},
                "stairs": {"location": "Main entry wide stairs + North emergency fire exits"},
                "balcony": {"location": "Courtside perimeter viewing concourse"},
                "key_rooms": ["Maple Basketball Court", "Badminton Arena (4 courts)", "Olympic Locker Rooms"]
            },
            2: {
                "floor_name": "Floor 2",
                "lift": {"side": "right", "details": "Right elevator landing at Gymnasium and Cardio Suite"},
                "stairs": {"location": "Main stairs leading to Gym + Left fire exit stairwell"},
                "balcony": {"location": "Upper Spectator Gallery Balcony overlooking Basketball Arena"},
                "key_rooms": ["Cardio & Weight Training Gym", "Yoga & Aerobics Studio", "Physiotherapy Clinic"]
            },
            3: {
                "floor_name": "Floor 3",
                "lift": {"side": "right", "details": "Right elevator terminus at Table Tennis and Squash Courts"},
                "stairs": {"location": "Stairwell to Squash gallery and roof solar equipment"},
                "balcony": {"location": "Outdoor Running Track Balcony overlooking Football Ground"},
                "key_rooms": ["Squash Courts (2 courts)", "Table Tennis Hall (8 tables)", "Sports Authority Office"]
            }
        },
        "amenities": ["Elevator (Right)", "Olympic Gym", "Sauna & Steam", "Juice & Nutrition Bar"]
    },
    "CRICKET_GROUND": {
        "id": "CRICKET_GROUND",
        "name": "University Cricket Ground & Pavilion",
        "short_name": "Cricket Ground",
        "category": "sports",
        "zone": "East Sports Precinct",
        "x": 840,
        "y": 420,
        "description": "Lush natural grass cricket stadium with turf pitch, digital scoreboard, sight screens, and player pavilion.",
        "icon": "circle",
        "has_floors": False,
        "floors_count": 1,
        "amenities": ["Turf Pitch", "Player Dugouts", "Digital Scoreboard", "Pavilion Terrace"]
    },

    # 10. Additional Places Specified: Cafeteria, Auditorium, Admin Block, Hostel Village, Amphitheatre
    "CAFETERIA": {
        "id": "CAFETERIA",
        "name": "Central Multi-Cuisine Food Court & Cafeteria",
        "short_name": "Cafeteria",
        "category": "life",
        "zone": "Central Student Plaza",
        "x": 340,
        "y": 490,
        "description": "Buzzing student dining destination serving multi-cuisine meals, bakery delicacies, artisan coffee, and quick bites.",
        "icon": "coffee",
        "has_floors": True,
        "floors_count": 2,
        "lift_side": "left",
        "lift_summary": "Service & passenger elevator on the LEFT side of the dining atrium.",
        "stairs_summary": "Central wide staircase leading to upper mezzanine dining gallery.",
        "balcony_summary": "Open-air patio and terrace balcony on Floor 2 overlooking the Grand Stairs.",
        "floors": {
            1: {
                "floor_name": "Ground Floor (Floor 1)",
                "lift": {"side": "left", "details": "Left-hand service lift for food delivery and wheelchair patrons"},
                "stairs": {"location": "Central wide dining staircase + South fire exit"},
                "balcony": {"location": "Sunlit Ground Patio with 120 outdoor garden seats"},
                "key_rooms": ["Main Food Court Counter", "Live Wok & Pasta Station", "Bakery & Espresso Bar"]
            },
            2: {
                "floor_name": "Floor 2 (Mezzanine)",
                "lift": {"side": "left", "details": "Left lift landing at Mezzanine Seating Lounge"},
                "stairs": {"location": "Central staircase arrival point"},
                "balcony": {"location": "Mezzanine Terrace Balcony with view of Grand Stairs & Fountain"},
                "key_rooms": ["Faculty Dining Club", "Quiet Study & Lunch Lounge", "Student Mess Office"]
            }
        },
        "amenities": ["Elevator (Left)", "Indoor/Outdoor Seating", "Juice Bar", "Digital Kiosks"]
    },
    "AUDITORIUM": {
        "id": "AUDITORIUM",
        "name": "MUJ Grand Auditorium",
        "short_name": "Auditorium",
        "category": "life",
        "zone": "East Cultural Wing",
        "x": 720,
        "y": 510,
        "description": "State-of-the-art 2,000-seat theatrical auditorium for convocations, cultural festivals, and keynote summits.",
        "icon": "volume-2",
        "has_floors": True,
        "floors_count": 3,
        "lift_side": "both",
        "lift_summary": "Twin elevators on BOTH SIDES of the grand marble entrance foyer.",
        "stairs_summary": "Grand curved stairways on left and right leading to Tier 1 and Tier 2 balcony seating.",
        "balcony_summary": "Grand Tier 1 and Tier 2 auditorium balcony tiers with royal red velvet seating.",
        "floors": {
            1: {
                "floor_name": "Ground Floor (Floor 1)",
                "lift": {"side": "both", "details": "Dual elevators (Left & Right grand foyer)"},
                "stairs": {"location": "Twin curved marble stairways + Stage backstage stairs"},
                "balcony": {"location": "Front Grand Portico opening to Fountain Plaza"},
                "key_rooms": ["Orchestra Main Seating (1,200 seats)", "Green Rooms A & B", "Sound & Lighting Console"]
            },
            2: {
                "floor_name": "Floor 2",
                "lift": {"side": "both", "details": "Dual elevator landings at Tier 1 Balcony Foyer"},
                "stairs": {"location": "Twin curved stairways landing at Balcony Foyer"},
                "balcony": {"location": "Tier 1 Center Balcony seating overlooking the main stage"},
                "key_rooms": ["Tier 1 Balcony Seating (500 seats)", "VIP Reception Lounge", "Restrooms"]
            },
            3: {
                "floor_name": "Floor 3",
                "lift": {"side": "both", "details": "Both elevators access Tier 2 Upper Circle"},
                "stairs": {"location": "Stairways continuing to upper tier and spotlight gantry"},
                "balcony": {"location": "Tier 2 Upper Circle Balcony (300 seats) with aerial stage view"},
                "key_rooms": ["Tier 2 Upper Seating", "Audio Engineering Control Room", "Spotlight Rig"]
            }
        },
        "amenities": ["Dual Elevators (Both Sides)", "Dolby Atmos Acoustic Shell", "VIP Green Rooms"]
    },
    "ADMIN_BLOCK": {
        "id": "ADMIN_BLOCK",
        "name": "Administrative Senate Tower",
        "short_name": "Admin Block",
        "category": "administrative",
        "zone": "Central South Core",
        "x": 500,
        "y": 740,
        "description": "University administrative headquarters: Vice-Chancellor's Secretariat, Registrar, Finance, and Admissions.",
        "icon": "briefcase",
        "has_floors": True,
        "floors_count": 3,
        "lift_side": "both",
        "lift_summary": "Dual executive elevators on BOTH SIDES of the reception lobby.",
        "stairs_summary": "Central executive staircase with brass railings; East & West emergency stairwells.",
        "balcony_summary": "Full executive perimeter balcony on Floor 3 with views across the entire campus.",
        "floors": {
            1: {
                "floor_name": "Ground Floor (Floor 1)",
                "lift": {"side": "both", "details": "Dual executive elevators (Left & Right wings)"},
                "stairs": {"location": "Central lobby staircase + East/West emergency stairwells"},
                "balcony": {"location": "South Garden Porch with flag posts and fountains"},
                "key_rooms": ["Student Admissions Office", "Fee Payment & Accounts Desk", "Registrar Counter"]
            },
            2: {
                "floor_name": "Floor 2",
                "lift": {"side": "both", "details": "Dual elevator landings at Academic Affairs foyer"},
                "stairs": {"location": "Central stairs landing with executive marble flooring"},
                "balcony": {"location": "North Balcony framing the Grand Stairs and Central Library"},
                "key_rooms": ["Dean of Academics Office", "Examination Controller Wing", "Human Resources"]
            },
            3: {
                "floor_name": "Floor 3",
                "lift": {"side": "both", "details": "Biometric access dual elevators opening to VC Secretariat"},
                "stairs": {"location": "Central stairs with security access door"},
                "balcony": {"location": "Executive Sky Balcony with 360-degree panorama of campus"},
                "key_rooms": ["Vice-Chancellor Secretariat", "University Senate Boardroom", "Legal Counsel Office"]
            }
        },
        "amenities": ["Dual Elevators (Both Sides)", "ATM Center", "Executive Conference Suites"]
    },
    "HOSTEL_VILLAGE": {
        "id": "HOSTEL_VILLAGE",
        "name": "Student Hostels & Residential Village",
        "short_name": "Hostel Village",
        "category": "residential",
        "zone": "South-West Residential",
        "x": 220,
        "y": 750,
        "description": "Multi-block student residence village with dining halls, laundromat, indoor games lounge, and convenience store.",
        "icon": "home",
        "has_floors": True,
        "floors_count": 3,
        "lift_side": "both",
        "lift_summary": "Passenger elevators on BOTH SIDES of each residential block (Blocks A, B, C).",
        "stairs_summary": "Stairwells on all 4 corners of each residential block for easy access and fire safety.",
        "balcony_summary": "Individual room balconies and common floor balconies overlooking the green lawn.",
        "floors": {
            1: {
                "floor_name": "Ground Floor (Floor 1)",
                "lift": {"side": "both", "details": "Dual elevators (East and West wings)"},
                "stairs": {"location": "Stairwells at East, West, North, and South corridors"},
                "balcony": {"location": "Ground Garden Veranda with common outdoor study tables"},
                "key_rooms": ["Hostel Warden Office", "Night Canteen & Mart", "Common TV & Recreation Lounge"]
            },
            2: {
                "floor_name": "Floor 2",
                "lift": {"side": "both", "details": "Dual elevator landings"},
                "stairs": {"location": "4 corner staircases for rapid egress"},
                "balcony": {"location": "Common Floor Balcony with laundry drying area"},
                "key_rooms": ["Student Rooms 201-240", "Quiet Study Room", "Laundromat (West Wing)"]
            },
            3: {
                "floor_name": "Floor 3",
                "lift": {"side": "both", "details": "Dual elevators terminating at top floor"},
                "stairs": {"location": "4 corner stairwells with roof access security gate"},
                "balcony": {"location": "Stargazing Sky Balcony overlooking the Football Stadium"},
                "key_rooms": ["Student Rooms 301-340", "Indoor Games Room (Table Tennis, Foosball)"]
            }
        },
        "amenities": ["Dual Elevators (Both Sides)", "24/7 Security", "Night Canteen", "Laundromat"]
    },
    "AMPHITHEATRE": {
        "id": "AMPHITHEATRE",
        "name": "Open Air Amphitheatre & Cultural Arena",
        "short_name": "Amphitheatre",
        "category": "life",
        "zone": "South-East Cultural",
        "x": 780,
        "y": 670,
        "description": "Tiered semicircular stone amphitheatre with 1,200 seats for live music concerts, drama, and open-mic evenings.",
        "icon": "sun",
        "has_floors": False,
        "floors_count": 1,
        "amenities": ["Acoustic Shell", "Concentric Stone Seats", "Stage Floodlights", "Green Lawn"]
    }
}

# Campus Pathway & Walkway Edges
CAMPUS_EDGES: List[Dict[str, Any]] = [
    # Main Exit & Entry Connections
    {"u": "MAIN_EXIT", "v": "PARKING", "surface": "paved", "speed_limit": 5.0, "scenic": 0.4},
    {"u": "MAIN_EXIT", "v": "FLAP_GATES", "surface": "paved", "speed_limit": 5.0, "scenic": 0.7},
    {"u": "PARKING", "v": "AB1", "surface": "paved", "speed_limit": 5.0, "scenic": 0.5},
    {"u": "PARKING", "v": "INCUBATION", "surface": "paved", "speed_limit": 5.0, "scenic": 0.6},
    {"u": "FLAP_GATES", "v": "CENTRAL_LIB", "surface": "paved", "speed_limit": 5.0, "scenic": 0.9},
    {"u": "FLAP_GATES", "v": "AB1", "surface": "paved", "speed_limit": 5.0, "scenic": 0.7},
    {"u": "FLAP_GATES", "v": "AB2", "surface": "paved", "speed_limit": 5.0, "scenic": 0.7},

    # Academic Core Connections
    {"u": "AB1", "v": "INCUBATION", "surface": "indoor", "speed_limit": 4.5, "scenic": 0.4},
    {"u": "AB1", "v": "CENTRAL_LIB", "surface": "paved", "speed_limit": 5.0, "scenic": 0.8},
    {"u": "AB1", "v": "AB3", "surface": "paved", "speed_limit": 5.0, "scenic": 0.6},
    {"u": "CENTRAL_LIB", "v": "AB2", "surface": "paved", "speed_limit": 5.0, "scenic": 0.8},
    {"u": "CENTRAL_LIB", "v": "GRAND_STAIRS", "surface": "paved", "speed_limit": 5.0, "scenic": 0.95},
    {"u": "AB2", "v": "NEW_LIB", "surface": "paved", "speed_limit": 5.0, "scenic": 0.8},
    {"u": "AB2", "v": "AB4", "surface": "paved", "speed_limit": 5.0, "scenic": 0.6},
    {"u": "AB2", "v": "CRICKET_GROUND", "surface": "paved", "speed_limit": 5.0, "scenic": 0.85},
    {"u": "NEW_LIB", "v": "CRICKET_GROUND", "surface": "gravel", "speed_limit": 4.5, "scenic": 0.9},

    # Central Core & Grand Stairs Hub
    {"u": "AB3", "v": "GRAND_STAIRS", "surface": "stairs", "speed_limit": 4.0, "scenic": 0.9},
    {"u": "AB4", "v": "GRAND_STAIRS", "surface": "stairs", "speed_limit": 4.0, "scenic": 0.9},
    {"u": "GRAND_STAIRS", "v": "SEMINAR_HALLS", "surface": "paved", "speed_limit": 5.0, "scenic": 0.9},
    {"u": "GRAND_STAIRS", "v": "CAFETERIA", "surface": "paved", "speed_limit": 5.0, "scenic": 0.85},
    {"u": "AB3", "v": "INCUBATION", "surface": "paved", "speed_limit": 4.8, "scenic": 0.5},
    {"u": "AB3", "v": "CAFETERIA", "surface": "indoor", "speed_limit": 4.5, "scenic": 0.6},
    {"u": "AB4", "v": "CRICKET_GROUND", "surface": "paved", "speed_limit": 5.0, "scenic": 0.8},
    {"u": "AB4", "v": "AUDITORIUM", "surface": "indoor", "speed_limit": 4.5, "scenic": 0.7},

    # South Wing & Sports Precinct
    {"u": "CAFETERIA", "v": "FOOTBALL_GROUND", "surface": "paved", "speed_limit": 5.0, "scenic": 0.7},
    {"u": "CAFETERIA", "v": "SEMINAR_HALLS", "surface": "paved", "speed_limit": 5.0, "scenic": 0.8},
    {"u": "SEMINAR_HALLS", "v": "AUDITORIUM", "surface": "paved", "speed_limit": 5.0, "scenic": 0.8},
    {"u": "SEMINAR_HALLS", "v": "SPORTS_COMPLEX", "surface": "paved", "speed_limit": 5.0, "scenic": 0.85},
    {"u": "AUDITORIUM", "v": "AMPHITHEATRE", "surface": "paved", "speed_limit": 5.0, "scenic": 0.9},
    {"u": "FOOTBALL_GROUND", "v": "SPORTS_COMPLEX", "surface": "paved", "speed_limit": 5.0, "scenic": 0.8},
    {"u": "FOOTBALL_GROUND", "v": "HOSTEL_VILLAGE", "surface": "paved", "speed_limit": 5.0, "scenic": 0.7},
    {"u": "SPORTS_COMPLEX", "v": "ADMIN_BLOCK", "surface": "paved", "speed_limit": 5.0, "scenic": 0.8},
    {"u": "SPORTS_COMPLEX", "v": "AMPHITHEATRE", "surface": "gravel", "speed_limit": 4.5, "scenic": 0.95},
    {"u": "HOSTEL_VILLAGE", "v": "ADMIN_BLOCK", "surface": "paved", "speed_limit": 5.0, "scenic": 0.7},
    {"u": "ADMIN_BLOCK", "v": "AMPHITHEATRE", "surface": "paved", "speed_limit": 5.0, "scenic": 0.9}
]

def calculate_euclidean_distance(node1: Dict[str, Any], node2: Dict[str, Any]) -> float:
    """Calculates spatial Euclidean distance in meters."""
    dx = (node1["x"] - node2["x"]) * 1.5
    dy = (node1["y"] - node2["y"]) * 1.5
    return round(math.sqrt(dx * dx + dy * dy), 1)

def calculate_manhattan_distance(node1: Dict[str, Any], node2: Dict[str, Any]) -> float:
    """Calculates Manhattan grid distance in meters."""
    dx = abs(node1["x"] - node2["x"]) * 1.5
    dy = abs(node1["y"] - node2["y"]) * 1.5
    return round(dx + dy, 1)

def build_campus_adjacency():
    """Builds undirected adjacency graph."""
    adj: Dict[str, List[Dict[str, Any]]] = {k: [] for k in CAMPUS_NODES}
    for edge in CAMPUS_EDGES:
        u_id = edge["u"]
        v_id = edge["v"]
        if u_id in CAMPUS_NODES and v_id in CAMPUS_NODES:
            u_node = CAMPUS_NODES[u_id]
            v_node = CAMPUS_NODES[v_id]
            dist = calculate_euclidean_distance(u_node, v_node)
            speed_mps = (edge["speed_limit"] * 1000) / 3600
            base_time = round(dist / max(speed_mps, 0.5), 1)
            
            adj[u_id].append({
                "neighbor": v_id,
                "distance": dist,
                "base_time": base_time,
                "surface": edge["surface"],
                "scenic_rating": edge["scenic"]
            })
            adj[v_id].append({
                "neighbor": u_id,
                "distance": dist,
                "base_time": base_time,
                "surface": edge["surface"],
                "scenic_rating": edge["scenic"]
            })
    return adj

ADJACENCY_GRAPH = build_campus_adjacency()
