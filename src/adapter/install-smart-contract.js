
'use strict';

const winston = require('winston');
const Web3 = require('web3');
const solc = require('solc');
const fs = require ('fs');
const accountUtil = require('../util/account');
const providers = require('../util/providers');

module.exports.run = async function (node, contractPath, contractName) {
    // web3sync.setWeb3(config.proxy);
    const web3 = providers.getProvider(node);
    winston.info(`Installing smart contract ${contractName} ...`);
    let accountPair = accountUtil.randomAccount(node);
    let accountPrivateKey = accountPair[1];
    let accountAddress = accountPair[0];
    let contractSource = fs.readFileSync(contractPath, 'utf-8');
    winston.info(`Compiling smart contract ${contractName} ...`);
    const output = solc.compile(contractSource, 1);
    // winston.info(contractBytecode);
// `output` here contains the JSON output as specified in the documentation
    let _contractName = ':' + contractName;
    const bytecode = output.contracts[_contractName].bytecode;
    const abi = output.contracts[_contractName].interface;
    let jsonABI = JSON.parse(abi);
    const contractStructure = web3.eth.Contract(jsonABI);
    winston.info(`Deploying smart contract ${contractName} ...`);
    let contractInstance = await contractStructure.deploy({
        data: '0x' + bytecode
    }).send({
        from: accountAddress,
        gas: 1500000,
        gasPrice: '20000000000'
    }).then((newContractInstance) => {
            winston.info(newContractInstance.options.address); // instance with the new contract address
            return Promise.resolve({
                address: newContractInstance.options.address,
                abi: JSON.parse(abi)
            });
        });

    winston.info('======================');
    return contractInstance;

};
