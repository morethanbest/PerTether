
'use strict';

const winston = require('winston');
const fs = require('fs');

//gasprice unit gwei
module.exports.submitTransaction = async function (nodeName, web3, address, abi, account, passphrase, gasprice, args) {
    let result = {
        status: 1,
        gasprice: gasprice,
        startTime: Date.now(),
        finishTime: -1,
        latency: -1
    };
    let data = web3.eth.abi.encodeFunctionCall(abi, args);
    return await web3.eth.sendTransaction({
        from: account,
        gasPrice: parseInt(gasprice * 1000000000).toString(),
        gas: '200000',
        to: address,
        value: "100000000000000000",
        data: data
    }).then(function (receipt) {
        result.status = 0;
        result.finishTime = Date.now();
        result.latency = result.finishTime - result.startTime;
        winston.info(`${nodeName}: ${JSON.stringify(receipt)}`);
        return Promise.resolve(result);
    }, function (error) {
        winston.info(`${nodeName}: ${JSON.stringify(error)}`);
        result.finishTime = Date.now();
        result.latency = result.finishTime - result.startTime;
        return Promise.resolve(result);
    });

};

module.exports.submitQuery = async function(context, contractID, args){
    //TODO
};
