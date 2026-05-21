const fs = require('fs');
const path = require('path');

const fontPath = path.join(__dirname, '../fonts/inter-latin.woff2');
const b64 = fs.readFileSync(fontPath).toString('base64');

const FONT_FACE = `
  @font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 100 900;
    src: url('data:font/woff2;base64,${b64}') format('woff2');
  }
`;

module.exports = { FONT_FACE };
