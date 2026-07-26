// ============================================================
//  DEVOTIONAL EMBLEMS — filled, layered, glowing sanctum art
//  Each emblem is drawn to sit inside the gopuram niche.
//  viewBox 0 0 120 120. Fills, not hairlines.
// ============================================================

const EMBLEMS = {
  // PERUMAL / VISHNU — the Vaishnavite thiruman (namam) flanked by shanku & chakra
  perumal: `
  <g class="em">
    <circle cx="60" cy="58" r="40" class="halo"/>
    <g transform="translate(24,50)">
      <circle r="13" class="gold-fill"/>
      <circle r="8.5" class="niche-fill"/>
      <g class="gold-fill">
        <circle cx="0" cy="-11.5" r="2"/><circle cx="8.1" cy="-8.1" r="2"/><circle cx="11.5" cy="0" r="2"/>
        <circle cx="8.1" cy="8.1" r="2"/><circle cx="0" cy="11.5" r="2"/><circle cx="-8.1" cy="8.1" r="2"/>
        <circle cx="-11.5" cy="0" r="2"/><circle cx="-8.1" cy="-8.1" r="2"/>
      </g>
      <circle r="3" class="gold-fill"/>
    </g>
    <g transform="translate(96,50)">
      <path d="M-3 -14 C7 -12 10 2 5 12 C2 17 -6 17 -8 11 C-10 5 -7 -2 -3 -14Z" class="gold-fill"/>
      <path d="M-3 -14 C0 -6 0 4 -1 11" class="niche-stroke"/>
      <ellipse cx="-6" cy="13" rx="6" ry="2.6" class="gold-fill"/>
    </g>
    <path d="M60 96 L44 40 Q60 30 76 40 Z" class="gold-fill"/>
    <path d="M60 90 L50 44 Q60 38 70 44 Z" class="niche-fill"/>
    <path d="M60 88 L56 46 Q60 43 64 46 Z" class="accent-red"/>
    <circle cx="60" cy="34" r="3.4" class="gold-fill"/>
  </g>`,

  shiva: `
  <g class="em">
    <circle cx="60" cy="58" r="40" class="halo"/>
    <ellipse cx="60" cy="92" rx="34" ry="9" class="gold-fill"/>
    <ellipse cx="60" cy="90" rx="26" ry="6" class="niche-fill"/>
    <path d="M46 88 Q46 54 60 46 Q74 54 74 88 Z" class="gold-fill"/>
    <path d="M52 88 Q52 58 60 52 Q68 58 68 88 Z" class="niche-fill"/>
    <g class="accent-red">
      <rect x="52" y="66" width="16" height="3" rx="1.5"/>
      <rect x="52" y="73" width="16" height="3" rx="1.5"/>
      <rect x="52" y="80" width="16" height="3" rx="1.5"/>
    </g>
    <path d="M44 40 A20 20 0 0 0 76 40 A15 15 0 0 1 44 40Z" class="gold-fill"/>
    <circle cx="60" cy="30" r="3" class="gold-fill"/>
  </g>`,

  amman: `
  <g class="em">
    <circle cx="60" cy="58" r="40" class="halo"/>
    <g class="gold-fill">
      <ellipse cx="60" cy="34" rx="12" ry="20"/>
      <ellipse cx="60" cy="34" rx="12" ry="20" transform="rotate(72 60 58)"/>
      <ellipse cx="60" cy="34" rx="12" ry="20" transform="rotate(144 60 58)"/>
      <ellipse cx="60" cy="34" rx="12" ry="20" transform="rotate(216 60 58)"/>
      <ellipse cx="60" cy="34" rx="12" ry="20" transform="rotate(288 60 58)"/>
    </g>
    <g class="accent-red">
      <ellipse cx="60" cy="42" rx="6" ry="11"/>
      <ellipse cx="60" cy="42" rx="6" ry="11" transform="rotate(72 60 58)"/>
      <ellipse cx="60" cy="42" rx="6" ry="11" transform="rotate(144 60 58)"/>
      <ellipse cx="60" cy="42" rx="6" ry="11" transform="rotate(216 60 58)"/>
      <ellipse cx="60" cy="42" rx="6" ry="11" transform="rotate(288 60 58)"/>
    </g>
    <line x1="60" y1="58" x2="60" y2="92" class="gold-stroke"/>
    <circle cx="60" cy="58" r="6" class="gold-fill"/>
    <circle cx="60" cy="92" r="4" class="gold-fill"/>
  </g>`,

  "full-moon": `
  <g class="em">
    <circle cx="60" cy="58" r="42" class="halo"/>
    <circle cx="60" cy="58" r="34" class="gold-fill"/>
    <g class="accent-soft">
      <circle cx="48" cy="48" r="6"/><circle cx="70" cy="52" r="4.5"/>
      <circle cx="64" cy="70" r="7"/><circle cx="50" cy="66" r="3.5"/>
    </g>
  </g>`,

  "new-moon": `
  <g class="em">
    <circle cx="60" cy="58" r="40" class="halo"/>
    <circle cx="60" cy="58" r="32" class="gold-ring"/>
    <circle cx="60" cy="58" r="27" class="niche-fill"/>
    <g class="gold-fill">
      <path d="M40 96 q6 -7 12 0 z"/><path d="M68 96 q6 -7 12 0 z"/>
    </g>
  </g>`,

  lamp: `
  <g class="em">
    <circle cx="60" cy="58" r="40" class="halo"/>
    <path d="M32 74 Q60 92 88 74 L82 84 Q60 98 38 84 Z" class="gold-fill"/>
    <g class="gold-fill">
      <path d="M60 70 Q54 58 60 44 Q66 58 60 70Z"/>
      <path d="M44 72 Q40 62 45 52 Q50 62 44 72Z"/>
      <path d="M76 72 Q72 62 75 52 Q81 62 76 72Z"/>
      <path d="M34 78 Q31 70 35 62 Q40 70 34 78Z"/>
      <path d="M86 78 Q83 70 85 62 Q90 70 86 78Z"/>
      <path d="M60 68 Q57 60 60 54 Q63 60 60 68Z" class="accent-red"/>
    </g>
  </g>`,

  vel: `
  <g class="em">
    <circle cx="60" cy="58" r="40" class="halo"/>
    <path d="M60 14 Q48 40 60 58 Q72 40 60 14Z" class="gold-fill"/>
    <path d="M60 22 Q54 40 60 54 Q66 40 60 22Z" class="niche-fill"/>
    <line x1="60" y1="58" x2="60" y2="104" class="gold-stroke-thick"/>
    <path d="M44 60 Q60 68 76 60" class="gold-stroke-thick"/>
  </g>`,

  modak: `
  <g class="em">
    <circle cx="60" cy="58" r="40" class="halo"/>
    <path d="M60 30 Q36 34 34 62 Q33 82 60 92 Q87 82 86 62 Q84 34 60 30Z" class="gold-fill"/>
    <path d="M60 38 Q44 42 43 62 Q43 76 60 84 Q77 76 77 62 Q76 42 60 38Z" class="accent-soft"/>
    <path d="M60 30 Q54 22 60 16 Q66 22 60 30Z" class="gold-fill"/>
    <circle cx="60" cy="62" r="7" class="gold-fill"/>
  </g>`,

  river: `
  <g class="em">
    <circle cx="60" cy="44" r="34" class="halo"/>
    <circle cx="60" cy="40" r="15" class="gold-fill"/>
    <g class="gold-stroke-river">
      <path d="M20 66 Q40 56 60 66 T100 66"/>
      <path d="M20 80 Q40 70 60 80 T100 80"/>
      <path d="M20 94 Q40 84 60 94 T100 94"/>
    </g>
  </g>`,

  generic: `
  <g class="em">
    <circle cx="60" cy="58" r="34" class="halo"/>
    <path d="M34 70 Q60 86 86 70 L80 80 Q60 92 40 80 Z" class="gold-fill"/>
    <path d="M60 68 Q52 58 60 44 Q68 58 60 68Z" class="gold-fill"/>
    <path d="M60 64 Q56 57 60 50 Q64 57 60 64Z" class="accent-red"/>
  </g>`
};

function emblemSvg(name) {
  const body = EMBLEMS[name] || EMBLEMS.generic;
  return `<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" class="emblem-svg">${body}</svg>`;
}
