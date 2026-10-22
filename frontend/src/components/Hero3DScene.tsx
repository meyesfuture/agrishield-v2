import React, { useEffect, useRef, useState } from 'react';

interface Hero3DSceneProps {
  className?: string;
}

export const Hero3DScene: React.FC<Hero3DSceneProps> = ({ className = '' }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [webGLAvailable, setWebGLAvailable] = useState<boolean>(true);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState<boolean>(false);
  const [isMotionPaused, setIsMotionPaused] = useState<boolean>(false);
  const [isLoaded, setIsLoaded] = useState<boolean>(false);

  useEffect(() => {
    // 1. Check for reduced motion preference
    const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(motionQuery.matches);
    if (motionQuery.matches) {
      setIsMotionPaused(true);
    }

    const handleMotionChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
      if (e.matches) {
        setIsMotionPaused(true);
      }
    };
    motionQuery.addEventListener('change', handleMotionChange);

    // 2. Check WebGL availability
    const testCanvas = document.createElement('canvas');
    const gl = testCanvas.getContext('webgl2') || testCanvas.getContext('webgl');
    if (!gl) {
      setWebGLAvailable(false);
      return () => {
        motionQuery.removeEventListener('change', handleMotionChange);
      };
    }

    const container = containerRef.current;
    const canvas = canvasRef.current;
    if (!container || !canvas) return;

    let cancelled = false;
    let animationFrameId: number;
    let cleanupFn: (() => void) | null = null;

    // 3. Lazy-load Three.js dynamically to avoid bundling overhead and memory pressure
    import('three')
      .then((THREE) => {
        if (cancelled) return;

        try {
          const width = container.clientWidth || 600;
          const height = container.clientHeight || 380;

          // Initialize Renderer
          const renderer = new THREE.WebGLRenderer({
            canvas,
            alpha: true,
            antialias: true,
            powerPreference: 'high-performance',
          });
          renderer.setSize(width, height);
          renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
          renderer.toneMapping = THREE.ACESFilmicToneMapping;
          renderer.toneMappingExposure = 1.1;

          // Initialize Scene & Fog (Light Agricultural Atmosphere)
          const scene = new THREE.Scene();
          scene.fog = new THREE.FogExp2('#f8fafc', 0.02);

          // Initialize Camera
          const camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 100);
          camera.position.set(0, 3.5, 9.5);
          camera.lookAt(0, 1.2, 0);

          // --- Lighting ---
          const ambientLight = new THREE.AmbientLight(0xfffaed, 1.2);
          scene.add(ambientLight);

          const sunLight = new THREE.DirectionalLight(0xf59e0b, 2.0);
          sunLight.position.set(6, 10, 5);
          scene.add(sunLight);

          const fillLight = new THREE.DirectionalLight(0x94a3b8, 0.6);
          fillLight.position.set(-6, 4, -3);
          scene.add(fillLight);

          // --- Materials ---
          const siloBodyMaterial = new THREE.MeshStandardMaterial({
            color: 0xcbd5e1, // Light brushed steel
            metalness: 0.8,
            roughness: 0.35,
          });

          const siloRoofMaterial = new THREE.MeshStandardMaterial({
            color: 0xd97706, // Warm golden wheat accent
            metalness: 0.6,
            roughness: 0.35,
          });

          const gantryMaterial = new THREE.MeshStandardMaterial({
            color: 0x475569,
            metalness: 0.7,
            roughness: 0.5,
          });

          const groundMaterial = new THREE.MeshStandardMaterial({
            color: 0x166534, // Rich Punjab agricultural field green
            roughness: 0.85,
            metalness: 0.1,
          });

          const groundGridMaterial = new THREE.LineBasicMaterial({
            color: 0x86efac,
            transparent: true,
            opacity: 0.25,
          });

          // --- Silo Complex Group ---
          const siloComplex = new THREE.Group();

          const createSilo = (x: number, z: number, radius: number, height: number) => {
            const siloGroup = new THREE.Group();
            siloGroup.position.set(x, 0, z);

            const bodyGeo = new THREE.CylinderGeometry(radius, radius, height, 32);
            const bodyMesh = new THREE.Mesh(bodyGeo, siloBodyMaterial);
            bodyMesh.position.y = height / 2;
            siloGroup.add(bodyMesh);

            const ringGeo = new THREE.TorusGeometry(radius * 1.015, 0.025, 8, 32);
            for (let y = height * 0.25; y < height; y += height * 0.25) {
              const ringMesh = new THREE.Mesh(ringGeo, siloRoofMaterial);
              ringMesh.rotation.x = Math.PI / 2;
              ringMesh.position.y = y;
              siloGroup.add(ringMesh);
            }

            const roofHeight = radius * 0.8;
            const roofGeo = new THREE.ConeGeometry(radius * 1.04, roofHeight, 32);
            const roofMesh = new THREE.Mesh(roofGeo, siloRoofMaterial);
            roofMesh.position.y = height + roofHeight / 2;
            siloGroup.add(roofMesh);

            const capGeo = new THREE.CylinderGeometry(0.06, 0.06, 0.3, 12);
            const capMesh = new THREE.Mesh(capGeo, gantryMaterial);
            capMesh.position.y = height + roofHeight + 0.15;
            siloGroup.add(capMesh);

            return siloGroup;
          };

          const silo1 = createSilo(-1.4, 0, 0.9, 2.6);
          const silo2 = createSilo(0.2, -0.4, 1.05, 3.1);
          const silo3 = createSilo(1.8, 0.1, 0.85, 2.4);
          siloComplex.add(silo1);
          siloComplex.add(silo2);
          siloComplex.add(silo3);

          const gantryPipeGeo = new THREE.CylinderGeometry(0.04, 0.04, 3.6, 12);
          const gantryPipe = new THREE.Mesh(gantryPipeGeo, gantryMaterial);
          gantryPipe.rotation.z = Math.PI / 2;
          gantryPipe.position.set(0.2, 2.7, -0.15);
          siloComplex.add(gantryPipe);

          scene.add(siloComplex);

          // --- Ground Terrain ---
          const groundGeo = new THREE.PlaneGeometry(28, 28, 32, 32);
          const pos = groundGeo.attributes.position;
          for (let i = 0; i < pos.count; i++) {
            const vx = pos.getX(i);
            const vy = pos.getY(i);
            pos.setZ(i, Math.sin(vx * 0.4) * 0.15 + Math.cos(vy * 0.3) * 0.12);
          }
          groundGeo.computeVertexNormals();

          const groundMesh = new THREE.Mesh(groundGeo, groundMaterial);
          groundMesh.rotation.x = -Math.PI / 2;
          groundMesh.position.y = 0;
          scene.add(groundMesh);

          const groundWire = new THREE.LineSegments(
            new THREE.WireframeGeometry(groundGeo),
            groundGridMaterial
          );
          groundWire.rotation.x = -Math.PI / 2;
          groundWire.position.y = 0.01;
          scene.add(groundWire);

          // --- Floating Golden Grain Particle Field ---
          const particleCount = 400;
          const particleGeo = new THREE.BufferGeometry();
          const particlePositions = new Float32Array(particleCount * 3);
          const particleSpeeds = new Float32Array(particleCount);

          for (let i = 0; i < particleCount; i++) {
            particlePositions[i * 3] = (Math.random() - 0.5) * 16;
            particlePositions[i * 3 + 1] = Math.random() * 5 + 0.2;
            particlePositions[i * 3 + 2] = (Math.random() - 0.5) * 12;
            particleSpeeds[i] = 0.2 + Math.random() * 0.4;
          }

          particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));

          const particleMat = new THREE.PointsMaterial({
            color: 0xf5df9b,
            size: 0.045,
            transparent: true,
            opacity: 0.7,
            blending: THREE.AdditiveBlending,
          });

          const particleSystem = new THREE.Points(particleGeo, particleMat);
          scene.add(particleSystem);

          // --- Interactive Mouse Parallax Tracking ---
          let mouseX = 0;
          let mouseY = 0;
          let targetCameraX = 0;
          let targetCameraY = 3.5;

          const handleMouseMove = (e: MouseEvent) => {
            const rect = container.getBoundingClientRect();
            const normX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
            const normY = -(((e.clientY - rect.top) / rect.height) * 2 - 1);
            mouseX = normX * 0.9;
            mouseY = normY * 0.5;
          };

          container.addEventListener('mousemove', handleMouseMove, { passive: true });

          // --- Resize & Visibility Observers ---
          const resizeObserver = new ResizeObserver((entries) => {
            for (const entry of entries) {
              const newWidth = entry.contentRect.width;
              const newHeight = entry.contentRect.height;
              if (newWidth > 0 && newHeight > 0) {
                camera.aspect = newWidth / newHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(newWidth, newHeight);
              }
            }
          });
          resizeObserver.observe(container);

          let isVisible = true;
          const intersectionObserver = new IntersectionObserver(
            (entries) => {
              isVisible = entries[0].isIntersecting;
            },
            { threshold: 0.1 }
          );
          intersectionObserver.observe(container);

          // --- Render Loop ---
          const clock = new THREE.Clock();

          const animate = () => {
            animationFrameId = requestAnimationFrame(animate);

            if (!isVisible) return;

            const delta = clock.getDelta();
            const time = clock.getElapsedTime();

            targetCameraX += (mouseX - targetCameraX) * 0.05;
            targetCameraY += (3.5 + mouseY - targetCameraY) * 0.05;
            camera.position.x = targetCameraX;
            camera.position.y = targetCameraY;
            camera.lookAt(0, 1.2, 0);

            if (!isMotionPaused) {
              siloComplex.rotation.y = Math.sin(time * 0.15) * 0.06;

              const positions = particleGeo.attributes.position.array as Float32Array;
              for (let i = 0; i < particleCount; i++) {
                positions[i * 3 + 1] -= delta * particleSpeeds[i];
                positions[i * 3] += Math.sin(time * 0.5 + i) * 0.003;

                if (positions[i * 3 + 1] < 0.1) {
                  positions[i * 3 + 1] = 5.0;
                  positions[i * 3] = (Math.random() - 0.5) * 16;
                }
              }
              particleGeo.attributes.position.needsUpdate = true;
            }

            renderer.render(scene, camera);
          };

          animate();
          setIsLoaded(true);

          cleanupFn = () => {
            cancelAnimationFrame(animationFrameId);
            container.removeEventListener('mousemove', handleMouseMove);
            resizeObserver.disconnect();
            intersectionObserver.disconnect();

            groundGeo.dispose();
            groundMaterial.dispose();
            groundGridMaterial.dispose();
            particleGeo.dispose();
            particleMat.dispose();
            siloBodyMaterial.dispose();
            siloRoofMaterial.dispose();
            gantryMaterial.dispose();
            renderer.dispose();
          };
        } catch (initErr) {
          console.warn('Three.js initialization failed, using static fallback:', initErr);
          setWebGLAvailable(false);
        }
      })
      .catch((importErr) => {
        console.warn('Could not dynamically load Three.js, using static fallback:', importErr);
        setWebGLAvailable(false);
      });

    return () => {
      cancelled = true;
      motionQuery.removeEventListener('change', handleMotionChange);
      if (cleanupFn) {
        cleanupFn();
      }
    };
  }, [isMotionPaused]);

  return (
    <div
      ref={containerRef}
      className={`hero-3d-wrapper ${className}`}
      role="region"
      aria-label="3D Agricultural Landscape and Grain Silo Visualizer"
    >
      {/* 3D WebGL Canvas */}
      {webGLAvailable ? (
        <canvas
          ref={canvasRef}
          className={`hero-3d-canvas ${isLoaded ? 'loaded' : 'loading'}`}
          role="img"
          aria-label="Interactive 3D model of Punjab grain storage elevators, undulating wheat field, and floating harvest particles"
        />
      ) : (
        /* Accessible Static Fallback (SVG Architectural Silos) */
        <div className="hero-static-fallback" role="img" aria-label="Punjab Grain Silos Architectural Diagram">
          <svg viewBox="0 0 600 360" className="static-fallback-svg" aria-hidden="true">
            <defs>
              <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#0f172a" />
                <stop offset="100%" stopColor="#0a0d12" />
              </linearGradient>
              <linearGradient id="siloGrad" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#334155" />
                <stop offset="50%" stopColor="#94a3b8" />
                <stop offset="100%" stopColor="#1e293b" />
              </linearGradient>
              <linearGradient id="roofGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#f5df9b" />
                <stop offset="100%" stopColor="#b48328" />
              </linearGradient>
              <linearGradient id="fieldGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#1e2d24" />
                <stop offset="100%" stopColor="#0f172a" />
              </linearGradient>
            </defs>

            {/* Backdrop */}
            <rect width="600" height="360" fill="url(#skyGrad)" />

            {/* Stylized Grain Silo 1 (Left) */}
            <g transform="translate(140, 90)">
              <rect x="0" y="50" width="80" height="150" rx="4" fill="url(#siloGrad)" />
              <polygon points="40,10 -4,50 84,50" fill="url(#roofGrad)" />
              <line x1="0" y1="90" x2="80" y2="90" stroke="#cbd5e1" strokeWidth="1.5" opacity="0.4" />
              <line x1="0" y1="130" x2="80" y2="130" stroke="#cbd5e1" strokeWidth="1.5" opacity="0.4" />
              <line x1="0" y1="170" x2="80" y2="170" stroke="#cbd5e1" strokeWidth="1.5" opacity="0.4" />
            </g>

            {/* Stylized Grain Silo 2 (Center - Primary) */}
            <g transform="translate(250, 60)">
              <rect x="0" y="60" width="100" height="180" rx="4" fill="url(#siloGrad)" />
              <polygon points="50,15 -5,60 105,60" fill="url(#roofGrad)" />
              <line x1="0" y1="105" x2="100" y2="105" stroke="#cbd5e1" strokeWidth="1.5" opacity="0.4" />
              <line x1="0" y1="150" x2="100" y2="150" stroke="#cbd5e1" strokeWidth="1.5" opacity="0.4" />
              <line x1="0" y1="195" x2="100" y2="195" stroke="#cbd5e1" strokeWidth="1.5" opacity="0.4" />
            </g>

            {/* Stylized Grain Silo 3 (Right) */}
            <g transform="translate(380, 100)">
              <rect x="0" y="45" width="75" height="140" rx="4" fill="url(#siloGrad)" />
              <polygon points="37.5,10 -4,45 79,45" fill="url(#roofGrad)" />
              <line x1="0" y1="85" x2="75" y2="85" stroke="#cbd5e1" strokeWidth="1.5" opacity="0.4" />
              <line x1="0" y1="125" x2="75" y2="125" stroke="#cbd5e1" strokeWidth="1.5" opacity="0.4" />
            </g>

            {/* Conveyor Gantry */}
            <line x1="180" y1="120" x2="420" y2="120" stroke="#64748b" strokeWidth="3" strokeDasharray="4,4" />

            {/* Undulating Agricultural Field */}
            <path
              d="M0,250 Q150,230 300,260 T600,240 L600,360 L0,360 Z"
              fill="url(#fieldGrad)"
            />
            <path
              d="M0,280 Q200,260 400,290 T600,270 L600,360 L0,360 Z"
              fill="#131c16"
              opacity="0.8"
            />
          </svg>
          <div className="static-fallback-badge">
            <span>STATIC FALLBACK: WebGL Disabled or Unsupported</span>
          </div>
        </div>
      )}

      {/* Floating 3D Scene Controls & Metadata Pill */}
      <div className="hero-3d-overlay">
        <div className="hero-3d-tag">
          <span className="dot" aria-hidden="true" />
          <span>3D Grain Infrastructure Visualizer</span>
        </div>

        {webGLAvailable && (
          <button
            type="button"
            className="motion-toggle-btn"
            onClick={() => setIsMotionPaused(!isMotionPaused)}
            aria-pressed={isMotionPaused}
            title={prefersReducedMotion ? 'System prefers reduced motion (paused by default)' : (isMotionPaused ? 'Resume 3D rotation and particle breeze' : 'Pause 3D motion for accessibility')}
          >
            {isMotionPaused ? '▶ Play 3D' : '⏸ Pause 3D'}
          </button>
        )}
      </div>
    </div>
  );
};

export default Hero3DScene;
