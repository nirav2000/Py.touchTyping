<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Typing Trainer Prototype</title>
  <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils/drawing_utils.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>
  <style>
    body { text-align: center; font-family: sans-serif; }
    video, canvas { transform: scaleX(-1); } /* Mirror like a webcam */
    #feedback { font-size: 20px; margin-top: 10px; }
  </style>
</head>
<body>
  <h1>Typing Trainer (JS Prototype)</h1>
  <video id="video" playsinline style="display:none;"></video>
  <canvas id="canvas"></canvas>
  <div id="feedback">Press "F" or "J"…</div>

  <script>
    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");
    const feedback = document.getElementById("feedback");

    // Map expected finger per key (simplified)
    const fingerMap = { "f": "L_index", "j": "R_index" };

    let pressedKey = null;
    document.addEventListener("keydown", (e) => {
      pressedKey = e.key.toLowerCase();
    });

    // Mediapipe Hands
    const hands = new Hands({
      locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
    });

    hands.setOptions({
      maxNumHands: 2,
      minDetectionConfidence: 0.7,
      minTrackingConfidence: 0.7
    });

    hands.onResults(onResults);

    // Start camera
    const camera = new Camera(video, {
      onFrame: async () => {
        await hands.send({ image: video });
      },
      width: 640,
      height: 480
    });
    camera.start();

    function onResults(results) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height);

      if (results.multiHandLandmarks && results.multiHandedness) {
        results.multiHandLandmarks.forEach((landmarks, i) => {
          drawConnectors(ctx, landmarks, HAND_CONNECTIONS, { color: "#00FF00", lineWidth: 2 });
          drawLandmarks(ctx, landmarks, { color: "#FF0000", lineWidth: 1 });

          const handedness = results.multiHandedness[i].label; // "Left" or "Right"

          // Find lowest y (finger tip closest to top)
          const fingertipIds = { "thumb": 4, "index": 8, "middle": 12, "ring": 16, "pinky": 20 };
          let activeFinger = null, minY = 1;
          for (const [finger, idx] of Object.entries(fingertipIds)) {
            if (landmarks[idx].y < minY) {
              minY = landmarks[idx].y;
              activeFinger = finger;
            }
          }

          if (pressedKey) {
            const expected = fingerMap[pressedKey];
            const used = `${handedness[0]}_${activeFinger}`;

            if (expected && expected.toLowerCase() === used.toLowerCase()) {
              feedback.textContent = `✅ Correct finger for ${pressedKey.toUpperCase()}`;
            } else {
              feedback.textContent = `❌ Wrong finger for ${pressedKey.toUpperCase()} (used ${used})`;
            }
            pressedKey = null;
          }
        });
      }
    }
  </script>
</body>
</html>
