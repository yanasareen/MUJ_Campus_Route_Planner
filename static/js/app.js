/**
 * Apex Smart Campus Route Planner — Interactive Application Controller
 * Handles 6 AI Search Algorithms, GN & HN For Every Location,
 * Responsive Multi-Run Replayability, and Unified Single-Scroll Layout.
 */

document.addEventListener('DOMContentLoaded', () => {
  const state = {
    campusData: null,
    startNode: "AB1",
    goalNode: "AB2",
    startFloor: 1,
    goalFloor: 1,
    selectedAlgo: "ASTAR_EUC",
    speedMultiplier: 2.0,
    weather: "clear",
    soundEnabled: true,
    routeData: null,
    isNavigating: false,
    selectedBlueprintBldg: "AB1",
    selectedBlueprintFloor: 1
  };

  const mapEngine = new CampusMapEngine('campusCanvas');

  // Web Audio Synthesizer
  class TacticalAudioSynth {
    constructor() {
      this.ctx = null;
    }
    init() {
      if (!this.ctx) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        this.ctx = new AudioContext();
      }
      if (this.ctx && this.ctx.state === 'suspended') {
        this.ctx.resume();
      }
    }
    playRadarPing() {
      if (!state.soundEnabled) return;
      try {
        this.init();
        if (!this.ctx) return;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(880, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(440, this.ctx.currentTime + 0.18);
        gain.gain.setValueAtTime(0.08, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.18);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.18);
      } catch (e) {}
    }
    playWaypointReached() {
      if (!state.soundEnabled) return;
      try {
        this.init();
        if (!this.ctx) return;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(523.25, this.ctx.currentTime);
        osc.frequency.setValueAtTime(659.25, this.ctx.currentTime + 0.08);
        gain.gain.setValueAtTime(0.06, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.25);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.25);
      } catch (e) {}
    }
    playDestinationFanfare() {
      if (!state.soundEnabled) return;
      try {
        this.init();
        if (!this.ctx) return;
        const notes = [523.25, 659.25, 783.99, 1046.50];
        notes.forEach((freq, idx) => {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, this.ctx.currentTime + idx * 0.1);
          gain.gain.setValueAtTime(0.1, this.ctx.currentTime + idx * 0.1);
          gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + idx * 0.1 + 0.35);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start(this.ctx.currentTime + idx * 0.1);
          osc.stop(this.ctx.currentTime + idx * 0.1 + 0.35);
        });
      } catch (e) {}
    }
  }
  const soundSynth = new TacticalAudioSynth();

  // Weather Particles Overlay
  const weatherCanvas = document.getElementById('weatherFxCanvas');
  const wCtx = weatherCanvas.getContext('2d');
  let weatherParticles = [];

  function initWeatherCanvas() {
    weatherCanvas.width = weatherCanvas.parentElement.clientWidth;
    weatherCanvas.height = weatherCanvas.parentElement.clientHeight;
    weatherParticles = [];
    const count = state.weather === 'rain' ? 140 : (state.weather === 'night' ? 60 : 0);
    for (let i = 0; i < count; i++) {
      weatherParticles.push({
        x: Math.random() * weatherCanvas.width,
        y: Math.random() * weatherCanvas.height,
        len: Math.random() * 18 + 10,
        speed: Math.random() * 8 + 12,
        opacity: Math.random() * 0.4 + 0.2,
        twinkle: Math.random() * Math.PI
      });
    }
  }

  function renderWeatherParticles() {
    wCtx.clearRect(0, 0, weatherCanvas.width, weatherCanvas.height);
    if (state.weather === 'rain') {
      wCtx.strokeStyle = 'rgba(56, 189, 248, 0.35)';
      wCtx.lineWidth = 1.2;
      for (const p of weatherParticles) {
        wCtx.beginPath();
        wCtx.moveTo(p.x, p.y);
        wCtx.lineTo(p.x - 3, p.y + p.len);
        wCtx.stroke();
        p.y += p.speed;
        p.x -= 1.5;
        if (p.y > weatherCanvas.height) {
          p.y = -20;
          p.x = Math.random() * weatherCanvas.width;
        }
      }
    } else if (state.weather === 'night') {
      for (const p of weatherParticles) {
        p.twinkle += 0.05;
        const alpha = (Math.sin(p.twinkle) + 1) * 0.35 + 0.1;
        wCtx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
        wCtx.beginPath();
        wCtx.arc(p.x, p.y, 1.2, 0, Math.PI * 2);
        wCtx.fill();
      }
    }
    requestAnimationFrame(renderWeatherParticles);
  }
  window.addEventListener('resize', initWeatherCanvas);
  renderWeatherParticles();

  // Load Knowledge Graph
  async function loadCampusData() {
    try {
      const response = await fetch('/api/campus');
      const data = await response.json();
      if (data.success) {
        state.campusData = data;
        mapEngine.setCampusData(data.nodes, data.edges);
        populateLocationDropdowns(data.nodes);
        renderDirectoryCards(data.nodes);
        updateArchitecturalTransitBox();
        fetchAndDisplayRoute();
      }
    } catch (err) {
      console.error('Failed to load campus graph data:', err);
    }
  }

  function populateLocationDropdowns(nodes) {
    const selStart = document.getElementById('selectStart');
    const selGoal = document.getElementById('selectGoal');
    selStart.innerHTML = '';
    selGoal.innerHTML = '';

    const categories = {
      academic: "Academic Blocks & Labs",
      sports: "Sports Complex & Grounds",
      life: "Student Life & Amenities",
      transit: "Gates & Parking"
    };

    const optGroupsStart = {};
    const optGroupsGoal = {};

    for (const cat in categories) {
      optGroupsStart[cat] = document.createElement('optgroup');
      optGroupsStart[cat].label = categories[cat];
      optGroupsGoal[cat] = document.createElement('optgroup');
      optGroupsGoal[cat].label = categories[cat];
    }

    for (const id in nodes) {
      const node = nodes[id];
      const cat = node.category in categories ? node.category : 'academic';

      const opt1 = document.createElement('option');
      opt1.value = node.id;
      opt1.textContent = `${node.short_name} — ${node.name}`;
      if (node.id === state.startNode) opt1.selected = true;
      optGroupsStart[cat].appendChild(opt1);

      const opt2 = document.createElement('option');
      opt2.value = node.id;
      opt2.textContent = `${node.short_name} — ${node.name}`;
      if (node.id === state.goalNode) opt2.selected = true;
      optGroupsGoal[cat].appendChild(opt2);
    }

    for (const cat in categories) {
      selStart.appendChild(optGroupsStart[cat]);
      selGoal.appendChild(optGroupsGoal[cat]);
    }

    updateFloorDropdownVisibility();
  }

  function updateFloorDropdownVisibility() {
    if (!state.campusData) return;
    const startNode = state.campusData.nodes[state.startNode];
    const goalNode = state.campusData.nodes[state.goalNode];

    const startFloorWrap = document.getElementById('startFloorWrap');
    const goalFloorWrap = document.getElementById('goalFloorWrap');

    if (startNode && startNode.has_floors) {
      startFloorWrap.style.display = 'flex';
      const el = document.getElementById('selectStartFloor');
      if (el) el.value = String(state.startFloor || 1);
    } else {
      startFloorWrap.style.display = 'none';
      state.startFloor = 1;
      const el = document.getElementById('selectStartFloor');
      if (el) el.value = '1';
    }

    if (goalNode && goalNode.has_floors) {
      goalFloorWrap.style.display = 'flex';
      const el = document.getElementById('selectGoalFloor');
      if (el) el.value = String(state.goalFloor || 1);
    } else {
      goalFloorWrap.style.display = 'none';
      state.goalFloor = 1;
      const el = document.getElementById('selectGoalFloor');
      if (el) el.value = '1';
    }

    updateArchitecturalTransitBox();
  }

  function updateArchitecturalTransitBox() {
    if (!state.campusData) return;
    const startNode = state.campusData.nodes[state.startNode];
    if (!startNode) return;

    const liftSideEl = document.getElementById('archLiftSide');
    const stairsLocEl = document.getElementById('archStairsLocation');
    const balconyLocEl = document.getElementById('archBalconyLocation');

    if (startNode.has_floors) {
      liftSideEl.textContent = `${(startNode.lift_side || 'both').toUpperCase()} WING`;
      stairsLocEl.textContent = startNode.stairs_summary || "Central & Fire Stairs";
      balconyLocEl.textContent = startNode.balcony_summary || "Floor Balcony";
      document.getElementById('architecturalTransitBox').style.display = 'flex';
    } else {
      liftSideEl.textContent = "Ground Level";
      stairsLocEl.textContent = "Ground Walkways";
      balconyLocEl.textContent = "Open Courtyard";
      document.getElementById('architecturalTransitBox').style.display = 'flex';
    }
  }

  // --------------------------------------------------------------------------
  // ROUTE CALCULATION & HEURISTIC BREAKDOWN (MULTI-RUN CAPABLE)
  // --------------------------------------------------------------------------
  async function fetchAndDisplayRoute(animateWavefront = true) {
    if (!state.startNode || !state.goalNode) return;

    // Safely reset navigation state
    mapEngine.resetAvatar();
    state.isNavigating = false;
    updateNavButtonsReadyState();

    mapEngine.startNodeId = state.startNode;
    mapEngine.goalNodeId = state.goalNode;

    const payload = {
      start: state.startNode,
      goal: state.goalNode,
      start_floor: state.startFloor,
      goal_floor: state.goalFloor,
      algorithm: state.selectedAlgo
    };

    try {
      const response = await fetch('/api/route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();

      if (data.success) {
        state.routeData = data;
        soundSynth.playRadarPing();

        const badgeMap = {
          "ASTAR_EUC": "A* (EUCLIDEAN)",
          "ASTAR_MAN": "A* (MANHATTAN)",
          "UCS": "DIJKSTRA (UNIFORM-COST)",
          "BFS": "BFS (HOP OPTIMAL)",
          "DFS": "DFS (WANDERING)",
          "GBFS": "GREEDY BEST-FIRST"
        };
        document.getElementById('activeAlgoBadge').textContent = badgeMap[state.selectedAlgo] || state.selectedAlgo;

        const allH = (data.metrics && data.metrics.all_nodes_heuristics) ? data.metrics.all_nodes_heuristics : {};

        if (animateWavefront && data.visited_order && data.visited_order.length > 0) {
          mapEngine.setRoute(data.path, data.visited_order, allH);
          mapEngine.animateFrontierExploration();
        } else {
          mapEngine.setRoute(data.path, data.visited_order, allH);
        }

        updateRouteTelemetryUI(data);
        updateHeuristicHUD(data);
        renderEveryLocationHeuristicTable(data);
      }
    } catch (err) {
      console.error('Error fetching route:', err);
    }
  }

  function updateNavButtonsReadyState() {
    const btnStart = document.getElementById('btnStartNavigation');
    if (btnStart) {
      btnStart.innerHTML = `<i data-feather="play"></i><span id="btnNavText">START LIVE GPS TRACKING</span>`;
    }
    const btnPause = document.getElementById('btnPauseNavigation');
    if (btnPause) {
      btnPause.style.display = 'none';
      btnPause.innerHTML = `<i data-feather="pause"></i>`;
    }
    const statusText = document.getElementById('missionStatusText');
    if (statusText) {
      statusText.textContent = 'READY TO NAVIGATE';
    }
    feather.replace();
  }

  // PROMINENT f(n) = g(n) + h(n) TOP HUD CARD
  function updateHeuristicHUD(data) {
    if (!data.metrics) return;
    const trace = data.metrics.heuristic_trace || [];
    if (trace.length === 0) return;

    const startStep = trace[0];
    const initialH = trace[0].h;

    document.getElementById('hudGVal').innerHTML = `0.0 <span class="unit">m</span>`;
    document.getElementById('hudHVal').innerHTML = `${initialH} <span class="unit">m</span>`;
    document.getElementById('hudFVal').innerHTML = `${initialH} <span class="unit">m</span>`;

    const algoTitleMap = {
      "ASTAR_EUC": "A* Search [Euclidean: f = g + h]",
      "ASTAR_MAN": "A* Search [Manhattan: f = g + h]",
      "UCS": "Dijkstra [Uniform-Cost: f = g, h = 0]",
      "GBFS": "Greedy Best-First [f = h, g = 0]",
      "BFS": "BFS [f = depth(n)]",
      "DFS": "DFS [LIFO Stack]"
    };
    document.getElementById('hudFormulaTitle').textContent = algoTitleMap[state.selectedAlgo] || "f(n) = g(n) + h(n)";

    document.getElementById('hudLiveEquation').textContent = 
      `At Start ${startStep.short_name}: g = 0m, h = ${initialH}m => f = ${initialH}m`;

    mapEngine.avatar.currentG = 0.0;
    mapEngine.avatar.currentH = initialH;
    mapEngine.avatar.currentF = initialH;
  }

  // RENDER GN AND HN VALUES FOR EVERY LOCATION TABLE
  function renderEveryLocationHeuristicTable(data) {
    const tbody = document.getElementById('locationsHeuristicTableBody');
    tbody.innerHTML = '';
    if (!data.metrics) return;

    const trace = data.metrics.heuristic_trace || [];
    trace.forEach((step) => {
      const node = state.campusData ? state.campusData.nodes[step.node_id] : null;
      const liftInfo = node && node.has_floors ? `Lift: ${(node.lift_side || 'both').toUpperCase()}` : "Ground Walkway";

      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td class="node-cell">
          <strong>${step.short_name}</strong>
          <div style="font-size: 9px; color: var(--text-muted);">${node ? node.name : ''}</div>
        </td>
        <td>Floor ${step.floor}</td>
        <td class="g-cell">${step.g} m</td>
        <td class="h-cell">${step.h} m</td>
        <td class="f-cell">${step.f} m</td>
        <td><span class="amenity-chip" style="font-size: 8px;">${liftInfo}</span></td>
      `;
      tbody.appendChild(tr);
    });
  }

  function updateRouteTelemetryUI(data) {
    const metrics = data.metrics || {};
    
    document.getElementById('metricRemainingDist').innerHTML = `${metrics.total_distance_m || 0} <span class="unit">m</span>`;
    document.getElementById('missionEtaBadge').textContent = `ETA: ${metrics.formatted_time || '0 min'}`;
    document.getElementById('metricNodesExpanded').innerHTML = `${data.nodes_expanded || 0} <span class="unit">nodes</span>`;
    document.getElementById('metricExecTime').innerHTML = `${data.execution_time_ms || 0} <span class="unit">ms</span>`;
    document.getElementById('metricSpeed').innerHTML = `4.8 <span class="unit">km/h</span>`;

    const pBar = document.getElementById('navProgressBar');
    if (pBar) pBar.style.width = '0%';
    const pTxt = document.getElementById('navProgressPercent');
    if (pTxt) pTxt.textContent = '0%';

    // Timeline Steps List
    const timelineList = document.getElementById('timelineStepsList');
    timelineList.innerHTML = '';
    
    if (metrics.departure_floor_details && metrics.departure_floor_details.requires_vertical_transit) {
      const depItem = document.createElement('div');
      depItem.className = 'timeline-item active';
      depItem.innerHTML = `
        <div class="timeline-dot" style="background: #38bdf8;"></div>
        <div class="timeline-content">
          <div class="timeline-name" style="color: #38bdf8;">DEPARTURE VERTICAL TRANSIT</div>
          <div class="timeline-sub">${metrics.departure_floor_details.instruction}</div>
        </div>
      `;
      timelineList.appendChild(depItem);
    }

    const segments = metrics.segments || [];
    segments.forEach((seg, idx) => {
      const item = document.createElement('div');
      item.className = `timeline-item ${idx === 0 ? 'active' : ''}`;
      item.id = `timelineStep_${idx}`;
      item.innerHTML = `
        <div class="timeline-dot"></div>
        <div class="timeline-content">
          <div class="timeline-name">${seg.to_name}</div>
          <div class="timeline-sub">${seg.distance_m}m • ${seg.surface} walkway • ~${Math.round(seg.estimated_time_s)}s</div>
          <div class="timeline-heuristic-tag">g = ${seg.g_at_step}m | h = ${seg.h_at_step}m => f = ${seg.f_at_step}m</div>
        </div>
      `;
      timelineList.appendChild(item);
    });

    if (metrics.destination_floor_details && metrics.destination_floor_details.requires_vertical_transit) {
      const arrItem = document.createElement('div');
      arrItem.className = 'timeline-item';
      arrItem.innerHTML = `
        <div class="timeline-dot" style="background: #f43f5e;"></div>
        <div class="timeline-content">
          <div class="timeline-name" style="color: #f43f5e;">ARRIVAL VERTICAL TRANSIT</div>
          <div class="timeline-sub">${metrics.destination_floor_details.instruction}</div>
        </div>
      `;
      timelineList.appendChild(arrItem);
    }

    if (segments.length > 0) {
      document.getElementById('nextStepTitle').textContent = `Head toward ${segments[0].to_name}`;
      document.getElementById('nextStepSub').textContent = `Follow ${segments[0].surface} path • ${segments[0].distance_m}m`;
    } else {
      const destNode = state.campusData && state.campusData.nodes[state.goalNode];
      document.getElementById('nextStepTitle').textContent = `At ${destNode ? destNode.short_name : 'Destination'}`;
      document.getElementById('nextStepSub').textContent = metrics.destination_floor_details && metrics.destination_floor_details.requires_vertical_transit
        ? metrics.destination_floor_details.instruction
        : 'Already at chosen destination location and floor';
    }
  }

  // --------------------------------------------------------------------------
  // LIVE GPS TELEMETRY & DYNAMIC f(n) HUD UPDATE
  // --------------------------------------------------------------------------
  window.updateTelemetryHUD = function(avatar) {
    let deg = Math.round((avatar.angle * 180 / Math.PI + 360) % 360);
    const cardinals = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
    const cardIndex = Math.round(deg / 22.5) % 16;
    const cardStr = cardinals[cardIndex];
    document.getElementById('headingDegrees').textContent = `${String(deg).padStart(3, '0')}° ${cardStr}`;
    
    const arrow = document.querySelector('.compass-arrow');
    if (arrow) arrow.style.transform = `rotate(${deg}deg)`;

    const latBase = 42.3601;
    const lonBase = -71.0942;
    const curLat = (latBase + (avatar.y - 450) * -0.00008).toFixed(4);
    const curLon = (lonBase + (avatar.x - 500) * 0.00010).toFixed(4);
    document.getElementById('hudCoordsLat').textContent = `LAT ${curLat}° N`;
    document.getElementById('hudCoordsLon').textContent = `LON ${Math.abs(curLon)}° W`;

    const pct = Math.round(avatar.totalProgress * 100);
    document.getElementById('navProgressBar').style.width = `${pct}%`;
    document.getElementById('navProgressPercent').textContent = `${pct}%`;

    // Dynamic Live g(n), h(n), f(n) calculation
    if (state.routeData && state.routeData.metrics) {
      const totalDist = state.routeData.metrics.total_distance_m;
      const curG = Math.round(totalDist * avatar.totalProgress * 10) / 10;
      const curH = Math.max(Math.round(totalDist * (1.0 - avatar.totalProgress) * 10) / 10, 0);
      const curF = Math.round((curG + curH) * 10) / 10;

      document.getElementById('hudGVal').innerHTML = `${curG} <span class="unit">m</span>`;
      document.getElementById('hudHVal').innerHTML = `${curH} <span class="unit">m</span>`;
      document.getElementById('hudFVal').innerHTML = `${curF} <span class="unit">m</span>`;

      document.getElementById('hudLiveEquation').textContent = 
        `Navigating: g = ${curG}m + h = ${curH}m => f = ${curF}m`;

      document.getElementById('metricRemainingDist').innerHTML = `${curH} <span class="unit">m</span>`;

      avatar.currentG = curG;
      avatar.currentH = curH;
      avatar.currentF = curF;
    }

    document.querySelectorAll('.timeline-item').forEach((el, idx) => {
      if (idx === avatar.segmentIndex) el.classList.add('active');
      else el.classList.remove('active');
    });

    if (state.routeData && state.routeData.metrics && state.routeData.metrics.segments) {
      const segs = state.routeData.metrics.segments;
      if (avatar.segmentIndex < segs.length) {
        const curSeg = segs[avatar.segmentIndex];
        document.getElementById('nextStepTitle').textContent = `En Route to ${curSeg.to_name}`;
        document.getElementById('nextStepSub').textContent = `Continue along ${curSeg.surface} path • ~${Math.round(curSeg.distance_m * (1 - avatar.segmentProgress))}m remaining`;
      }
    }
  };

  window.onWaypointReached = function(nodeId) {
    soundSynth.playWaypointReached();
    const node = state.campusData ? state.campusData.nodes[nodeId] : null;
    if (node) {
      document.getElementById('missionStatusText').textContent = `WAYPOINT: ${node.short_name.toUpperCase()}`;
    }
  };

  window.onNavigationArrival = function() {
    soundSynth.playDestinationFanfare();
    document.getElementById('missionStatusText').textContent = 'DESTINATION REACHED — ARRIVAL CONFIRMED';
    const btnStart = document.getElementById('btnStartNavigation');
    if (btnStart) {
      btnStart.innerHTML = `<i data-feather="rotate-ccw"></i><span id="btnNavText">REPLAY NAVIGATION</span>`;
      feather.replace();
    }
    const btnPause = document.getElementById('btnPauseNavigation');
    if (btnPause) btnPause.style.display = 'none';
    state.isNavigating = false;
  };

  // --------------------------------------------------------------------------
  // TOOLTIP WITH GN & HN
  // --------------------------------------------------------------------------
  const tooltip = document.getElementById('landmarkTooltip');
  let currentTooltipNode = null;

  window.onCampusNodeHovered = function(node, screenX, screenY, hData) {
    if (!node) {
      tooltip.classList.remove('show');
      currentTooltipNode = null;
      return;
    }
    currentTooltipNode = node;
    document.getElementById('ttCategory').textContent = node.category.toUpperCase();
    document.getElementById('ttTitle').textContent = `${node.short_name} (${node.name})`;
    document.getElementById('ttDesc').textContent = node.description;
    
    if (hData) {
      document.getElementById('ttGVal').textContent = `${hData.g} m`;
      document.getElementById('ttHVal').textContent = `${hData.h} m`;
      document.getElementById('ttFVal').textContent = `${hData.f} m`;
      document.getElementById('ttHeuristicsBox').style.display = 'flex';
    } else {
      document.getElementById('ttHeuristicsBox').style.display = 'none';
    }

    const archDiv = document.getElementById('ttArchSpecs');
    if (node.has_floors) {
      archDiv.innerHTML = `
        <div>🏢 <strong>3 Floors</strong> with architectural stairwells</div>
        <div>🛗 Lift Side: <strong>${(node.lift_side || 'both').toUpperCase()}</strong> (${node.lift_summary || 'Passenger Lift'})</div>
        <div>🌅 Balcony: <strong>${node.balcony_summary || 'Panoramic Terrace'}</strong></div>
      `;
      archDiv.style.display = 'flex';
    } else {
      archDiv.style.display = 'none';
    }

    const amenDiv = document.getElementById('ttAmenities');
    amenDiv.innerHTML = (node.amenities || []).map(a => `<span class="amenity-chip">${a}</span>`).join('');

    tooltip.style.left = `${screenX}px`;
    tooltip.style.top = `${screenY}px`;
    tooltip.classList.add('show');
  };

  window.onCampusNodeClicked = function(node) {
    if (!node) return;
    if (state.startNode !== node.id) {
      state.goalNode = node.id;
      document.getElementById('selectGoal').value = node.id;
    } else {
      state.startNode = node.id;
      document.getElementById('selectStart').value = node.id;
    }
    updateFloorDropdownVisibility();
    fetchAndDisplayRoute();
  };

  document.getElementById('btnSetAsStart').addEventListener('click', () => {
    if (currentTooltipNode) {
      state.startNode = currentTooltipNode.id;
      document.getElementById('selectStart').value = currentTooltipNode.id;
      tooltip.classList.remove('show');
      updateFloorDropdownVisibility();
      fetchAndDisplayRoute();
    }
  });

  document.getElementById('btnSetAsGoal').addEventListener('click', () => {
    if (currentTooltipNode) {
      state.goalNode = currentTooltipNode.id;
      document.getElementById('selectGoal').value = currentTooltipNode.id;
      tooltip.classList.remove('show');
      updateFloorDropdownVisibility();
      fetchAndDisplayRoute();
    }
  });

  // --------------------------------------------------------------------------
  // MULTI-FLOOR ARCHITECTURAL BLUEPRINT MODAL
  // --------------------------------------------------------------------------
  const floorModal = document.getElementById('floorBlueprintModal');
  const btnOpenFloorBlueprint = document.getElementById('btnOpenFloorBlueprint');
  const btnCloseFloorBlueprint = document.getElementById('btnCloseFloorBlueprint');

  btnOpenFloorBlueprint.addEventListener('click', () => {
    floorModal.classList.add('show');
    renderBlueprintDetails();
  });

  btnCloseFloorBlueprint.addEventListener('click', () => {
    floorModal.classList.remove('show');
  });

  document.querySelectorAll('.bldg-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.bldg-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.selectedBlueprintBldg = btn.dataset.bldg;
      renderBlueprintDetails();
    });
  });

  document.querySelectorAll('.floor-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.floor-tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.selectedBlueprintFloor = parseInt(btn.dataset.floor);
      renderBlueprintDetails();
    });
  });

  function renderBlueprintDetails() {
    if (!state.campusData) return;
    const bldg = state.campusData.nodes[state.selectedBlueprintBldg];
    if (!bldg) return;

    const floorNum = state.selectedBlueprintFloor;
    const floorData = (bldg.floors && bldg.floors[floorNum]) ? bldg.floors[floorNum] : null;

    document.getElementById('bpBuildingTitle').textContent = 
      `${bldg.name} — Floor ${floorNum} (${floorData ? floorData.floor_name : 'Standard Floor'})`;

    const liftSide = (bldg.lift_side || 'both').toUpperCase();
    document.getElementById('bpLiftTag').textContent = `ELEVATOR: ${liftSide} SIDE`;

    if (floorData) {
      document.getElementById('bpLiftDesc').textContent = 
        `${floorData.lift.details} (Side: ${liftSide})`;
      document.getElementById('bpStairsDesc').textContent = 
        floorData.stairs.location;
      document.getElementById('bpBalconyDesc').textContent = 
        floorData.balcony.location;

      const roomsList = document.getElementById('bpRoomsList');
      roomsList.innerHTML = (floorData.key_rooms || []).map(r => `<span class="room-chip">${r}</span>`).join('');
    }
  }

  // --------------------------------------------------------------------------
  // DIRECTORY ATLAS CARDS
  // --------------------------------------------------------------------------
  function renderDirectoryCards(nodes, filterCat = 'all', searchQuery = '') {
    const grid = document.getElementById('directoryGrid');
    grid.innerHTML = '';
    const query = searchQuery.toLowerCase().trim();

    for (const id in nodes) {
      const node = nodes[id];
      if (filterCat !== 'all' && node.category !== filterCat) continue;
      if (query && !node.name.toLowerCase().includes(query) && !node.short_name.toLowerCase().includes(query) && !node.description.toLowerCase().includes(query)) {
        continue;
      }

      const card = document.createElement('div');
      card.className = 'dir-card';
      card.innerHTML = `
        <div class="dir-card-header">
          <span class="tooltip-badge">${node.category.toUpperCase()}</span>
          <span style="font-size: 10px; color: var(--text-muted); font-family: var(--font-mono);">${node.zone}</span>
        </div>
        <div class="dir-card-title">${node.short_name} — ${node.name}</div>
        <div class="dir-card-desc">${node.description}</div>
        ${node.has_floors ? `
          <div style="font-size: 10px; color: var(--accent-cyan-bright); font-weight: 600;">
            🛗 Lift: ${(node.lift_side || 'both').toUpperCase()} | 3 Floors | Balconies
          </div>
        ` : ''}
        <div class="tooltip-amenities">
          ${(node.amenities || []).map(a => `<span class="amenity-chip">${a}</span>`).join('')}
        </div>
        <div class="dir-card-footer">
          <button class="tooltip-btn" data-action="start" data-id="${node.id}">Set Origin</button>
          <button class="tooltip-btn highlight" data-action="goal" data-id="${node.id}">Navigate Here</button>
        </div>
      `;

      card.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          const targetId = btn.dataset.id;
          if (btn.dataset.action === 'start') {
            state.startNode = targetId;
            document.getElementById('selectStart').value = targetId;
          } else {
            state.goalNode = targetId;
            document.getElementById('selectGoal').value = targetId;
          }
          document.getElementById('directoryModal').classList.remove('show');
          updateFloorDropdownVisibility();
          fetchAndDisplayRoute();
        });
      });

      grid.appendChild(card);
    }
  }

  // --------------------------------------------------------------------------
  // CONTROLS & LISTENERS (SAFE REPEATABLE EXECUTION)
  // --------------------------------------------------------------------------
  document.getElementById('selectStart').addEventListener('change', (e) => {
    state.startNode = e.target.value;
    updateFloorDropdownVisibility();
    fetchAndDisplayRoute();
  });

  document.getElementById('selectGoal').addEventListener('change', (e) => {
    state.goalNode = e.target.value;
    updateFloorDropdownVisibility();
    fetchAndDisplayRoute();
  });

  document.getElementById('selectStartFloor').addEventListener('change', (e) => {
    state.startFloor = parseInt(e.target.value);
    fetchAndDisplayRoute(false);
  });

  document.getElementById('selectGoalFloor').addEventListener('change', (e) => {
    state.goalFloor = parseInt(e.target.value);
    fetchAndDisplayRoute(false);
  });

  document.getElementById('btnSwapLocations').addEventListener('click', () => {
    const tmpNode = state.startNode;
    state.startNode = state.goalNode;
    state.goalNode = tmpNode;

    const tmpFloor = state.startFloor;
    state.startFloor = state.goalFloor;
    state.goalFloor = tmpFloor;

    document.getElementById('selectStart').value = state.startNode;
    document.getElementById('selectGoal').value = state.goalNode;
    document.getElementById('selectStartFloor').value = state.startFloor;
    document.getElementById('selectGoalFloor').value = state.goalFloor;

    updateFloorDropdownVisibility();
    fetchAndDisplayRoute();
  });

  // Algorithm Pills Switcher
  const algoComplexityMap = {
    "ASTAR_EUC": "f(n) = g(n) + h(n)",
    "ASTAR_MAN": "f(n) = g(n) + |Δx|+|Δy|",
    "UCS": "f(n) = g(n) [Dijkstra]",
    "BFS": "f(n) = depth(n)",
    "GBFS": "f(n) = h(n)",
    "DFS": "LIFO Stack Search"
  };

  document.querySelectorAll('.algo-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.algo-pill').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      state.selectedAlgo = btn.dataset.algo;
      document.getElementById('algoComplexityTag').textContent = algoComplexityMap[state.selectedAlgo] || "AI Search";
      fetchAndDisplayRoute(true);
    });
  });

  // Speed Multiplier Pills (1x, 2x, 4x)
  document.querySelectorAll('.speed-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.speed-pill').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      state.speedMultiplier = parseFloat(btn.dataset.speed);
      mapEngine.speedMultiplier = state.speedMultiplier;
    });
  });

  // START / RESTART LIVE GPS TRACKING BUTTON
  const btnStartNav = document.getElementById('btnStartNavigation');
  const btnPauseNav = document.getElementById('btnPauseNavigation');
  const btnResetNav = document.getElementById('btnResetNavigation');

  btnStartNav.addEventListener('click', () => {
    state.isNavigating = true;
    mapEngine.startNavigation(state.speedMultiplier);
    btnStartNav.innerHTML = `<i data-feather="navigation-2"></i><span id="btnNavText">LIVE NAVIGATING...</span>`;
    btnPauseNav.style.display = 'flex';
    document.getElementById('missionStatusText').textContent = 'LIVE TRACKING IN PROGRESS';
    feather.replace();
  });

  btnPauseNav.addEventListener('click', () => {
    const isPaused = mapEngine.pauseNavigation();
    btnPauseNav.innerHTML = isPaused ? `<i data-feather="play"></i>` : `<i data-feather="pause"></i>`;
    document.getElementById('missionStatusText').textContent = isPaused ? 'NAVIGATION PAUSED' : 'LIVE TRACKING IN PROGRESS';
    feather.replace();
  });

  btnResetNav.addEventListener('click', () => {
    mapEngine.resetAvatar();
    state.isNavigating = false;
    btnStartNav.innerHTML = `<i data-feather="play"></i><span id="btnNavText">START LIVE GPS TRACKING</span>`;
    btnPauseNav.style.display = 'none';
    document.getElementById('missionStatusText').textContent = 'READY TO NAVIGATE';
    feather.replace();

    if (state.routeData) {
      updateRouteTelemetryUI(state.routeData);
      updateHeuristicHUD(state.routeData);
    }
  });

  document.getElementById('btnZoomIn').addEventListener('click', () => {
    mapEngine.scale = Math.min(mapEngine.scale * 1.25, mapEngine.maxScale);
  });
  document.getElementById('btnZoomOut').addEventListener('click', () => {
    mapEngine.scale = Math.max(mapEngine.scale * 0.8, mapEngine.minScale);
  });
  document.getElementById('btnResetView').addEventListener('click', () => {
    mapEngine.centerView();
  });
  document.getElementById('btnFollowAvatar').addEventListener('click', function() {
    mapEngine.followAvatar = !mapEngine.followAvatar;
    this.classList.toggle('active', mapEngine.followAvatar);
  });

  const weatherModes = ['clear', 'rain', 'heatwave', 'night'];
  const weatherIcons = { clear: 'sun', rain: 'cloud-rain', heatwave: 'zap', night: 'moon' };
  document.getElementById('btnWeatherToggle').addEventListener('click', () => {
    const nextIdx = (weatherModes.indexOf(state.weather) + 1) % weatherModes.length;
    state.weather = weatherModes[nextIdx];
    document.body.className = `theme-dark weather-${state.weather}`;
    mapEngine.weather = state.weather;
    document.getElementById('weatherTooltip').textContent = `Weather: ${state.weather.toUpperCase()}`;
    const iconElem = document.getElementById('weatherIcon');
    iconElem.setAttribute('data-feather', weatherIcons[state.weather]);
    feather.replace();
    initWeatherCanvas();
  });

  document.getElementById('btnAudioToggle').addEventListener('click', function() {
    state.soundEnabled = !state.soundEnabled;
    this.classList.toggle('active', state.soundEnabled);
    this.querySelector('.btn-tooltip').textContent = `Sound FX: ${state.soundEnabled ? 'ON' : 'OFF'}`;
  });

  // Benchmark Modal (6 Algorithms)
  const compareModal = document.getElementById('compareModal');
  document.getElementById('btnOpenCompare').addEventListener('click', async () => {
    compareModal.classList.add('show');
    const tbody = document.getElementById('benchmarkTableBody');
    tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; padding: 20px;">Computing real-time benchmarks across all 6 AI algorithms...</td></tr>`;

    try {
      const res = await fetch('/api/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start: state.startNode,
          goal: state.goalNode,
          start_floor: state.startFloor,
          goal_floor: state.goalFloor
        })
      });
      const data = await res.json();
      if (data.success && data.summary) {
        tbody.innerHTML = '';
        data.summary.forEach(row => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td class="algo-name-cell">${row.name}</td>
            <td><span class="amenity-chip">${row.type}</span></td>
            <td style="font-family: var(--font-mono); color: var(--accent-cyan);">${row.formula}</td>
            <td>${row.distance_m} m</td>
            <td>${row.time_formatted}</td>
            <td class="${row.id === 'ASTAR_EUC' ? 'highlight-cell' : ''}">${row.nodes_expanded}</td>
            <td>${row.path_hops} hops</td>
            <td>${row.exec_ms} ms</td>
            <td><span class="status-pill">${row.optimal}</span></td>
          `;
          tbody.appendChild(tr);
        });
      }
    } catch (e) {
      console.error('Benchmark fetch error:', e);
    }
  });

  document.getElementById('btnCloseCompare').addEventListener('click', () => {
    compareModal.classList.remove('show');
  });
  document.getElementById('btnCloseCompareBottom').addEventListener('click', () => {
    compareModal.classList.remove('show');
  });

  const dirModal = document.getElementById('directoryModal');
  document.getElementById('btnToggleDirectory').addEventListener('click', () => {
    dirModal.classList.add('show');
  });
  document.getElementById('btnCloseDirectory').addEventListener('click', () => {
    dirModal.classList.remove('show');
  });

  document.querySelectorAll('.cat-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      const cat = pill.dataset.cat;
      const query = document.getElementById('dirSearchInput').value;
      renderDirectoryCards(state.campusData.nodes, cat, query);
    });
  });

  document.getElementById('dirSearchInput').addEventListener('input', (e) => {
    const activeCat = document.querySelector('.cat-pill.active').dataset.cat;
    renderDirectoryCards(state.campusData.nodes, activeCat, e.target.value);
  });

  const btnToggleTimeline = document.getElementById('btnToggleTimeline');
  if (btnToggleTimeline) {
    btnToggleTimeline.addEventListener('click', () => {
      const list = document.getElementById('timelineStepsList');
      const chev = document.getElementById('timelineChevron');
      if (list.style.display === 'none') {
        list.style.display = 'flex';
        if (chev) chev.style.transform = 'rotate(0deg)';
      } else {
        list.style.display = 'none';
        if (chev) chev.style.transform = 'rotate(-90deg)';
      }
    });
  }

  // Export AISC Report
  const btnExport = document.getElementById('btnExportBenchmark');
  if (btnExport) {
    btnExport.addEventListener('click', () => {
      if (!state.campusData) return;
      const startName = state.campusData.nodes[state.startNode].name;
      const goalName = state.campusData.nodes[state.goalNode].name;
      
      let report = `# AI PROJECT: SMART CAMPUS ROUTE PLANNER\n`;
      report += `## Benchmark Evaluation Report (6 Algorithms)\n`;
      report += `- Campus: Apex Institute of Technology & Science (AITS)\n`;
      report += `- Origin: ${startName} (Floor ${state.startFloor})\n`;
      report += `- Destination: ${goalName} (Floor ${state.goalFloor})\n`;
      report += `- Generated: ${new Date().toISOString()}\n\n`;
      report += `### Search Strategy Comparison Matrix\n\n`;
      report += `| Strategy | Type | Formula | Path Length | Travel Time | Expanded Nodes | Hops | Execution Time | Optimality |\n`;
      report += `|---|---|---|---|---|---|---|---|---|\n`;

      const rows = document.querySelectorAll('#benchmarkTableBody tr');
      rows.forEach(r => {
        const cols = Array.from(r.querySelectorAll('td')).map(td => td.textContent.trim());
        if (cols.length >= 9) {
          report += `| ${cols.join(' | ')} |\n`;
        }
      });

      report += `\n### Algorithmic & Heuristic Analysis\n`;
      report += `1. **A* Search (Euclidean)**:\n`;
      report += `   - Evaluation Function: $f(n) = g(n) + h(n)$\n`;
      report += `   - Admissibility: Straight-line Euclidean distance is the shortest possible metric between any two points in $\\mathbb{R}^2$, so $h(n) \\le h^*(n)$ holds unconditionally, guaranteeing an optimal solution path.\n\n`;
      report += `2. **Dijkstra vs A***:\n`;
      report += `   - Dijkstra expands in circular contours ($h(n) = 0$), expanding more nodes. A* biases its frontier directly towards the goal.\n`;

      const blob = new Blob([report], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `AISC_Campus_Route_Report_${state.startNode}_to_${state.goalNode}.md`;
      a.click();
      URL.revokeObjectURL(url);
    });
  }

  loadCampusData();
});
