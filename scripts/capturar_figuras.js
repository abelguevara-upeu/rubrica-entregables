// Exporta las figuras de los entregables desde cologistic-infra/docs/topologia.html (la página que genera cologistic-nettop).
//
//   cd scripts && npm i playwright     (sin descargar navegador: usa el Chrome instalado)
//   node capturar_figuras.js [figura ...]      sin argumentos: todas;  p. ej.  node capturar_figuras.js red vpn
//
// Las vistas de grafo (enlace, fisica, red y los recortes vpn, vpc, hipervisor) se exportan con cy.png() de Cytoscape a alta resolución
// (no una captura de pantalla): el texto queda nítido al ampliar. Las vistas HTML (computo, ubicacion) se capturan con una escala de píxeles alta.
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const HTML = "file://" + path.resolve(__dirname, "../../cologistic-infra/docs/topologia.html");
const OUT = path.resolve(__dirname, "../figuras");
const SOLO = process.argv.slice(2);
const quiere = f => SOLO.length === 0 || SOLO.includes(f);
const MAX_ANCHO = 11000;          // píxeles de ancho máximo por figura (el límite del lienzo del navegador es mayor, pero el DOCX pesaría demasiado)
const ESCALA = 6;
const AREA_MAX = 60e6;             // píxeles de área máxima

(async () => {
  const b = await chromium.launch({ channel: "chrome" });
  const abrir = async (vista, dsf = 1, ancho = 2400, alto = 1500) => {
    const p = await b.newPage({ viewport: { width: ancho, height: alto }, deviceScaleFactor: dsf });
    await p.goto(HTML); await p.waitForTimeout(2000);
    await p.evaluate(x => cambiarVista(x), vista); await p.waitForTimeout(4500);
    return p;
  };
  // Exporta el grafo (todo, o solo los nodos cuyo id cumple `re`, con sus contenedores y las aristas entre ellos) como PNG vectorial a escala alta.
  const grafo = async (vista, f, re = null, recorte = null) => {
    if (!quiere(f)) return;
    const p = await abrir(vista);
    const uri = await p.evaluate(({ re, ESCALA, MAX_ANCHO, AREA_MAX }) => {
      if (re) {
        let e = cy.nodes().filter(n => new RegExp(re, "i").test(n.id()));
        e = e.union(e.ancestors());
        cy.elements().not(e.union(e.connectedEdges().filter(a => e.contains(a.source()) && e.contains(a.target())))).remove();
      }
      // la escala se acota para que ni el ancho ni el área superen el límite (el lienzo del navegador falla con imágenes enormes)
      const bb = cy.elements().boundingBox();
      const escala = Math.min(ESCALA, MAX_ANCHO / bb.w, Math.sqrt(AREA_MAX / (bb.w * bb.h)));
      return cy.png({ full: true, scale: escala, bg: "#ffffff", output: "base64uri" });
    }, { re, ESCALA, MAX_ANCHO, AREA_MAX });
    fs.writeFileSync(`${OUT}/${f}.png`, Buffer.from(uri.split(",")[1], "base64"));
    await p.close(); console.log(f);
  };
  const pagina = async (vista, f, sel, dsf, ancho, alto) => {
    if (!quiere(f)) return;
    const p = await abrir(vista, dsf, ancho, alto);
    await p.locator(sel).screenshot({ path: `${OUT}/${f}.png` }); await p.close(); console.log(f);
  };

  await grafo("enlace", "enlace");
  await grafo("enlace", "hipervisor", "^(eq:HV|vs:|mq:|if:)");
  await grafo("enlace", "vpn", "^(nb|vp|sr|rn|bd:tn|bd:ln):|^eq:(FW-|UPLINK|Router)");
  await grafo("fisica", "fisica");
  await grafo("red", "red");
  await grafo("red", "vpc", "^(nb|vp):|^sr:NUBE|^rn:GCP");
  await grafo("red", "zonas_completa");           // la figura de zonas es la mitad superior de la vista de red (se recorta en el generador)
  await pagina("computo", "computo", "#html-vista", 4, 2400, 1500);
  await pagina("rack", "ubicacion", "#html-vista", 4, 1500, 1800);
  await b.close();
})();
