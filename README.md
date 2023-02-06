# SEQuRe
Sharing of Entangled Qubits to Read a common private key (E91 protocol)

(Temporary README, to be expanded)

-E91.py:
Simulation of E91 protocol.
At the start of the program you can change some parameters:
n: number of qubits pairs used in the protocol;
_backend: the backend used to execute the protocol. You can use the Aer simulator or the IBM real quantum computers;
eveStrategy: you can choose one of 3 strategies for Eve to interfere with the exchange of the private key. eveStrategy = 0 to disable Eve tampering.

At the end of the program it prints the results: the S value (CHSH correlation value), the shared key, its length and the number of different bits (errors) in the shared key between Alice and Bob.

-E91_optimized.py:
It's the same as E91.py, but instead of creating n circuits it creates just 9 circuits with n counts (shots) so that the execution on the backend is much faster. Alice and Bob use 3 basis each for measuring the qubits, so the combinations are 9 (9 different circuits).
There are two problems with this optimization: Eve's strategy #2 cannot be implemented because Eve chooses a random gate for each qubit, so the different circuits are not 9 anymore.
Also, the resulting key fetched with this method is not random anymore: all the 1s and 0s are sequential and not distributed randomly inside the key. This is not a problem for the performance analysis of the protocol, because the program can still check the number of errors in the shared key, and that's the main point here.