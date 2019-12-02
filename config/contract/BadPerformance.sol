pragma solidity ^0.4.2;

contract BadPerformance {

    mapping(string=>uint) map0;
    mapping(string=>uint) map1;

    function badPerfLevel1(string arg0, uint arg1) public {
        for (uint p = 0; p < 10; p++) {
            map0[arg0] = arg1 + p;
            map1[arg0] = map0[arg0] + p;
        }
    }

    function badPerfLevel2(string arg0, uint arg1) public {
        for (uint p = 0; p < 100; p++) {
            map0[arg0] = arg1 + p;
            map1[arg0] = map0[arg0] + p;
        }
    }

    function badPerfLevel3(string arg0, uint arg1) public {
        for (uint p = 0; p < 1000; p++) {
            map0[arg0] = arg1 + p;
            map1[arg0] = map0[arg0] + p;
        }
    }

}
