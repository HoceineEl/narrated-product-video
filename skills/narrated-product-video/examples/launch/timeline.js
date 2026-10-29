// Example GSAP timeline from a shipped launch film: every tween is at("word", offset), T from word_times.py, RECTS from DOM rects shot with the screenshots.
const tl = gsap.timeline({ paused: true });
const T = window.T, RX = window.RECTS;
const E = "power3.out", EI = "power2.inOut", B = "back.out(1.7)";
const at = (k, o = 0) => T[k] + o;

/* S1 HOOK */
tl.fromTo("#s1-h1", { scale: 1.35, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.4, ease: "expo.out" }, at("fin", -0.05));
tl.fromTo("#s1-date", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4, ease: E }, at("fin", 0.2));
tl.to("#s1-title", { y: -330, scale: 0.42, duration: 0.55, ease: EI }, at("whats", -0.45));
tl.fromTo("#s1-count", { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.35, ease: B }, at("whats", -0.2));
["#wa1", "#wa2", "#wa3", "#wa4"].forEach((id, i) => {
  tl.fromTo(id, { opacity: 0, scale: 0.5, y: 60, rotation: i % 2 ? 6 : -5 }, { opacity: 1, scale: 1, y: 0, rotation: i % 2 ? 3 : -2, duration: 0.38, ease: B }, at("whats", -0.08 + i * 0.16));
});
["#ml1", "#ml2", "#ml3"].forEach((id, i) => {
  tl.fromTo(id, { opacity: 0, x: -260, rotation: -8 }, { opacity: 1, x: 0, rotation: i === 1 ? 2 : -3, duration: 0.42, ease: E }, at("email", -0.05 + i * 0.14));
});
[["#bp1", -0.15, -9], ["#bp2", 0.15, 7]].forEach(([id, o, r]) => {
  tl.fromTo(id, { opacity: 0, scale: 0.35, rotation: r * 3, y: 120 }, { opacity: 1, scale: 1, rotation: r, y: 0, duration: 0.42, ease: B }, at("photos", o));
  tl.fromTo(id + " .bp-img img", { filter: "blur(2px) brightness(.82) saturate(.75) sepia(.25)" }, { filter: "blur(11px) brightness(.82) saturate(.75) sepia(.25)", duration: 0.28, ease: "sine.inOut", yoyo: true, repeat: 3 }, at("photos", o + 0.1));
  tl.fromTo(id, { x: 0 }, { x: 6, duration: 0.05, yoyo: true, repeat: 5, ease: "none", immediateRender: false }, at("photos", o + 0.05));
});
tl.set("#s1-flash", { opacity: 0 }, 0);
tl.fromTo("#s1-flash", { opacity: 0.85 }, { opacity: 0, duration: 0.3, ease: "power2.out", immediateRender: false }, at("photos", -0.15));
tl.fromTo("#s1-flash", { opacity: 0.7 }, { opacity: 0, duration: 0.25, ease: "power2.out", immediateRender: false }, at("photos", 0.15));
tl.fromTo(".bp-tag", { opacity: 0, scale: 2 }, { opacity: 1, scale: 1, duration: 0.25, ease: "power4.in" }, at("photos", 0.55));
tl.to("#bp1", { x: -260, rotation: -16, duration: 0.4, ease: "power3.out" }, at("sacs", -0.25));
tl.to("#bp2", { x: 300, rotation: 14, duration: 0.4, ease: "power3.out" }, at("sacs", -0.25));
tl.fromTo("#bagwrap", { y: -1500, rotation: -12, opacity: 1, scale: 1.3 }, { y: 0, rotation: 0, scale: 1.3, duration: 0.55, ease: "power2.in" }, at("sacs", -0.4));
tl.fromTo("#bagwrap", { scaleY: 1, scaleX: 1, transformOrigin: "50% 100%" }, { scaleY: 0.86, scaleX: 1.08, duration: 0.08, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }, at("sacs", 0.15));
[[-310, -110, -38], [270, -150, 31], [-140, -230, -14], [350, -40, 52]].forEach(([x, y, r], i) => {
  tl.fromTo("#tk" + (i + 1), { x: 0, y: 70, rotation: (i % 2 ? 8 : -8), opacity: 1 }, { x, y, rotation: r, opacity: 1, duration: 0.5, ease: "power3.out" }, at("sacs", 0.22 + i * 0.07));
});
const counter = { v: 128 };
tl.to(counter, { v: 214, duration: at("cab") - at("whats"), ease: "none", onUpdate: () => { document.getElementById("s1-count").textContent = "+" + Math.round(counter.v) + " pièces"; } }, at("whats"));
tl.to("#s1-chaos", { scale: 1.08, duration: at("cab") - at("whats"), ease: "none" }, at("whats"));
tl.to("#s1-chaos", { y: 1100, rotation: 4, duration: 0.4, ease: "power3.in" }, at("cab", -0.45));
tl.to(["#s1-title", "#s1-count"], { opacity: 0, duration: 0.25 }, at("cab", -0.4));

/* S2 GRIND */
tl.fromTo("#s2-kicker", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.35, ease: E }, at("cab", -0.05));
tl.fromTo("#s2-sheet", { opacity: 0, x: 220, rotation: 4 }, { opacity: 1, x: 0, rotation: 1.5, duration: 0.55, ease: E }, at("cab", -0.15));
["saisit", "verifie", "relance"].forEach((k, i) => {
  tl.fromTo(["#v1", "#v2", "#v3"][i], { opacity: 0, x: -120, scale: 1.08 }, { opacity: 1, x: 0, scale: 1, duration: 0.3, ease: "expo.out" }, at(k, -0.12));
});
tl.to("#v1", { color: "rgba(19,35,28,.18)", duration: 0.25 }, at("verifie", -0.1));
tl.to("#v2", { color: "rgba(19,35,28,.18)", duration: 0.25 }, at("relance", -0.1));
tl.to("#v3", { color: "rgba(19,35,28,.18)", duration: 0.25 }, at("recommence", -0.3));
const lineGap = (at("recommence") - at("cab")) / 9;
["#l1", "#l2", "#l3", "#l4", "#l5", "#l6", "#l7", "#l8"].forEach((id, i) => {
  tl.fromTo(id, { opacity: 0, x: 30 }, { opacity: 1, x: 0, duration: 0.16, ease: E }, at("cab", 0.3 + i * lineGap));
});
tl.fromTo("#v4", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.35, ease: E }, at("recommence", -0.35));
tl.to("#s2-sheet", { x: 260, opacity: 0.35, duration: 0.4, ease: "power2.inOut" }, at("recommence", -0.5));
tl.fromTo("#s2-loop", { opacity: 0, scale: 0.3, rotation: -180 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.45, ease: B }, at("recommence", -0.2));
tl.to("#s2-loop", { rotation: -720, duration: 1.0, ease: "power2.inOut" }, at("recommence", 0.25));
tl.to(["#l8", "#l7", "#l6", "#l5", "#l4", "#l3", "#l2", "#l1"], { opacity: 0, x: -20, duration: 0.1, stagger: 0.06 }, at("recommence", 0.3));
tl.to("#s2", { opacity: 0, duration: 0.25 }, at("etsi", -0.3));

/* S3 QUESTION */
const stackPos = [[180, 640, -22], [560, 700, 14], [1300, 620, -9], [1560, 720, 18], [900, 760, -4]];
["#st1", "#st2", "#st3", "#st4", "#st5"].forEach((id, i) => {
  const [x, y, r] = stackPos[i];
  tl.fromTo(id, { x: x, y: y + 200, rotation: r, opacity: 0 }, { y: y, opacity: 0.85, duration: 0.55, ease: E }, at("etsi", -0.2 + i * 0.06));
  tl.to(id, { x: 1520, y: 150 - i * 7, rotation: (i - 2) * 1.2, duration: 0.7, ease: "power3.inOut" }, at("pret", -0.6 + i * 0.1));
});
tl.fromTo("#q1", { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 0.42, ease: E }, at("etsi", -0.1));
tl.fromTo("#q2", { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 0.42, ease: E }, at("avant", -0.15));
tl.fromTo("#q2 .pill", { scale: 0.6 }, { scale: 1, duration: 0.4, ease: B }, at("fscompta", -0.1));
tl.fromTo("#q3", { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 0.42, ease: E }, at("arrivait", -0.12));
tl.to("#s3-text", { scale: 1.04, duration: at("voici") - at("etsi"), ease: "none", transformOrigin: "0% 50%" }, at("etsi"));
tl.to(["#s3-text", "#s3-stack"], { opacity: 0, scale: 1.25, duration: 0.3, ease: "power2.in" }, at("voici", -0.3));

/* S4 LOGO */
const L0 = at("voici", -0.05);
tl.fromTo("#s4-flash", { opacity: 0.95 }, { opacity: 0, duration: 0.45, ease: "power2.out" }, L0);
tl.fromTo("#mk-page", { scale: 0.2, opacity: 0, transformOrigin: "50% 50%" }, { scale: 1, opacity: 1, duration: 0.4, ease: B }, L0);
tl.fromTo("#mk-fold", { opacity: 0, x: 8, y: -8 }, { opacity: 1, x: 0, y: 0, duration: 0.28, ease: E }, L0 + 0.22);
["#mk-b1", "#mk-b2", "#mk-b3"].forEach((id, i) => {
  tl.fromTo(id, { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: 0.28, ease: E }, L0 + 0.28 + i * 0.08);
});
tl.fromTo("#mk-arrow", { x: -30, opacity: 0 }, { x: 0, opacity: 1, duration: 0.32, ease: "back.out(2.5)" }, L0 + 0.52);
tl.fromTo("#s4-word", { opacity: 0, x: -50, clipPath: "inset(0 100% 0 0)" }, { opacity: 1, x: 0, clipPath: "inset(0 0% 0 0)", duration: 0.55, ease: "power3.out" }, at("brand", -0.15));
tl.fromTo("#s4-tag", { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.4, ease: E }, at("compagnon", -0.1));
tl.to("#s4-lock", { scale: 1.06, duration: at("client") - L0, ease: "none" }, L0);
tl.to("#s4-lock", { y: -60, opacity: 0, duration: 0.3, ease: "power2.in" }, at("client", -0.3));

/* S5 CLIENT */
tl.set(["#p-up1", "#p-up2", "#p-ar", "#toast", "#stcard", "#flashw", "#p-app", "#bd2", "#bd3", "#h5b", "#s5b", "#h5c", "#s5c"], { opacity: 0 }, 0);
tl.fromTo("#c5", { opacity: 0, y: -30 }, { opacity: 1, y: 0, duration: 0.35, ease: B }, at("client", -0.1));
tl.fromTo("#phone", { y: 900, rotation: 6 }, { y: 0, rotation: 0, duration: 0.7, ease: "expo.out" }, at("client", -0.2));
tl.fromTo("#h5a", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.42, ease: E }, at("application", -0.15));
tl.fromTo("#s5a", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.42, ease: E }, at("application", 0.2));
tl.fromTo("#app-ours", { scale: 1 }, { scale: 1.18, duration: 0.22, ease: "power2.out", yoyo: true, repeat: 1 }, at("telephone", -0.35));
tl.fromTo("#rp1", { scale: 0.2, opacity: 1 }, { scale: 1.6, opacity: 0, duration: 0.45, ease: "power2.out" }, at("telephone", -0.1));
tl.fromTo("#p-app", { opacity: 0, scale: 0.18, transformOrigin: "44% 30%" }, { opacity: 1, scale: 1, duration: 0.5, ease: "expo.out" }, at("telephone", 0.05));
tl.to("#home", { opacity: 0, duration: 0.25 }, at("telephone", 0.25));
tl.to(["#h5a", "#s5a"], { opacity: 0, y: -30, duration: 0.25, ease: "power2.in" }, at("photo", -0.6));
tl.fromTo("#h5b", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.4, ease: E }, at("photo", -0.35));
tl.fromTo("#s5b", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.4, ease: E }, at("photo", -0.05));
tl.fromTo("#p-up1", { opacity: 0, y: 200 }, { opacity: 1, y: 0, duration: 0.3, ease: E }, at("photo", -0.7));
tl.fromTo("#rp2", { scale: 0.2, opacity: 1 }, { scale: 1.6, opacity: 0, duration: 0.4, ease: "power2.out" }, at("photo", -0.12));
tl.fromTo("#flashw", { opacity: 0 }, { opacity: 1, duration: 0.05 }, at("photo", 0.0));
tl.to("#flashw", { opacity: 0, duration: 0.3 }, at("photo", 0.07));
tl.set("#p-up2", { opacity: 1 }, at("photo", 0.06));
tl.set("#p-app", { opacity: 0 }, at("photo", -0.38));
tl.set("#p-up1", { opacity: 0 }, at("photo", 0.08));
tl.to("#p-app", { opacity: 1, duration: 0.2 }, at("suit", -0.2));
tl.fromTo("#rp3", { scale: 0.2, opacity: 1 }, { scale: 1.6, opacity: 0, duration: 0.4, ease: "power2.out" }, at("envoyee", -0.25));
tl.fromTo("#toast", { opacity: 0, y: -60 }, { opacity: 1, y: 0, duration: 0.35, ease: B }, at("envoyee", -0.05));
tl.to(["#h5b", "#s5b"], { opacity: 0, y: -30, duration: 0.25, ease: "power2.in" }, at("suit", -0.35));
tl.fromTo("#h5c", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.4, ease: E }, at("suit", -0.15));
tl.fromTo("#s5c", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.4, ease: E }, at("suit", 0.2));
tl.to(["#p-up1", "#p-up2", "#toast"], { opacity: 0, duration: 0.25 }, at("suit", -0.2));
tl.fromTo("#stcard", { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1.04, duration: 0.35, ease: B }, at("suit", -0.1));
const sg = (at("arabe") - 0.9 - at("suit")) / 2;
tl.fromTo("#bd1", { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.28, ease: B }, at("suit", 0.1));
tl.to("#bd1", { opacity: 0, scale: 0.6, duration: 0.12 }, at("suit", 0.1 + sg));
tl.fromTo("#bd2", { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.28, ease: B, immediateRender: false }, at("suit", 0.2 + sg));
tl.to("#bd2", { opacity: 0, scale: 0.6, duration: 0.12 }, at("suit", 0.2 + 2 * sg));
tl.fromTo("#bd3", { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.28, ease: B, immediateRender: false }, at("suit", 0.3 + 2 * sg));
tl.to("#langflip", { rotationY: 90, duration: 0.22, ease: "power2.in" }, at("arabe", -0.3));
tl.set("#p-ar", { opacity: 1 }, at("arabe", -0.08));
tl.set(["#stcard", "#p-app"], { opacity: 0 }, at("arabe", -0.08));
tl.to("#langflip", { rotationY: 0, duration: 0.28, ease: "power2.out" }, at("arabe", -0.08));
tl.to("#phone", { x: 120, opacity: 0, duration: 0.3, ease: "power2.in" }, at("cabinet2", -0.35));
tl.to(["#h5c", "#s5c", "#c5"], { opacity: 0, x: -60, duration: 0.25, ease: "power2.in" }, at("cabinet2", -0.35));

/* S6 CABINET */
const S = 0.9375, WL = 210, WT = 110;
function cam(px, py, k, t, d, ease) {
  tl.to("#cam6", { x: 960 - (WL + px * S) * k, y: 560 - (WT + py * S) * k, scale: k, duration: d, ease: ease || "power3.inOut" }, t);
}
function place(el, r, pad) {
  const [x, y, w, h] = r;
  Object.assign(el.style, { left: (x - pad) * S + "px", top: (y - pad) * S + "px", width: (w + 2 * pad) * S + "px", height: (h + 2 * pad) * S + "px" });
}
function spot(wrapId, r, pad) {
  const el = document.createElement("div"); el.className = "spot"; document.getElementById(wrapId).appendChild(el); place(el, r, pad); return el;
}
function tag(wrapId, r, text, cls, dx) {
  const el = document.createElement("div"); el.className = "tag " + (cls || ""); el.textContent = text;
  el.style.left = (r[0] + r[2] + (dx || 14)) * S + "px"; el.style.top = (r[1] + r[3] / 2 - 21) * S + "px";
  document.getElementById(wrapId).appendChild(el); return el;
}
const nr = document.getElementById("newrow");
place(nr, RX.row0, 0);
nr.style.gridTemplateColumns = RX.cells.slice(1, 6).map((c) => c[1] * S + "px").join(" ");
nr.style.paddingLeft = RX.cells[0][1] * S + "px";
nr.style.fontSize = 14 * S + "px";
const C0 = at("cabinet2", -0.2);
tl.set(["#w-doc", "#w-entry", "#vwrap", "#dup", "#timer", "#fb-ext", "#stamp"], { opacity: 0 }, 0);
tl.fromTo("#c6", { opacity: 0, y: -30 }, { opacity: 1, y: 0, duration: 0.35, ease: B }, C0 + 0.1);
tl.fromTo("#w-list", { x: 1400, rotation: 3 }, { x: 0, rotation: 0, duration: 0.6, ease: "expo.out" }, C0);
tl.fromTo("#newrow", { opacity: 0, y: -40 }, { opacity: 1, y: 0, duration: 0.35, ease: B }, at("facture2", -0.1));
const rowCx = RX.row0[0] + RX.row0[2] * 0.45, rowCy = RX.row0[1] + 30;
cam(rowCx, rowCy, 1.7, at("facture2", 0.0), 0.8);
tl.fromTo("#timer", { opacity: 0, y: -20 }, { opacity: 1, y: 0, duration: 0.3, ease: E }, at("lue", -0.2));
const tv = { v: 0 };
const tvDur = Math.max(0.8, at("fournisseur") - at("lue") - 0.4);
tl.fromTo(tv, { v: 0 }, { v: 3.8, duration: tvDur, ease: "power1.out", onUpdate: () => { document.querySelector("#timer .mono").textContent = tv.v.toFixed(1).replace(".", ",") + " s"; } }, at("lue"));
tl.to("#fb-proc", { opacity: 0, duration: 0.1 }, at("lue", tvDur));
tl.fromTo("#fb-ext", { opacity: 0, scale: 1.6 }, { opacity: 1, scale: 1, duration: 0.28, ease: B, immediateRender: false }, at("lue", tvDur + 0.02));
tl.to("#timer", { opacity: 0, duration: 0.25 }, at("ice", 0.2));
const D0 = at("fournisseur", -0.35);
tl.to("#w-list", { opacity: 0, duration: 0.22 }, D0);
tl.fromTo("#w-doc", { opacity: 0 }, { opacity: 1, duration: 0.22, immediateRender: false }, D0);
tl.set("#cam6", { x: 960 - (WL + 540 * S) * 1.5, y: 560 - (WT + 300 * S) * 1.5, scale: 1.5 }, D0);
cam(RX.four[0] + 230, RX.four[1] + 60, 1.7, D0 + 0.02, 0.5);
const sp = { four: spot("wrap-doc", [RX.four[0], RX.four[1], 250, RX.four[3]], 8), ice: spot("wrap-doc", RX.ice, 8), taux: spot("wrap-doc", RX.taux, 8), check: spot("wrap-doc", [RX.check[0], RX.check[1], 300, RX.check[3]], 8) };
const tg = { four: tag("wrap-doc", [RX.four[0], RX.four[1], 250, RX.four[3]], "Fournisseur reconnu", "terra"), ice: tag("wrap-doc", RX.ice, "ICE contrôlé ✓", "teal"), taux: tag("wrap-doc", RX.taux, "2 taux · 10 % + 20 %", "terra", 20), check: tag("wrap-doc", [RX.check[0], RX.check[1], 300, RX.check[3]], "HT + TVA = TTC ✓", "teal") };
Object.values(sp).concat(Object.values(tg)).forEach((el) => tl.set(el, { opacity: 0 }, 0));
const show = (k, t, hide) => {
  tl.fromTo(sp[k], { opacity: 0 }, { opacity: 1, duration: 0.25, ease: E, immediateRender: false }, t);
  tl.fromTo(tg[k], { opacity: 0, x: -16 }, { opacity: 1, x: 0, duration: 0.28, ease: E, immediateRender: false }, t + 0.05);
  tl.to([sp[k], tg[k]], { opacity: 0, duration: 0.2 }, hide);
};
show("four", at("fournisseur", -0.05), at("ice", -0.15));
show("ice", at("ice", -0.05), at("ht", -0.35));
cam(RX.taux[0] + 280, RX.taux[1] + 60, 1.55, at("ht", -0.45), 0.6);
show("taux", at("ht", -0.05), at("doublons", -0.2));
tl.fromTo("#dup", { opacity: 0, x: 120 }, { opacity: 1, x: 0, duration: 0.4, ease: B }, at("doublons", -0.1));
tl.fromTo("#dup", { rotation: 0 }, { rotation: 1.5, duration: 0.06, yoyo: true, repeat: 5, immediateRender: false }, at("bloques", -0.05));
tl.to("#dup", { opacity: 0, x: 120, duration: 0.28 }, at("montants", -0.15));
cam(RX.check[0] + 250, RX.check[1], 1.7, at("montants", -0.35), 0.5);
show("check", at("montants", -0.05), at("ecriture", -0.25));
const N0 = at("ecriture", -0.25);
tl.to("#w-doc", { opacity: 0, duration: 0.25 }, N0);
tl.fromTo("#w-entry", { opacity: 0 }, { opacity: 1, duration: 0.25, immediateRender: false }, N0);
tl.set("#cam6", { x: 960 - (WL + 830 * S) * 1.0, y: 560 - (WT + 520 * S) * 1.0, scale: 1.0 }, N0);
cam(900, 520, 1.15, N0 + 0.05, 1.0);
const rs = ["r1", "r2", "r3"].map((k) => spot("wrap-entry", RX[k], 2));
const eqs = spot("wrap-entry", RX.eq, 2);
const cg = tag("wrap-entry", [RX.r1[0] + 900, RX.table[1] - 46, 0, 40], "Plan comptable CGNC", "");
const eqt = tag("wrap-entry", [RX.eq[0] + 120, RX.eq[1] + RX.eq[3] + 8, 0, 44], "Débit = Crédit · 11 142,00", "teal");
[...rs, eqs, cg, eqt].forEach((el) => tl.set(el, { opacity: 0 }, 0));
const rowStep = (at("valider") - 0.6 - at("ecriture")) / 4;
rs.forEach((el, i) => {
  tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: 0.2, immediateRender: false }, at("ecriture", 0.2 + i * rowStep));
  tl.to(el, { opacity: 0, duration: 0.15 }, at("ecriture", 0.2 + (i + 1) * rowStep));
});
tl.fromTo(cg, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.3, ease: B, immediateRender: false }, at("plan", -0.05));
tl.fromTo(eqs, { opacity: 0 }, { opacity: 1, duration: 0.2, immediateRender: false }, at("ecriture", 0.2 + 3 * rowStep));
tl.fromTo(eqt, { opacity: 0, scale: 0.7 }, { opacity: 1, scale: 1, duration: 0.3, ease: B, immediateRender: false }, at("ecriture", 0.25 + 3 * rowStep));
const V0 = at("valider", -0.75);
tl.to("#cam6", { opacity: 0.16, scale: 1.1, duration: 0.35, ease: "power2.inOut" }, V0);
tl.to("#c6", { opacity: 0, duration: 0.25 }, V0);
tl.fromTo("#vwrap", { opacity: 0 }, { opacity: 1, duration: 0.25, immediateRender: false }, V0 + 0.1);
tl.fromTo("#validate-btn", { scale: 0.7 }, { scale: 1, duration: 0.4, ease: B }, V0 + 0.1);
tl.fromTo("#cur6", { x: 1500, y: 900, opacity: 0 }, { x: 1210, y: 520, opacity: 1, duration: 0.55, ease: "power3.out" }, V0 + 0.15);
tl.to("#validate-btn", { scale: 0.93, duration: 0.07, ease: "power2.out" }, at("valider", -0.05));
tl.to("#validate-btn", { scale: 1.0, backgroundColor: "#16a34a", duration: 0.3, ease: B }, at("valider", 0.03));
tl.fromTo("#stamp", { opacity: 0, scale: 2.2, rotation: -8 }, { opacity: 1, scale: 1, rotation: -4, duration: 0.28, ease: "power4.in", immediateRender: false }, at("valider", 0.15));
tl.to("#cur6", { opacity: 0, duration: 0.25 }, at("valider", 0.6));
tl.to("#vwrap", { scale: 0.32, y: 30, opacity: 0, duration: 0.45, ease: "power3.inOut" }, at("suit2", -0.45));

/* S7 MOSAIC */
tl.fromTo("#s7-head", { opacity: 0, y: -30 }, { opacity: 1, y: 0, duration: 0.4, ease: E }, at("suit2", -0.05));
["#t1", "#t2", "#t3", "#t4", "#t5"].forEach((id, i) => {
  tl.fromTo(id, { opacity: 0, y: 80, scale: 0.85 }, { opacity: 1, y: 0, scale: 1, duration: 0.45, ease: E }, at("suit2", -0.15 + i * 0.07));
  tl.set(id + " .tlab", { opacity: 0 }, 0);
});
const tileK = ["decl", "ventes", "relances", "echanges", "equipe"];
["#t1", "#t2", "#t3", "#t4", "#t5"].forEach((id, i) => {
  const t = at(tileK[i], -0.08);
  tl.to(id, { y: -14, scale: 1.04, boxShadow: "0 50px 100px rgba(19,35,28,.32), 0 0 0 4px #C8694A", duration: 0.26, ease: B }, t);
  tl.fromTo(id + " .tlab", { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.26, ease: B, immediateRender: false }, t + 0.04);
  tl.to(id + " img", { y: -60, duration: 1.4, ease: "power1.inOut" }, t);
  if (i < 4) tl.to(id, { y: 0, scale: 1, boxShadow: "0 30px 70px rgba(19,35,28,.2), 0 0 0 1px rgba(19,35,28,.08)", duration: 0.3, ease: E }, at(tileK[i + 1], -0.15));
});
tl.to("#s7", { opacity: 0, duration: 0.25 }, at("ensuite", -0.3));

/* S8 BRIDGE */
tl.fromTo("#s8-head", { opacity: 0, y: -20 }, { opacity: 1, y: 0, duration: 0.35, ease: E }, at("ensuite", -0.1));
tl.fromTo("#n-left", { opacity: 0, x: -120 }, { opacity: 1, x: 0, duration: 0.45, ease: E }, at("ensuite", -0.15));
tl.fromTo("#n-right", { opacity: 0, x: 120 }, { opacity: 1, x: 0, duration: 0.45, ease: E }, at("fscompta2", -0.15));
tl.to("#s8-path", { strokeDashoffset: 0, duration: 0.6, ease: "power2.inOut" }, at("recupere", -0.2));
tl.fromTo("#s8-head-ar", { opacity: 0 }, { opacity: 1, duration: 0.2 }, at("recupere", 0.4));
const flowStep = Math.max(0.35, (at("ressaisie") - at("recupere") - 0.6) / 4);
["#f1", "#f2", "#f3", "#f4"].forEach((id, i) => {
  const t0 = at("recupere", 0.2 + i * flowStep);
  tl.fromTo(id, { x: 560, y: 470, opacity: 0, scale: 0.8 }, { x: 870, y: 395, opacity: 1, scale: 1, duration: 0.5, ease: "power2.out" }, t0);
  tl.to(id, { x: 1220, y: 470, opacity: 0, scale: 0.8, duration: 0.5, ease: "power2.in" }, t0 + 0.5);
});
(function () {
  const host = document.getElementById("dots");
  const P = (u) => { const a = [600, 510], b = [820, 430], c = [1100, 430], d = [1320, 510]; const m = 1 - u; return [m*m*m*a[0] + 3*m*m*u*b[0] + 3*m*u*u*c[0] + u*u*u*d[0], m*m*m*a[1] + 3*m*m*u*b[1] + 3*m*u*u*c[1] + u*u*u*d[1]]; };
  const n = Math.max(8, Math.floor((at("reserve") - at("recupere")) / 0.17));
  for (let k = 0; k < n; k++) {
    const el = document.createElement("div"); el.className = "dot"; host.appendChild(el);
    const st = { u: 0 };
    tl.set(el, { opacity: 0 }, 0);
    tl.to(st, { u: 1, duration: 0.9, ease: "none", onUpdate: () => { const [x, y] = P(st.u); gsap.set(el, { x, y, opacity: Math.sin(st.u * Math.PI) }); } }, at("recupere", 0.3 + k * 0.17));
  }
})();
tl.fromTo("#n-right", { boxShadow: "0 0 0 0 rgba(200,105,74,0)" }, { boxShadow: "0 0 0 14px rgba(200,105,74,.35)", duration: 0.25, yoyo: true, repeat: 5, immediateRender: false }, at("pieces"));
tl.fromTo("#s8-st", { opacity: 0, scale: 2.0, rotation: -6 }, { opacity: 1, scale: 1, rotation: -2, duration: 0.28, ease: "power4.in" }, at("ressaisie", -0.2));
tl.to("#s8", { opacity: 0, duration: 0.3 }, at("reserve", -0.3));

/* S9 OUTRO */
tl.fromTo("#r1", { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 0.4, ease: E }, at("reserve", -0.1));
tl.fromTo("#r2", { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 0.4, ease: E }, at("valide", -0.45));
tl.fromTo("#r3", { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 0.4, ease: E }, at("recoit", -0.7));
tl.fromTo("#r3 .pill9", { scale: 0.6 }, { scale: 1, duration: 0.4, ease: B }, at("recoit", -0.6));
tl.to("#s9-r", { opacity: 0, y: -80, duration: 0.35, ease: "power2.in" }, at("prochaine", -0.4));
tl.fromTo("#o1", { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 0.45, ease: E }, at("prochaine", -0.15));
tl.fromTo("#o2", { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 0.45, ease: E }, at("besoin", -0.15));
tl.to(["#s9-a"], { opacity: 0, y: -80, duration: 0.35, ease: "power2.in" }, at("brand", -0.35));
tl.set(["#s9-row", "#s9-offer", "#s9-url", "#s9-tag"], { opacity: 0 }, 0);
tl.fromTo("#s9-row", { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.5, ease: B, immediateRender: false }, at("brand", -0.1));
tl.fromTo("#s9-offer", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.4, ease: E, immediateRender: false }, at("contact", 0.3));
tl.fromTo("#s9-url", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.4, ease: B, immediateRender: false }, at("contact", 0.0));
tl.fromTo("#s9-tag", { opacity: 0 }, { opacity: 1, duration: 0.5, immediateRender: false }, at("contact", 0.8));
tl.to("#s9-lock", { scale: 1.03, duration: T.dur - at("contact"), ease: "none" }, at("contact"));
tl.fromTo("#fadeout", { opacity: 0 }, { opacity: 1, duration: 0.6, ease: "power1.in" }, T.dur - 0.7);

window.__timelines["main"] = tl;
