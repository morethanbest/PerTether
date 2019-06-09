
'use strict';

const setup = require('./setup/setup');
const account = require('./util/account');
const util = require('./util/util');
const winston = require('winston');
const contract = require('./transaction/contractInfo');
const client = require('./transaction/clientControl');
const dataAnalysis = require('./dataAnalysis/processData');
const path = require('path');
const fs1 = require('fs');

let configFile;

function setConfig(file) {
    configFile = file;
}

async function run() {
    let program = require('commander');
    program.version('0.1')
        .option('-c, --config <file>', 'config file of the benchmark, default is config.json', setConfig)
        .parse(process.argv);
    const fs = require('fs-extra');
    let absConfigFile;
    if(typeof configFile === 'undefined') {
        absConfigFile = path.join(__dirname, '..', 'config.json');
    }
    else {
        absConfigFile = path.isAbsolute(configFile) ? configFile : path.join(__dirname, '..', configFile);
    }
    if(!fs.existsSync(absConfigFile)) {
        winston.error('file ' + absConfigFile + ' does not exist');
        return;
    }
    let absConfigObject = require(absConfigFile);
    winston.info(absConfigObject);
    let difficulties = absConfigObject.difficulty;
    let gasLimits = absConfigObject.gasLimit;
    let clientType = absConfigObject.clientType;
    let startRate = absConfigObject.startTps;
    let finishRate = absConfigObject.finishTps;
    let duration = absConfigObject.duration;
    let smartContract = absConfigObject.smartContract;

    //start and stop docker
    winston.info('PerTether starts a new test task.');
    let configObject = util.parseYaml('config/config.yml');
    let tFinalResult = {
        timestamp: Date.now(),
        difficulty: difficulties,
        gasLimit: gasLimits,
        nodeCount: 2,
        startUpType: "docker",
        clientType: clientType,
        result: []
    };
    for (let i = 0; i < difficulties.length; i++) {
        for (let j = 0; j < gasLimits.length; j++) {
            setup.writeGenesis(clientType, difficulties[i], gasLimits[j], configObject.nodes.length);
            let startStatus = await setup.startTestChain(clientType);
            if (startStatus !== 0) {
                winston.error('Blockchain started failed.');
                return;
            }
            await util.sleep(5000);
            await setup.start(configObject);
            let nodeCount = configObject.nodes.length;

            client.startClients(nodeCount);

            // let testConfig = configObject.tests;
            let rate = startRate;
            // let rate = testConfig.startRate;
            // let finishRate = testConfig.finishRate;
            // let duration = testConfig.duration;
            let eachClientRate = rate / nodeCount;
            let finalResult = {
                difficulty: difficulties[i],
                gasLimit: gasLimits[j],
                throughput: [],
                latency:[],
                txCompeltion: [],
                // gasCompletion: [],
                detailedLatency: []

            };
            while (eachClientRate <= finishRate / nodeCount) {
                let results = [];
                await client.startTest(configObject.nodes, account.getAccounts(), eachClientRate, duration, contract.getContractConfig(smartContract), results);
                let data = dataAnalysis.processResult(results);
                winston.info(`Result rate ${eachClientRate * nodeCount} ${data}`);
                finalResult.throughput.push(data.throughput);
                finalResult.latency.push(data.latency);
                finalResult.txCompeltion.push(data.gasCompletion);
                // finalResult.gasCompletion.push(data.gasCompletion);
                finalResult.detailedLatency.push(data.gasLatency);
                eachClientRate *= 2;
            }
            client.stop();
            winston.info(`##########Round Final Result##########`);
            winston.info(finalResult);
            tFinalResult.result.push(finalResult);
            let stopStatus = await setup.stopTestChain(clientType);
            if (stopStatus !== 0)
                winston.error('Docker stopped failed. Please stop manually.');
        }
    }
    winston.info(`##########True Final Result##########`);
    let tFinalResultStr = JSON.stringify(tFinalResult);
    winston.info(tFinalResultStr);
    fs1.writeFileSync(`result.json`, tFinalResultStr);

}

(async () => {
    try {
        await run();
    } catch (err) {
        winston.error(`Error while executing the task: ${err.stack ? err.stack : err}`);
    }
})();
