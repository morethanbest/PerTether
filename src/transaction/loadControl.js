
'use strict';

const clientControl = require('./clientControl');
const winston = require('winston');

function startLoadTimer(loadConfig) {
    let period = loadConfig.period;
    let doubleTimes = loadConfig.doubleTimes;
    let index = 2;
    for (let i = 1; i < doubleTimes; i++) {
        setTimeout(clientControl.controlRateIndex, i * period * 1000, index);
        index *= 2;
    }
}

module.exports.startLoadTimer = startLoadTimer;
