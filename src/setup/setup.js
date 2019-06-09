
'use strict';

const winston = require('winston');
const dockerCompose = require('docker-compose');
const path = require('path');
const install = require('../adapter/install-smart-contract');
const util = require('../util/util');
const contractInfo = require('../transaction/contractInfo');
const providers = require('../util/providers');
const fs = require('fs');

module.exports.startTestChain = async function startTestChain(client) {
    winston.info(`Start test blockchain, client type: ${client} ...`);
    if (client === 'Geth') {
        let result = await dockerCompose.upAll({cwd: path.join(__dirname, 'geth', 'docker'), log: true});
        return result.exitCode;
    }
    winston.error(`No ${client} client supported.`);
    return 1;
};


module.exports.stopTestChain = async function stopTestChain(client) {
    winston.info(`Stop test blockchain, client type: ${client} ...`);
    if (client === 'Geth') {
        let result = await dockerCompose.down({cwd: path.join(__dirname, 'geth', 'docker'), log: true});
        return result.exitCode;
    }
    winston.error(`No ${client} client supported.`);
    return 1;
};

module.exports.start = async function (configObject) {
    let nodesConfig = configObject.nodes;
    await providers.initProviders(nodesConfig);
    let contract = await install.run(nodesConfig[0].nodeName, configObject.contracts[0].path, configObject.contracts[0].name);
    contractInfo.newContract(configObject.contracts[0], contract);
};

module.exports.writeGenesis = function (client, difficulty, gasLimit, nodeCount) {
    if (client === 'Geth') {
        let genesis = require(path.join(__dirname, '../../config/geth/genesis.json'));
        genesis.difficulty = difficulty;
        genesis.gasLimit = gasLimit.toString();
        let gstr = JSON.stringify(genesis);
        winston.info(genesis);
        for (let i = 0; i < nodeCount; i++) {
            fs.writeFileSync(`src/setup/geth/docker/tmp/node${i}/work/genesis.json`, gstr);
        }
    }
};
