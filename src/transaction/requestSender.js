
'use strict';

const winston = require('winston');
const Web3 = require('web3');
const util = require('../util/util');
const invoke = require('../adapter/invoke-smart-contract');
const gasControl = require('./gasControl');
const path = require('path');

const rootDir = path.join('..', '..');
let web3Proxy;
let nodeAccounts;
let txNum = 0;

async function doTest(msg){
    return await runTest(msg.nodeName, msg.accounts, msg.proxy, msg.rate, msg.duration, msg.contractConfig);
}

async function runTest(nodeName, accounts, proxy, rate, duration, contractConfig) {
    winston.info(`${nodeName}: Request client ${nodeName} started. Rate ${rate}.`);
    winston.info(contractConfig.abi);
    web3Proxy = new Web3(Web3.providers.HttpProvider(proxy));
    let promises = [];
    winston.info(`${nodeName}: Unlock accounts for ${nodeName}.`);
    nodeAccounts = accounts;
    accounts.forEach((item, index) => {
        promises.push(web3Proxy.eth.personal.unlockAccount(item[0], item[1], 100));
    });
    await Promise.all(promises);
    let startTime = Date.now();
    winston.info(`${nodeName}: Start ${startTime} finish ${startTime + duration * 1000}.`);
    let results = await sendRequests(startTime, nodeName, web3Proxy, rate, duration, contractConfig.address, contractConfig.abi, contractConfig.workload);
    winston.info(`${nodeName}: Request rate ${rate}. Results ${results}.`);
    txNum = 0;
    return {
        rate: rate,
        node: nodeName,
        duration: duration,
        startTime: startTime,
        finishTime: startTime + duration * 1000,
        result: results
    };
}

async function sendRequests(startTime, nodeName, web3, rate, duration, address, abi, contractWorkloadPath) {
    winston.info(`${nodeName}:start time ${startTime}`);
    const workloadGeneration = require(path.join(rootDir, contractWorkloadPath));
    let promises = [];
    let sleepTime = 1000 / rate;
    winston.info(`${nodeName}:sleep time ${sleepTime}`);
    while ((Date.now() - startTime)/1000 < duration){
        let account = getRandomAccount();
        // winston.info(`${nodeName}:Send TX account ${account[0]}`);
        let workload = workloadGeneration.run();
        // winston.info(`${nodeName}:Func ${workload.func}, Param ${workload.param}`);
        let func;
        for (let i = 0; i < abi.length; i++) {
            if (abi[i].name === workload.func) {
                func = abi[i];
                break;
            }
        }
        let gasprice = gasControl.getNumberInNormalDistribution(12, 4);
        while(gasprice <= 1) gasprice++;
        // winston.info(`${nodeName}:Func ${func}, Param ${workload.param}`);
        promises.push(invoke.submitTransaction(nodeName, web3, address, func, account[0], account[1], gasprice, workload.param));
        txNum += 1;
        await rateControl(sleepTime, Date.now(), startTime);
    }
    return await Promise.all(promises);
}

async function rateControl(sleepTime, nowDate, startTime) {
    let diff = txNum * sleepTime - (nowDate - startTime);
    if( diff > 5) {
        return util.sleep(diff);
    }
    else {
        return Promise.resolve();
    }
}

function getRandomAccount() {
    let index = Math.floor(Math.random() * nodeAccounts.length);
    return nodeAccounts[index];
}

process.on('message', async (message) => {
    if (!message.hasOwnProperty('type')) {
        process.send({type: 'error', data: 'unknown message type'});
        return;
    }

    try {
        switch (message.type) {
            case 'test': {
                let results = await doTest(message);
                await util.sleep(200);
                process.send({type: 'testResult', data: results});
                break;
            }
            default: {
                process.send({type: 'error', data: 'unknown message type'});
            }
        }
    }
    catch (err) {
        process.send({type: 'error', data: err.toString()});
    }
});

module.exports.doTest = doTest;
