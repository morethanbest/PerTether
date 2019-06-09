
'use strict';

const winston = require('winston');

function processResult(result){
    let txSuccess = 0;
    let txTotal = 0;
    let latencyTotal = 0;
    let rate = result[0].rate * result.length;
    let duration = result[0].duration;
    let durationMs = duration * 1000;
    let maxGasprice = 20;
    let gasCompletion = [];
    let gasLatency = [];
    let gasTotal = [];
    for (let i = 0; i <= maxGasprice; i += 2) {
        gasCompletion.push([rate, i, 0]);
        gasLatency.push([rate, i, 0]);
        gasTotal.push([0,0,0])
    }
    for(let i = 0; i < result.length; i++){
        winston.info(`Process ${result[i].node}`);
        let res = result[i].result;
        winston.info(`Result ${JSON.stringify(res)}`);
        for(let j = 0; j < res.length; j++){
            txTotal ++;
            let gasBucket = parseInt(res[j].gasprice / 2);
            if (gasBucket > maxGasprice / 2) gasBucket = maxGasprice / 2;
            gasTotal[gasBucket][0]++;
            if(res[j].status === 0 && res[j].finishTime - res[0].finishTime < durationMs) {
                gasTotal[gasBucket][2] += res[j].latency;
                latencyTotal += res[j].latency;
                txSuccess++;
                gasTotal[gasBucket][1]++;
            }
        }
    }
    for (let i = 0; i < gasTotal.length; i++) {
        if(gasTotal[i][0] === 0){
            gasLatency[i][2] = 0;
            gasCompletion[i][2] = 0;
        } else {
            gasLatency[i][2] = gasTotal[i][2] / (gasTotal[i][1] * 1000);
            gasCompletion[i][2] = gasTotal[i][1] / gasTotal[i][0];
        }
    }
    winston.info(`Test rate ${rate}, duration ${duration}. Total tx ${txTotal}, success tx ${txSuccess}.`);
    let throughput = txSuccess / duration;
    let latency = latencyTotal / (txSuccess * 1000);
    let txCompletion = txSuccess / txTotal;
    winston.info(`Throughput ${throughput}, latency ${latency}, txCompletion ${txCompletion}.`);
    return {
        throughput: [rate, throughput],
        latency: [rate, latency],
        txCompletion: [rate, txCompletion],
        gasCompletion: gasCompletion,
        gasLatency: gasLatency
    }
}

module.exports.processResult = processResult;
