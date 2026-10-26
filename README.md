# 🧭 MUJ Campus Route Planner
### Manipal University Jaipur — AI & Soft Computing (AISC) Course Project

An interactive, game-based smart campus navigation and live GPS tracking web application for **Manipal University Jaipur (MUJ)** built from scratch with **Python (Flask)**, **HTML5 Vector Canvas**, and **Tactical Glassmorphism UI**.

---

## 🌟 Key Updates & Specific Campus Architecture

### 1. 🏛️ Exact Campus Landmarks
Includes all requested landmarks plus essential student facilities:
1. **AB1 (Academic Block 1)**: 3 Floors, Lift on **LEFT** side, West Patio & Elevated Sunset Balcony, Physics & Cyber Security Labs.
2. **AB2 (Academic Block 2)**: 3 Floors, Lift on **RIGHT** side, East Promenade Balcony facing Cricket Ground, VLSI & Robotics Arena.
3. **AB3 (Academic Block 3)**: 3 Floors, Dual Lifts on **BOTH SIDES** (Passenger Left, Heavy Service Right), Viewing Balcony framing Grand Stairs.
4. **AB4 (Academic Block 4)**: 3 Floors, Glass Scenic Lift on **LEFT** side, Open Glass Balconies, Soft Computing & AI Lab.
5. **Incubation Center**: 3 Floors, Startup Accelerator, Pitch Auditorium, Makers Balcony.
6. **Central Library**: 3 Floors, Silent Hydraulic Lift on **RIGHT** side, Grand Spiral Mahogany Stairs, Silent Study Balconies.
7. **New Library**: 3 Floors, Dual Glass Lifts on **BOTH SIDES**, 24/7 Digital Cyber Lounge, Wraparound Sky Balcony.
8. **Grand Stairs**: Monumental stone amphitheatre steps connecting upper academic boulevard to sunken fountain plaza.
9. **Flap Gates**: RFID card swipe and optical biometric smart turnstiles.
10. **Main Exit**: Campus Main Security Exit, Portal & Taxi bays.
11. **Parking**: Central & Solar EV Fast Charging stalls.
12. **Seminar Halls**: 3 Floors, Dual Lifts on **BOTH SIDES**, Tiered Multimedia Convention Theatres.
13. **Football Ground**: FIFA-standard synthetic turf stadium with 400m all-weather rubberized running track.
14. **Sports Complex**: 3 Floors, Athlete Lift on **RIGHT** side, Maple Basketball Arena, Olympic Gym, Squash Courts.
15. **Cricket Ground**: Natural grass cricket stadium with center turf pitch, sight screens, and pavilion.
16. **Cafeteria**: 2 Floors, Multi-cuisine food court, bakery espresso bar, and mezzanine terrace dining balcony.
17. **Auditorium**: 3 Floors, Dual Lifts on **BOTH SIDES**, 2,000-seat theatrical auditorium with Tier 1 & 2 balconies.
18. **Admin Block**: 3 Floors, Dual Executive Lifts on **BOTH SIDES**, Vice-Chancellor's Secretariat & Senate Boardroom.
19. **Hostel Village**: 3 Floors, Passenger Lifts on **BOTH SIDES**, student residence quadrangle.
20. **Amphitheatre**: Semicircular open-air cultural arena.

---

### 2. 🧮 Prominent Mathematical Heuristic HUD: $f(n) = g(n) + h(n)$
- Floating HUD card clearly visible in the canvas viewport:
  - **$g(n)$ Past Path Cost**: Exact accumulated distance traversed from the starting origin in meters.
  - **$+$**
  - **$h(n)$ Heuristic Evaluation**: Estimated straight-line Euclidean or Manhattan distance remaining to goal.
  - **$=$**
  - **$f(n)$ Total Evaluation Score**: Total priority function $f(n) = g(n) + h(n)$.
- Live interactive equations:
  - Updates continuously in real time as the avatar navigates.
  - Floating dynamic badge tagged directly above the moving avatar: `f = ...m (g = ...m, h = ...m)`.
  - Step-by-step mathematical breakdown logged for every node along the turn-by-turn timeline.

---

### 3. 🏢 Multi-Floor Navigation & Architectural Blueprint
- **Floor Selection**: Choose starting floor (Floor 1 Ground, Floor 2, Floor 3) and destination floor (Floor 1, Floor 2, Floor 3) directly in the planner.
- **Architectural Details Provided**:
  - **Lift Location**: Tells whether the elevator is on the **LEFT side**, **RIGHT side**, or **BOTH sides** with exact foyer positioning.
  - **Stairs Location**: Identifies central marble stairwells, spiral staircases, and fire exit escapes.
  - **Balconies**: Identifies specific floor balconies, quad viewing galleries, and terrace sky verandas.
  - **Floor Blueprint Modal**: Click **"Floor Blueprints"** in the top navigation to interactively explore Floor 1, Floor 2, and Floor 3 for any building, complete with room directories and lab locations!

---

## 🚀 Running the App

```bash
cd "/Users/yanasareen/Desktop/aisc project"
python3 app.py
```
Open **http://127.0.0.1:5001** in your browser.
