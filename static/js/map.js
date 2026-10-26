/**
 * Apex Smart Campus — Tactical Vector Canvas Map Engine
 * Robust Multi-Run Animation Engine:
 * - Bulletproof animation loop with try/catch recovery (never dies or freezes)
 * - Safe frontier exploration interval cancellation on route changes
 * - Explicit GN & HN badges for every location
 * - Continuous replayability across multiple source-destination queries
 */

class CampusMapEngine {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    
    this.worldWidth = 1000;
    this.worldHeight = 900;
    
    this.scale = 1.0;
    this.offsetX = 0;
    this.offsetY = 0;
    this.minScale = 0.55;
    this.maxScale = 2.4;
    
    this.isDragging = false;
    this.dragStartX = 0;
    this.dragStartY = 0;
    this.hoveredNode = null;
    this.followAvatar = true;
    
    this.nodes = {};
    this.edges = [];
    this.startNodeId = "AB1";
    this.goalNodeId = "AB2";
    
    this.currentPath = [];
    this.visitedOrder = [];
    this.visitedStep = 0;
    this.isVisualizingFrontier = false;
    this.frontierInterval = null;
    this.allNodesHeuristics = {};
    this.speedMultiplier = 2.0;
    
    this.avatar = {
      x: 300,
      y: 210,
      targetX: 300,
      targetY: 210,
      angle: 0,
      speedKmh: 4.8,
      isMoving: false,
      isPaused: false,
      segmentIndex: 0,
      segmentProgress: 0,
      totalProgress: 0,
      pulsePhase: 0,
      radarSweepAngle: 0,
      currentG: 0.0,
      currentH: 0.0,
      currentF: 0.0
    };
    
    this.weather = "clear";
    this.waterPhase = 0;
    this.dashOffset = 0;
    
    this.initCanvasSize();
    this.bindEvents();
    this.centerView();
    this.startAnimationLoop();
  }

  initCanvasSize() {
    const dpr = window.devicePixelRatio || 1;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.ctx.scale(dpr, dpr);
    this.viewWidth = rect.width;
    this.viewHeight = rect.height;
  }

  setCampusData(nodes, edges) {
    this.nodes = nodes || {};
    this.edges = edges || [];
    if (this.nodes[this.startNodeId]) {
      this.avatar.x = this.nodes[this.startNodeId].x;
      this.avatar.y = this.nodes[this.startNodeId].y;
    }
  }

  centerView() {
    const margin = 60;
    const availWidth = this.viewWidth - 490;
    const scaleX = availWidth / (this.worldWidth + margin * 2);
    const scaleY = this.viewHeight / (this.worldHeight + margin * 2);
    this.scale = Math.max(Math.min(scaleX, scaleY), this.minScale);
    
    this.offsetX = (availWidth - this.worldWidth * this.scale) / 2 + 20;
    this.offsetY = (this.viewHeight - this.worldHeight * this.scale) / 2;
  }

  bindEvents() {
    window.addEventListener('resize', () => {
      this.initCanvasSize();
    });

    this.canvas.addEventListener('mousedown', (e) => {
      this.isDragging = true;
      this.dragStartX = e.clientX - this.offsetX;
      this.dragStartY = e.clientY - this.offsetY;
    });

    window.addEventListener('mousemove', (e) => {
      if (this.isDragging) {
        this.offsetX = e.clientX - this.dragStartX;
        this.offsetY = e.clientY - this.dragStartY;
        this.followAvatar = false;
        const btn = document.getElementById('btnFollowAvatar');
        if (btn) btn.classList.remove('active');
      } else {
        this.handleCanvasHover(e);
      }
    });

    window.addEventListener('mouseup', () => {
      this.isDragging = false;
    });

    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.12 : 0.89;
      const mouseX = e.clientX;
      const mouseY = e.clientY;
      const newScale = Math.min(Math.max(this.scale * zoomFactor, this.minScale), this.maxScale);
      this.offsetX = mouseX - (mouseX - this.offsetX) * (newScale / this.scale);
      this.offsetY = mouseY - (mouseY - this.offsetY) * (newScale / this.scale);
      this.scale = newScale;
    }, { passive: false });

    this.canvas.addEventListener('click', () => {
      if (this.hoveredNode && window.onCampusNodeClicked) {
        window.onCampusNodeClicked(this.hoveredNode);
      }
    });
  }

  screenToWorld(screenX, screenY) {
    return {
      x: (screenX - this.offsetX) / this.scale,
      y: (screenY - this.offsetY) / this.scale
    };
  }

  worldToScreen(worldX, worldY) {
    return {
      x: worldX * this.scale + this.offsetX,
      y: worldY * this.scale + this.offsetY
    };
  }

  handleCanvasHover(e) {
    const rect = this.canvas.getBoundingClientRect();
    const mousePos = this.screenToWorld(e.clientX - rect.left, e.clientY - rect.top);
    
    let found = null;
    const hitRadius = 26;
    for (const id in this.nodes) {
      const node = this.nodes[id];
      const dx = mousePos.x - node.x;
      const dy = mousePos.y - node.y;
      if (dx * dx + dy * dy <= hitRadius * hitRadius) {
        found = node;
        break;
      }
    }

    if (found !== this.hoveredNode) {
      this.hoveredNode = found;
      this.canvas.style.cursor = found ? 'pointer' : (this.isDragging ? 'grabbing' : 'grab');
      if (window.onCampusNodeHovered) {
        const hData = found && this.allNodesHeuristics ? this.allNodesHeuristics[found.id] : null;
        window.onCampusNodeHovered(found, e.clientX, e.clientY, hData);
      }
    }
  }

  // BULLETPROOF ANIMATION LOOP WITH EXCEPTION RECOVERY
  startAnimationLoop() {
    const render = () => {
      try {
        this.updateState();
        this.draw();
      } catch (err) {
        console.warn("Animation frame recovered safely:", err);
      }
      requestAnimationFrame(render);
    };
    requestAnimationFrame(render);
  }

  updateState() {
    this.waterPhase += 0.03;
    this.dashOffset -= 1.4;
    this.avatar.pulsePhase += 0.06;
    this.avatar.radarSweepAngle += 0.05;

    // Follow moving avatar
    if (this.followAvatar && this.avatar.isMoving) {
      const targetScreenX = (this.viewWidth - 480) / 2;
      const targetScreenY = this.viewHeight / 2;
      const currentScreen = this.worldToScreen(this.avatar.x, this.avatar.y);
      this.offsetX += (targetScreenX - currentScreen.x) * 0.08;
      this.offsetY += (targetScreenY - currentScreen.y) * 0.08;
    }

    if (this.avatar.isMoving && !this.avatar.isPaused && this.currentPath.length > 1) {
      this.advanceAvatarAlongPath();
    }
  }

  advanceAvatarAlongPath() {
    if (!this.currentPath || this.currentPath.length < 2) {
      this.avatar.isMoving = false;
      return;
    }

    if (this.avatar.segmentIndex >= this.currentPath.length - 1) {
      this.avatar.isMoving = false;
      this.avatar.totalProgress = 1.0;
      if (this.nodes[this.currentPath[this.currentPath.length - 1]]) {
        const dest = this.nodes[this.currentPath[this.currentPath.length - 1]];
        this.avatar.x = dest.x;
        this.avatar.y = dest.y;
      }
      if (window.updateTelemetryHUD) {
        window.updateTelemetryHUD(this.avatar);
      }
      if (window.onNavigationArrival) {
        window.onNavigationArrival();
      }
      return;
    }

    const uId = this.currentPath[this.avatar.segmentIndex];
    const vId = this.currentPath[this.avatar.segmentIndex + 1];
    const u = this.nodes[uId];
    const v = this.nodes[vId];

    if (!u || !v) {
      this.avatar.isMoving = false;
      return;
    }

    const dx = v.x - u.x;
    const dy = v.y - u.y;
    const segDist = Math.sqrt(dx * dx + dy * dy);

    // Highly visible animated movement step
    const mult = this.speedMultiplier || 2.0;
    const step = (1.5 / Math.max(segDist, 30)) * mult;
    this.avatar.segmentProgress += step;

    // Smooth heading angle update
    const targetAngle = Math.atan2(dy, dx);
    let diff = targetAngle - this.avatar.angle;
    while (diff < -Math.PI) diff += Math.PI * 2;
    while (diff > Math.PI) diff -= Math.PI * 2;
    this.avatar.angle += diff * 0.16;

    if (this.avatar.segmentProgress >= 1.0) {
      this.avatar.segmentProgress = 0.0;
      this.avatar.segmentIndex++;
      this.avatar.x = v.x;
      this.avatar.y = v.y;
      
      if (window.onWaypointReached) {
        window.onWaypointReached(vId, this.avatar.segmentIndex);
      }
    } else {
      this.avatar.x = u.x + dx * this.avatar.segmentProgress;
      this.avatar.y = u.y + dy * this.avatar.segmentProgress;
    }

    const totalSegments = Math.max(this.currentPath.length - 1, 1);
    this.avatar.totalProgress = Math.min(
      (this.avatar.segmentIndex + this.avatar.segmentProgress) / totalSegments,
      1.0
    );

    if (window.updateTelemetryHUD) {
      window.updateTelemetryHUD(this.avatar);
    }
  }

  draw() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.viewWidth, this.viewHeight);

    ctx.save();
    ctx.translate(this.offsetX, this.offsetY);
    ctx.scale(this.scale, this.scale);

    this.drawCampusTerrain(ctx);
    this.drawCampusBuildings(ctx);
    this.drawCampusRoads(ctx);
    this.drawSearchFrontier(ctx);
    this.drawActiveRoute(ctx);
    this.drawCampusNodes(ctx);
    this.drawAvatar(ctx);

    ctx.restore();
  }

  drawCampusTerrain(ctx) {
    ctx.fillStyle = '#080d16';
    ctx.fillRect(40, 20, 920, 840);

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.025)';
    ctx.lineWidth = 1;
    for (let x = 50; x <= 950; x += 50) {
      ctx.beginPath();
      ctx.moveTo(x, 30);
      ctx.lineTo(x, 850);
      ctx.stroke();
    }
    for (let y = 30; y <= 850; y += 50) {
      ctx.beginPath();
      ctx.moveTo(50, y);
      ctx.lineTo(950, y);
      ctx.stroke();
    }

    // Grand Stairs
    ctx.save();
    ctx.translate(500, 360);
    for (let r = 55; r >= 15; r -= 10) {
      ctx.fillStyle = r % 20 === 0 ? '#131e2e' : '#0e1724';
      ctx.beginPath();
      ctx.arc(0, 0, r, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = 'rgba(16, 185, 129, 0.2)';
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }
    const fountainPulse = (Math.sin(this.waterPhase * 2) + 1) * 4;
    ctx.fillStyle = 'rgba(6, 182, 212, 0.3)';
    ctx.beginPath();
    ctx.arc(0, 0, 10 + fountainPulse, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // Cricket Ground
    ctx.save();
    ctx.translate(840, 420);
    ctx.fillStyle = '#0a2318';
    ctx.beginPath();
    ctx.ellipse(0, 0, 85, 65, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = 'rgba(34, 197, 94, 0.35)';
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 4]);
    ctx.beginPath();
    ctx.ellipse(0, 0, 50, 38, 0, 0, Math.PI * 2);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = '#92400e';
    ctx.fillRect(-14, -6, 28, 12);
    ctx.strokeStyle = '#fef3c7';
    ctx.strokeRect(-14, -6, 28, 12);
    ctx.restore();

    // Football Ground
    ctx.save();
    ctx.translate(260, 590);
    ctx.strokeStyle = '#991b1b';
    ctx.lineWidth = 12;
    ctx.beginPath();
    ctx.roundRect(-55, -34, 110, 68, 34);
    ctx.stroke();

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.fillStyle = '#064e3b';
    ctx.beginPath();
    ctx.roundRect(-45, -24, 90, 48, 20);
    ctx.fill();

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.25)';
    ctx.strokeRect(-38, -18, 76, 36);
    ctx.beginPath();
    ctx.moveTo(0, -18);
    ctx.lineTo(0, 18);
    ctx.arc(0, 0, 8, 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();

    // Smart Flap Gates
    ctx.save();
    ctx.translate(500, 140);
    ctx.fillStyle = '#1e293b';
    ctx.beginPath();
    ctx.roundRect(-40, -10, 80, 20, 6);
    ctx.fill();
    ctx.strokeStyle = 'rgba(6, 182, 212, 0.4)';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    for (let gx = -24; gx <= 24; gx += 16) {
      ctx.fillStyle = '#10b981';
      ctx.fillRect(gx - 2, -6, 4, 12);
    }
    ctx.restore();

    // Amphitheatre
    ctx.save();
    ctx.translate(780, 670);
    ctx.strokeStyle = 'rgba(245, 158, 11, 0.3)';
    ctx.lineWidth = 2;
    for (let ar = 45; ar >= 15; ar -= 10) {
      ctx.beginPath();
      ctx.arc(0, 0, ar, Math.PI * 0.8, Math.PI * 2.2);
      ctx.stroke();
    }
    ctx.restore();
  }

  drawCampusBuildings(ctx) {
    for (const id in this.nodes) {
      const node = this.nodes[id];
      if (["GRAND_STAIRS", "FLAP_GATES", "MAIN_EXIT", "CRICKET_GROUND", "FOOTBALL_GROUND", "AMPHITHEATRE"].includes(id)) {
        continue;
      }

      const w = 56;
      const h = 40;
      const bx = node.x - w / 2;
      const by = node.y - h / 2 - 8;

      ctx.fillStyle = 'rgba(0, 0, 0, 0.45)';
      ctx.beginPath();
      ctx.roundRect(bx + 4, by + 6, w, h, 8);
      ctx.fill();

      ctx.fillStyle = '#101726';
      ctx.beginPath();
      ctx.roundRect(bx, by, w, h, 8);
      ctx.fill();

      let strokeColor = 'rgba(255, 255, 255, 0.12)';
      if (node.category === 'academic') strokeColor = 'rgba(6, 182, 212, 0.5)';
      else if (node.category === 'life') strokeColor = 'rgba(16, 185, 129, 0.5)';
      else if (node.category === 'sports') strokeColor = 'rgba(245, 158, 11, 0.5)';
      else if (node.category === 'residential') strokeColor = 'rgba(244, 63, 94, 0.5)';

      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = 1.4;
      ctx.stroke();

      if (node.has_floors) {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.04)';
        ctx.fillRect(bx + 4, by + 12, w - 8, 2);
        ctx.fillRect(bx + 4, by + 24, w - 8, 2);

        const liftSide = node.lift_side || "both";
        ctx.fillStyle = '#22d3ee';
        if (liftSide === "left" || liftSide === "both") {
          ctx.beginPath();
          ctx.arc(bx + 8, by + 8, 3, 0, Math.PI * 2);
          ctx.fill();
        }
        if (liftSide === "right" || liftSide === "both") {
          ctx.beginPath();
          ctx.arc(bx + w - 8, by + 8, 3, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    }
  }

  drawCampusRoads(ctx) {
    ctx.save();
    for (const edge of this.edges) {
      const u = this.nodes[edge.u];
      const v = this.nodes[edge.v];
      if (!u || !v) continue;

      let roadWidth = 5;
      let roadColor = 'rgba(30, 41, 59, 0.7)';
      if (edge.surface === "gravel") {
        roadWidth = 3.5;
        roadColor = 'rgba(40, 50, 65, 0.5)';
      } else if (edge.surface === "indoor") {
        roadWidth = 6;
        roadColor = 'rgba(56, 189, 248, 0.12)';
      } else if (edge.surface === "stairs") {
        roadWidth = 6;
        roadColor = 'rgba(245, 158, 11, 0.15)';
      }

      ctx.strokeStyle = roadColor;
      ctx.lineWidth = roadWidth;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(u.x, u.y);
      ctx.lineTo(v.x, v.y);
      ctx.stroke();

      ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 6]);
      ctx.beginPath();
      ctx.moveTo(u.x, u.y);
      ctx.lineTo(v.x, v.y);
      ctx.stroke();
      ctx.setLineDash([]);
    }
    ctx.restore();
  }

  // BULLETPROOF SAFE FRONTIER DRAWING
  drawSearchFrontier(ctx) {
    if (!this.visitedOrder || !Array.isArray(this.visitedOrder) || this.visitedOrder.length === 0) return;

    ctx.save();
    const maxStep = Math.min(
      this.isVisualizingFrontier ? this.visitedStep : this.visitedOrder.length,
      this.visitedOrder.length
    );
    
    for (let i = 0; i < maxStep; i++) {
      const stepData = this.visitedOrder[i];
      if (!stepData || !stepData.node_id) continue;
      const node = this.nodes[stepData.node_id];
      if (!node) continue;

      if (stepData.parent_id && this.nodes[stepData.parent_id]) {
        const parent = this.nodes[stepData.parent_id];
        ctx.strokeStyle = 'rgba(168, 85, 247, 0.3)';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([2, 4]);
        ctx.beginPath();
        ctx.moveTo(parent.x, parent.y);
        ctx.lineTo(node.x, node.y);
        ctx.stroke();
        ctx.setLineDash([]);
      }

      ctx.fillStyle = 'rgba(168, 85, 247, 0.2)';
      ctx.beginPath();
      ctx.arc(node.x, node.y, 16, 0, Math.PI * 2);
      ctx.fill();

      ctx.font = '8px JetBrains Mono';
      ctx.fillStyle = 'rgba(216, 180, 254, 0.9)';
      ctx.textAlign = 'center';
      ctx.fillText(`#${stepData.step || (i + 1)}`, node.x, node.y - 15);
    }
    ctx.restore();
  }

  drawActiveRoute(ctx) {
    if (!this.currentPath || this.currentPath.length < 2) return;

    const validPoints = [];
    for (let i = 0; i < this.currentPath.length; i++) {
      const node = this.nodes[this.currentPath[i]];
      if (node) validPoints.push(node);
    }
    if (validPoints.length < 2) return;

    ctx.save();
    ctx.strokeStyle = 'rgba(16, 185, 129, 0.25)';
    ctx.lineWidth = 14;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.beginPath();
    for (let i = 0; i < validPoints.length; i++) {
      const pt = validPoints[i];
      if (i === 0) ctx.moveTo(pt.x, pt.y);
      else ctx.lineTo(pt.x, pt.y);
    }
    ctx.stroke();

    ctx.strokeStyle = '#10b981';
    ctx.lineWidth = 4;
    ctx.stroke();

    ctx.strokeStyle = '#00f59b';
    ctx.lineWidth = 2.5;
    ctx.setLineDash([8, 12]);
    ctx.lineDashOffset = this.dashOffset;
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.restore();
  }

  drawCampusNodes(ctx) {
    for (const id in this.nodes) {
      const node = this.nodes[id];
      const isStart = (id === this.startNodeId);
      const isGoal = (id === this.goalNodeId);
      const isHovered = (this.hoveredNode && this.hoveredNode.id === id);
      const isOnPath = this.currentPath && this.currentPath.includes(id);

      ctx.save();

      if (isStart || isGoal) {
        const pulseSize = 16 + (Math.sin(this.avatar.pulsePhase * 2) + 1) * 6;
        ctx.strokeStyle = isStart ? 'rgba(16, 185, 129, 0.4)' : 'rgba(244, 63, 94, 0.4)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(node.x, node.y, pulseSize, 0, Math.PI * 2);
        ctx.stroke();
      }

      let nodeRadius = isHovered ? 14 : 10;
      let fillColor = '#0e1726';
      let strokeColor = 'rgba(255, 255, 255, 0.3)';

      if (isStart) {
        fillColor = '#10b981';
        strokeColor = '#ffffff';
        nodeRadius = 12;
      } else if (isGoal) {
        fillColor = '#f43f5e';
        strokeColor = '#ffffff';
        nodeRadius = 12;
      } else if (isOnPath) {
        fillColor = '#065f46';
        strokeColor = '#34d399';
      }

      ctx.fillStyle = fillColor;
      ctx.beginPath();
      ctx.arc(node.x, node.y, nodeRadius, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = 2;
      ctx.stroke();

      if (!isStart && !isGoal) {
        ctx.fillStyle = strokeColor;
        ctx.beginPath();
        ctx.arc(node.x, node.y, 3, 0, Math.PI * 2);
        ctx.fill();
      }

      this.drawNodeLabelWithHeuristics(ctx, node, isStart, isGoal, isHovered, isOnPath);

      ctx.restore();
    }
  }

  drawNodeLabelWithHeuristics(ctx, node, isStart, isGoal, isHovered, isOnPath) {
    const hData = this.allNodesHeuristics ? this.allNodesHeuristics[node.id] : null;
    const text = node.short_name;
    const labelY = node.y + 18;

    ctx.font = isHovered ? '600 11px Inter, sans-serif' : '500 10px Inter, sans-serif';
    const textWidth = ctx.measureText(text).width;
    const paddingX = 8;

    ctx.fillStyle = isHovered ? 'rgba(15, 23, 42, 0.95)' : 'rgba(11, 16, 25, 0.88)';
    ctx.beginPath();
    ctx.roundRect(node.x - textWidth / 2 - paddingX, labelY - 2, textWidth + paddingX * 2, 18, 6);
    ctx.fill();

    let borderColor = 'rgba(255, 255, 255, 0.12)';
    if (isStart) borderColor = '#10b981';
    else if (isGoal) borderColor = '#f43f5e';
    else if (isHovered) borderColor = '#38bdf8';

    ctx.strokeStyle = borderColor;
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.fillStyle = isStart ? '#10b981' : (isGoal ? '#f43f5e' : (isHovered ? '#ffffff' : '#cbd5e1'));
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, node.x, labelY + 7);

    // GN & HN BADGE FOR EVERY LOCATION
    if (hData && (isOnPath || isHovered || this.scale >= 1.0)) {
      const gnText = `g:${Math.round(hData.g)}m | h:${Math.round(hData.h)}m`;
      ctx.font = '700 8px JetBrains Mono';
      const hw = ctx.measureText(gnText).width;
      const hBadgeY = labelY + 20;

      ctx.fillStyle = isOnPath ? 'rgba(6, 182, 212, 0.18)' : 'rgba(0, 0, 0, 0.6)';
      ctx.beginPath();
      ctx.roundRect(node.x - hw / 2 - 4, hBadgeY, hw + 8, 14, 4);
      ctx.fill();

      ctx.strokeStyle = isOnPath ? '#06b6d4' : 'rgba(255, 255, 255, 0.15)';
      ctx.lineWidth = 0.8;
      ctx.stroke();

      ctx.fillStyle = isOnPath ? '#22d3ee' : '#94a3b8';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(gnText, node.x, hBadgeY + 7);
    }
  }

  drawAvatar(ctx) {
    if (!this.avatar.isMoving && this.avatar.segmentIndex === 0 && !this.currentPath.length) return;

    ctx.save();
    const x = this.avatar.x;
    const y = this.avatar.y;
    const angle = this.avatar.angle;

    // Translucent Emerald Radar Cone
    const coneDistance = 110;
    const fovAngle = Math.PI / 3.2;

    ctx.save();
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.arc(x, y, coneDistance, angle - fovAngle / 2, angle + fovAngle / 2);
    ctx.closePath();

    const coneGrad = ctx.createRadialGradient(x, y, 4, x, y, coneDistance);
    coneGrad.addColorStop(0, 'rgba(16, 185, 129, 0.45)');
    coneGrad.addColorStop(0.5, 'rgba(16, 185, 129, 0.15)');
    coneGrad.addColorStop(1, 'rgba(16, 185, 129, 0.0)');
    ctx.fillStyle = coneGrad;
    ctx.fill();
    ctx.restore();

    // Radar Shockwave
    const radarPulse = (Math.sin(this.avatar.pulsePhase * 3) + 1) * 12;
    ctx.strokeStyle = 'rgba(0, 245, 155, 0.35)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(x, y, 16 + radarPulse, 0, Math.PI * 2);
    ctx.stroke();

    // User Avatar Disc
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(x, y, 12, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#091510';
    ctx.beginPath();
    ctx.arc(x, y, 10, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#00f59b';
    ctx.beginPath();
    ctx.arc(x, y, 6, 0, Math.PI * 2);
    ctx.fill();

    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.fillStyle = '#00f59b';
    ctx.beginPath();
    ctx.moveTo(11, 0);
    ctx.lineTo(5, -4);
    ctx.lineTo(5, 4);
    ctx.closePath();
    ctx.fill();
    ctx.restore();

    // Floating f = g + h Tag
    if (this.avatar.currentF > 0) {
      const tagText = `f=${Math.round(this.avatar.currentF)}m (g=${Math.round(this.avatar.currentG)}, h=${Math.round(this.avatar.currentH)})`;
      ctx.font = '700 9px JetBrains Mono';
      const tw = ctx.measureText(tagText).width;
      
      ctx.fillStyle = 'rgba(11, 16, 26, 0.9)';
      ctx.beginPath();
      ctx.roundRect(x - tw / 2 - 6, y - 30, tw + 12, 16, 4);
      ctx.fill();

      ctx.strokeStyle = '#22d3ee';
      ctx.lineWidth = 1;
      ctx.stroke();

      ctx.fillStyle = '#22d3ee';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(tagText, x, y - 22);
    }

    ctx.restore();
  }

  // CONTROLLER ACTIONS WITH SAFE RESET
  setRoute(path, visitedOrder = [], allNodesHeuristics = {}) {
    // Safely clear any active frontier interval
    if (this.frontierInterval) {
      clearInterval(this.frontierInterval);
      this.frontierInterval = null;
    }
    this.isVisualizingFrontier = false;
    this.visitedStep = 0;

    this.currentPath = Array.isArray(path) ? path : [];
    this.visitedOrder = Array.isArray(visitedOrder) ? visitedOrder : [];
    this.allNodesHeuristics = allNodesHeuristics || {};
    
    // Always reset avatar position to the new start node
    if (this.currentPath.length > 0 && this.nodes[this.currentPath[0]]) {
      const start = this.nodes[this.currentPath[0]];
      this.avatar.x = start.x;
      this.avatar.y = start.y;
      this.avatar.segmentIndex = 0;
      this.avatar.segmentProgress = 0;
      this.avatar.totalProgress = 0;
      this.avatar.isMoving = false;
      this.avatar.isPaused = false;
      
      if (this.currentPath.length > 1 && this.nodes[this.currentPath[1]]) {
        const next = this.nodes[this.currentPath[1]];
        this.avatar.angle = Math.atan2(next.y - start.y, next.x - start.x);
      }
    }
  }

  startNavigation(multiplier = 2.0) {
    if (!this.currentPath || this.currentPath.length < 2) return;
    this.speedMultiplier = multiplier;
    this.avatar.segmentIndex = 0;
    this.avatar.segmentProgress = 0;
    this.avatar.totalProgress = 0;
    this.avatar.isMoving = true;
    this.avatar.isPaused = false;
    this.followAvatar = true;
    
    const startNode = this.nodes[this.currentPath[0]];
    if (startNode) {
      this.avatar.x = startNode.x;
      this.avatar.y = startNode.y;
    }

    if (this.currentPath.length > 1 && this.nodes[this.currentPath[0]] && this.nodes[this.currentPath[1]]) {
      const u = this.nodes[this.currentPath[0]];
      const v = this.nodes[this.currentPath[1]];
      this.avatar.angle = Math.atan2(v.y - u.y, v.x - u.x);
    }

    const btn = document.getElementById('btnFollowAvatar');
    if (btn) btn.classList.add('active');
  }

  pauseNavigation() {
    this.avatar.isPaused = !this.avatar.isPaused;
    return this.avatar.isPaused;
  }

  resetAvatar() {
    if (this.frontierInterval) {
      clearInterval(this.frontierInterval);
      this.frontierInterval = null;
    }
    this.isVisualizingFrontier = false;
    this.avatar.isMoving = false;
    this.avatar.isPaused = false;
    this.avatar.segmentIndex = 0;
    this.avatar.segmentProgress = 0;
    this.avatar.totalProgress = 0;
    if (this.currentPath.length > 0 && this.nodes[this.currentPath[0]]) {
      this.avatar.x = this.nodes[this.currentPath[0]].x;
      this.avatar.y = this.nodes[this.currentPath[0]].y;
    }
  }

  animateFrontierExploration(onComplete) {
    if (this.frontierInterval) {
      clearInterval(this.frontierInterval);
      this.frontierInterval = null;
    }
    if (!this.visitedOrder || !Array.isArray(this.visitedOrder) || this.visitedOrder.length === 0) {
      if (onComplete) onComplete();
      return;
    }
    this.isVisualizingFrontier = true;
    this.visitedStep = 0;
    
    this.frontierInterval = setInterval(() => {
      this.visitedStep++;
      if (this.visitedStep >= this.visitedOrder.length) {
        clearInterval(this.frontierInterval);
        this.frontierInterval = null;
        this.isVisualizingFrontier = false;
        if (onComplete) onComplete();
      }
    }, 40);
  }
}

window.CampusMapEngine = CampusMapEngine;
