/**
 * 3D Visualization for Microgrid Digital Twin System
 * Uses Three.js for rendering
 */

class MicrogridVisualization {
    constructor(container) {
        this.container = container;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        
        // 3D Objects
        this.battery = null;
        this.pvPanels = [];
        this.windTurbines = [];
        this.loadBuilding = null;
        this.gridConnection = null;
        
        // Animation
        this.animationId = null;
        this.frameCount = 0;
        this.lastTime = performance.now();
        
        // Data
        this.currentData = null;
        
        this.init();
    }
    
    init() {
        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1a1a2e);
        this.scene.fog = new THREE.Fog(0x1a1a2e, 50, 200);
        
        // Camera
        this.camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        this.camera.position.set(30, 25, 30);
        this.camera.lookAt(0, 0, 0);
        
        // Renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.container.appendChild(this.renderer.domElement);
        
        // Controls
        try {
            this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
            this.controls.enableDamping = true;
            this.controls.dampingFactor = 0.05;
            this.controls.minDistance = 10;
            this.controls.maxDistance = 100;
        } catch (e) {
            console.warn('OrbitControls not available, using fallback');
            // Fallback controls will be handled by the inline script in HTML
            this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        }
        
        // Lighting
        this.setupLighting();
        
        // Ground
        this.createGround();
        
        // Create microgrid components
        this.createBattery();
        this.createPVPanels();
        this.createWindTurbines();
        this.createLoadBuilding();
        this.createGridConnection();
        this.createLabels();
        
        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());
        
        // Start animation
        this.animate();
    }
    
    setupLighting() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);
        
        // Directional light (sun)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(50, 50, 50);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        directionalLight.shadow.camera.near = 0.5;
        directionalLight.shadow.camera.far = 200;
        directionalLight.shadow.camera.left = -50;
        directionalLight.shadow.camera.right = 50;
        directionalLight.shadow.camera.top = 50;
        directionalLight.shadow.camera.bottom = -50;
        this.scene.add(directionalLight);
        
        // Point lights for visual appeal
        const pointLight1 = new THREE.PointLight(0x4a90e2, 0.5, 30);
        pointLight1.position.set(-15, 5, -15);
        this.scene.add(pointLight1);
        
        const pointLight2 = new THREE.PointLight(0xe24a4a, 0.5, 30);
        pointLight2.position.set(15, 5, 15);
        this.scene.add(pointLight2);
    }
    
    createGround() {
        const groundGeometry = new THREE.PlaneGeometry(100, 100);
        const groundMaterial = new THREE.MeshStandardMaterial({
            color: 0x2d3748,
            roughness: 0.8,
            metalness: 0.2
        });
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.position.y = 0;
        ground.receiveShadow = true;
        this.scene.add(ground);
        
        // Grid lines
        const gridHelper = new THREE.GridHelper(100, 20, 0x444444, 0x222222);
        this.scene.add(gridHelper);
    }
    
    createBattery() {
        const group = new THREE.Group();
        
        // Battery container
        const batteryGeometry = new THREE.BoxGeometry(4, 3, 2);
        const batteryMaterial = new THREE.MeshStandardMaterial({
            color: 0x4a90e2,
            metalness: 0.7,
            roughness: 0.3,
            emissive: 0x001122,
            emissiveIntensity: 0.2
        });
        const batteryBox = new THREE.Mesh(batteryGeometry, batteryMaterial);
        batteryBox.castShadow = true;
        batteryBox.receiveShadow = true;
        batteryBox.position.y = 1.5;
        group.add(batteryBox);
        
        // Battery indicator (SOC visualization)
        const indicatorGeometry = new THREE.BoxGeometry(3.5, 0.2, 1.5);
        const indicatorMaterial = new THREE.MeshStandardMaterial({
            color: 0x4caf50,
            emissive: 0x224422,
            emissiveIntensity: 0.5
        });
        this.batteryIndicator = new THREE.Mesh(indicatorGeometry, indicatorMaterial);
        this.batteryIndicator.position.set(0, 0.5, 0);
        group.add(this.batteryIndicator);
        
        // Base
        const baseGeometry = new THREE.BoxGeometry(5, 0.5, 3);
        const baseMaterial = new THREE.MeshStandardMaterial({ color: 0x333333 });
        const base = new THREE.Mesh(baseGeometry, baseMaterial);
        base.position.y = 0.25;
        group.add(base);
        
        group.position.set(0, 0, 0);
        this.scene.add(group);
        this.battery = group;
    }
    
    createPVPanels() {
        const panelCount = 8;
        const spacing = 6;
        const startX = -spacing * (panelCount / 2 - 0.5);
        
        for (let i = 0; i < panelCount; i++) {
            const group = new THREE.Group();
            
            // Panel
            const panelGeometry = new THREE.BoxGeometry(3, 0.1, 2);
            const panelMaterial = new THREE.MeshStandardMaterial({
                color: 0x1a1a1a,
                metalness: 0.9,
                roughness: 0.1,
                emissive: 0x224422,
                emissiveIntensity: 0.3
            });
            const panel = new THREE.Mesh(panelGeometry, panelMaterial);
            panel.rotation.x = -Math.PI / 4;
            panel.position.y = 2;
            panel.castShadow = true;
            group.add(panel);
            
            // Support pole
            const poleGeometry = new THREE.CylinderGeometry(0.1, 0.1, 2);
            const poleMaterial = new THREE.MeshStandardMaterial({ color: 0x666666 });
            const pole = new THREE.Mesh(poleGeometry, poleMaterial);
            pole.position.y = 1;
            group.add(pole);
            
            group.position.set(startX + i * spacing, 0, -12);
            this.scene.add(group);
            this.pvPanels.push(group);
        }
    }
    
    createWindTurbines() {
        const turbineCount = 3;
        const spacing = 15;
        const startX = -spacing;
        
        for (let i = 0; i < turbineCount; i++) {
            const group = new THREE.Group();
            
            // Tower
            const towerGeometry = new THREE.CylinderGeometry(0.3, 0.5, 8, 16);
            const towerMaterial = new THREE.MeshStandardMaterial({ color: 0x888888 });
            const tower = new THREE.Mesh(towerGeometry, towerMaterial);
            tower.position.y = 4;
            tower.castShadow = true;
            group.add(tower);
            
            // Nacelle
            const nacelleGeometry = new THREE.BoxGeometry(1.5, 1, 1.5);
            const nacelleMaterial = new THREE.MeshStandardMaterial({ color: 0xaaaaaa });
            const nacelle = new THREE.Mesh(nacelleGeometry, nacelleMaterial);
            nacelle.position.y = 8.5;
            group.add(nacelle);
            
            // Blades
            const bladeGroup = new THREE.Group();
            for (let j = 0; j < 3; j++) {
                const bladeGeometry = new THREE.BoxGeometry(0.2, 5, 0.05);
                const bladeMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff });
                const blade = new THREE.Mesh(bladeGeometry, bladeMaterial);
                blade.position.y = 2.5;
                blade.rotation.z = (j * Math.PI * 2) / 3;
                bladeGroup.add(blade);
            }
            bladeGroup.position.y = 8.5;
            group.add(bladeGroup);
            this.windTurbines.push({ group, bladeGroup });
            
            group.position.set(startX + i * spacing, 0, 12);
            this.scene.add(group);
        }
    }
    
    createLoadBuilding() {
        const group = new THREE.Group();
        
        // Building
        const buildingGeometry = new THREE.BoxGeometry(8, 6, 8);
        const buildingMaterial = new THREE.MeshStandardMaterial({
            color: 0x555555,
            roughness: 0.7
        });
        const building = new THREE.Mesh(buildingGeometry, buildingMaterial);
        building.position.y = 3;
        building.castShadow = true;
        building.receiveShadow = true;
        group.add(building);
        
        // Windows
        const windowMaterial = new THREE.MeshStandardMaterial({
            color: 0xffffaa,
            emissive: 0xffffaa,
            emissiveIntensity: 0.5
        });
        for (let i = 0; i < 2; i++) {
            for (let j = 0; j < 2; j++) {
                const windowGeometry = new THREE.PlaneGeometry(1, 1);
                const window = new THREE.Mesh(windowGeometry, windowMaterial);
                window.position.set(
                    -3 + i * 6,
                    2 + j * 2,
                    4.01
                );
                group.add(window);
            }
        }
        
        group.position.set(0, 0, -20);
        this.scene.add(group);
        this.loadBuilding = group;
    }
    
    createGridConnection() {
        const group = new THREE.Group();
        
        // Power lines
        const lineMaterial = new THREE.LineBasicMaterial({ color: 0xffff00 });
        const points = [
            new THREE.Vector3(0, 8, 0),
            new THREE.Vector3(0, 15, 0),
            new THREE.Vector3(20, 15, 0)
        ];
        const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
        const line = new THREE.Line(lineGeometry, lineMaterial);
        group.add(line);
        
        // Connection point
        const connectorGeometry = new THREE.SphereGeometry(0.5, 16, 16);
        const connectorMaterial = new THREE.MeshStandardMaterial({
            color: 0xffff00,
            emissive: 0xffff00,
            emissiveIntensity: 0.8
        });
        const connector = new THREE.Mesh(connectorGeometry, connectorMaterial);
        connector.position.set(0, 8, 0);
        group.add(connector);
        
        this.scene.add(group);
        this.gridConnection = group;
    }
    
    createLabels() {
        // This would require additional libraries for 3D text
        // For now, we'll use HTML overlays instead
    }
    
    update(data) {
        this.currentData = data;
        
        if (!data) return;
        
        // Update battery SOC indicator
        if (this.batteryIndicator && data.battery_soc !== undefined) {
            const soc = Math.max(0, Math.min(1, data.battery_soc));
            this.batteryIndicator.scale.x = soc;
            this.batteryIndicator.material.color.setHex(
                soc > 0.5 ? 0x4caf50 : (soc > 0.2 ? 0xff9800 : 0xf44336)
            );
            this.batteryIndicator.material.emissiveIntensity = 0.3 + soc * 0.5;
        }
        
        // Update PV panel glow based on power
        if (data.pv_power !== undefined && this.pvPanels.length > 0) {
            const intensity = Math.min(1, data.pv_power / 80);
            this.pvPanels.forEach(panel => {
                const mesh = panel.children[0];
                if (mesh && mesh.material) {
                    mesh.material.emissiveIntensity = 0.1 + intensity * 0.6;
                }
            });
        }
        
        // Update wind turbine rotation
        if (data.wind_power !== undefined && this.windTurbines.length > 0) {
            const speed = Math.min(1, data.wind_power / 60) * 0.02;
            this.windTurbines.forEach(turbine => {
                if (turbine.bladeGroup) {
                    turbine.bladeGroup.rotation.y += speed;
                }
            });
        }
        
        // Update building load visualization
        if (this.loadBuilding && data.load !== undefined) {
            const loadIntensity = Math.min(1, data.load / 150);
            this.loadBuilding.children.forEach((child, index) => {
                if (child.material && child.material.emissive) {
                    child.material.emissiveIntensity = 0.3 + loadIntensity * 0.7;
                }
            });
        }
        
        // Update grid connection
        if (this.gridConnection && data.grid_power !== undefined) {
            const power = Math.abs(data.grid_power);
            const intensity = Math.min(1, power / 100);
            this.gridConnection.children.forEach(child => {
                if (child.material && child.material.emissive) {
                    child.material.emissiveIntensity = 0.3 + intensity * 0.7;
                    if (data.grid_power > 0) {
                        child.material.color.setHex(0xff4444); // Import (red)
                    } else {
                        child.material.color.setHex(0x44ff44); // Export (green)
                    }
                }
            });
        }
    }
    
    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());
        
        // Update controls
        this.controls.update();
        
        // Rotate camera slightly for dynamic view (optional)
        // this.camera.position.x = 30 * Math.cos(Date.now() * 0.0001);
        // this.camera.position.z = 30 * Math.sin(Date.now() * 0.0001);
        // this.camera.lookAt(0, 0, 0);
        
        // Render
        this.renderer.render(this.scene, this.camera);
        
        // Calculate FPS
        this.frameCount++;
        const currentTime = performance.now();
        if (currentTime >= this.lastTime + 1000) {
            const fps = this.frameCount;
            this.frameCount = 0;
            this.lastTime = currentTime;
            const fpsElement = document.getElementById('fps');
            if (fpsElement) {
                fpsElement.textContent = `FPS: ${fps}`;
            }
        }
    }
    
    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }
    
    dispose() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        if (this.renderer) {
            this.renderer.dispose();
        }
    }
}
