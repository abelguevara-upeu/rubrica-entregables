// Exporta figura_pipeline_cicd.html a figuras/pipeline_cicd_wms_backend.png (1920x1080 a escala 2 = 3840x2160).
//   cd scripts && node render_pipeline_cicd.js
const { chromium } = require("playwright");
const path = require("path");

(async () => {
  const b = await chromium.launch({ channel: "chrome" });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2 });
  await p.goto("file://" + path.resolve(__dirname, "figura_pipeline_cicd.html"));
  await p.waitForTimeout(800);
  await p.screenshot({ path: path.resolve(__dirname, "../figuras/pipeline_cicd_wms_backend.png") });
  await b.close();
  console.log("pipeline_cicd_wms_backend.png");
})();
