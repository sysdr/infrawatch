#!/usr/bin/env node
'use strict';
const path = require('path');
const fs = require('fs');
const target = path.join(__dirname, '../node_modules/detect-port-alt/lib/detect-port.js');
if (!fs.existsSync(target)) return;
let code = fs.readFileSync(target, 'utf8');
if (code.includes("(typeof d === 'function'")) return;
const bad = "const debug = require('debug')('detect-port');";
const good = `let debug;
try {
  const d = require('debug');
  debug = (typeof d === 'function' ? d : (d && typeof d.default === 'function' ? d.default : function () {}))('detect-port');
} catch (e) {
  debug = function () {};
}`;
if (code.includes(bad)) {
  code = code.replace(bad, good);
  fs.writeFileSync(target, code);
  console.log('Applied detect-port-alt patch.');
}
