import random
from datetime import datetime
from typing import List
import winsound
from matplotlib import pyplot as plt
from qiskit import QuantumCircuit, execute, IBMQ
from qiskit.providers import Backend
from qiskit.providers.aer import QasmSimulator
from qiskit.providers.ibmq import IBMQBackend


# X gate
def A1(circ: QuantumCircuit):
    circ.h(0)

# Corrisponde a Z + X / sqrt(2)
def A2(circ: QuantumCircuit):
    circ.s(0)
    circ.h(0)
    circ.t(0)
    circ.h(0)

# Z gate
def A3(circ: QuantumCircuit):
    return #Nessuna operazione richiesta per la direzione Z


# Corrisponde a Z + X / sqrt(2)
def B1(circ: QuantumCircuit):
    circ.s(1)
    circ.h(1)
    circ.t(1)
    circ.h(1)

# Z
def B2(circ: QuantumCircuit):
    return  # Nessuna operazione richiesta per la direzione Z

# Corrisponde a Z - X / sqrt(2)
def B3(circ: QuantumCircuit):
    circ.s(1)
    circ.h(1)
    circ.tdg(1)
    circ.h(1)

def useIBMBackend(backendName: str):
    IBMQ.load_account()
    provider = IBMQ.get_provider(group='uni-milano-bicoc-1') # Alcuni backend premium sono presenti solo su questo gruppo
    backend = provider.get_backend(backendName)
    return backend

# Lo stato inziale sarà |01> - |10> / sqrt(2)
def newEntangledCircuit():
    newCircuit = QuantumCircuit(3, 3) #Il terzo qubit serve per implementare la strategia 3 di Eve
    newCircuit.x(0)
    newCircuit.x(1)
    newCircuit.h(0)
    newCircuit.cnot(0, 1)
    return newCircuit

def getResultsFromCircuits(circuits: List[QuantumCircuit], backend: Backend):
    job = execute(circuits, backend, shots=1)
    print(job.status())
    # Grab results from the job
    results = job.result()
    print(job.status())
    #print("Data e ora Job: ", job.creation_date()) # Il metodo creation_date() esiste solo sui backend dei computer reali
    print("Data e ora completamento: ", datetime.now())
    return results

def indexForResult(result: str) -> int:
    result = result[1:3] #I risultati sono al contrario, il terzo bit quindi è quello di Alice, il secondo quello di Bob, il terzo quello di Eve
    if result == '00':
        return 0
    elif result == '01':
        return 1
    elif result == '10':
        return 2
    elif result == '11':
        return 3

def eveAction1(circuits: list):
    # Strategia 1: Misuro tutti i qubit di Bob
    for circuit in circuits:
        circuit.measure(1, 1)

def eveAction2(circuits: list):
    # Strategia 2: Misuro tutti i qubit di Bob usando una direzione casuale tra quelle a disposizione di Bob
    for circuit in circuits:
        eve_basis = random.choice([1, 2, 3])
        if eve_basis == 1:
            B1(circuit)
        elif eve_basis == 2:
            B2(circuit)
        elif eve_basis == 3:
            B3(circuit)
        circuit.measure(1, 1)

def eveAction3(circuits: list):
    # Strategia 3: Metto in entanglement un terzo qubit posseduto da Eve con il qubit di Bob
    for circuit in circuits:
        circuit.cnot(1, 2)



######### Parametri configurabili - Inizio #############

_backend = QasmSimulator() # Aer's qasm_simulator
#_backend = useIBMBackend('ibm_lagos')

# Numero di coppie di qubit in entanglement generate
n=500

# Strategia di Eve; i valori possibili sono 1, 2, 3
# 0 per non avere l'intervento di Eve
eveStrategy = 0
######### Parametri configurabili - Fine #############


alice_basis = []
bob_basis = []

qubits_circuits = []

for i in range(0, n):
    #Charlie (o Alice) genera n coppie di qubit in entanglement
    qubits_circuits.append(newEntangledCircuit())

    #Alice e Bob scelgono indipendentemente una delle 3 basi previste per loro con cui misurare i propri qubit
    alice_basis.append(random.choice([1, 2, 3]))
    bob_basis.append(random.choice([1, 2, 3]))

####################################
# L'azione di Eve si inserisce qui #
####################################
if eveStrategy == 1:
    eveAction1(qubits_circuits)
elif eveStrategy == 2:
    eveAction2(qubits_circuits)
elif eveStrategy == 3:
    eveAction3(qubits_circuits)


#Conteggi per 00, 01, 10, 11, rispettivamente
countA1B1 = [0, 0, 0, 0] # XW observable
countA1B3 = [0, 0, 0, 0] # XV observable
countA3B1 = [0, 0, 0, 0] # ZW observable
countA3B3 = [0, 0, 0, 0] # ZV observable


aliceKey = []
bobKey = []

for i, circ in enumerate(qubits_circuits):
    if alice_basis[i] == 3 and bob_basis[i] == 2: #Verranno usati per la chiave
        A3(circ)
        B2(circ)
    elif alice_basis[i] == 2 and bob_basis[i] == 1: #Verranno usati per la chiave
        A2(circ)
        B1(circ)
    elif alice_basis[i] == 1 and bob_basis[i] == 3:
        A1(circ)
        B3(circ)
    elif alice_basis[i] == 1 and bob_basis[i] == 1:
        A1(circ)
        B1(circ)
    elif alice_basis[i] == 3 and bob_basis[i] == 1:
        A3(circ)
        B1(circ)
    elif alice_basis[i] == 3 and bob_basis[i] == 3:
        A3(circ)
        B3(circ)

    circ.measure(0, 0)
    circ.measure(1, 1)
    circ.measure(2, 2)


backendResults = getResultsFromCircuits(qubits_circuits, _backend)

for i, result in enumerate(backendResults.get_counts()):
    resultBits = list(result.keys())[0]
    if (alice_basis[i] == 3 and bob_basis[i] == 2) or (alice_basis[i] == 2 and bob_basis[i] == 1):
        aliceKey.append(resultBits[2])
        bobKey.append(resultBits[1])
    elif alice_basis[i] == 1 and bob_basis[i] == 3:
        j = indexForResult(resultBits)
        countA1B3[j] += 1
    elif alice_basis[i] == 1 and bob_basis[i] == 1:
        j = indexForResult(resultBits)
        countA1B1[j] += 1
    elif alice_basis[i] == 3 and bob_basis[i] == 1:
        j = indexForResult(resultBits)
        countA3B1[j] += 1
    elif alice_basis[i] == 3 and bob_basis[i] == 3:
        j = indexForResult(resultBits)
        countA3B3[j] += 1

aliceKeyString = ""
bobKeyString = ""
errorCount = 0

#for i in range(0, len(aliceKey)-1):
for (i, aliceBitString) in enumerate(aliceKey):
    bobBitString = bobKey[i]
    bobBitString = str(int(not bool(int(bobBitString)))) #applico NOT
    aliceKeyString += aliceBitString
    bobKeyString += bobBitString
    if aliceBitString != bobBitString:
        errorCount += 1



# number of the results obtained from the measurements in a particular basis
total11 = sum(countA1B1)
total13 = sum(countA1B3)
total31 = sum(countA3B1)
total33 = sum(countA3B3)

# Valori d'aspettazione
expect11 = (countA1B1[0] - countA1B1[1] - countA1B1[2] + countA1B1[3]) / total11  # -1/sqrt(2)
expect13 = (countA1B3[0] - countA1B3[1] - countA1B3[2] + countA1B3[3]) / total13  # 1/sqrt(2)
expect31 = (countA3B1[0] - countA3B1[1] - countA3B1[2] + countA3B1[3]) / total31  # -1/sqrt(2)
expect33 = (countA3B3[0] - countA3B3[1] - countA3B3[2] + countA3B3[3]) / total33  # -1/sqrt(2)

# Valore di correlazione CHSH
#|S| = |<A1B1> - <A1B3> + <A3B1> + <A3B3>|
corr = expect11 - expect13 + expect31 + expect33

#print(expect11)
#print(expect13)
#print(expect31)
#print(expect33)
#print(corr)

# CHSH inequality test
print('----------------------------------------')
print('----------------Risultati---------------')
print('----------------------------------------')
print('CHSH correlation value: ' + str(round(abs(corr), 5)))
print('The shared key is: ' + aliceKeyString)
print('Key length: ' + str(len(aliceKey)))
print('Number of errors in key shared: ' + str(errorCount))


# Draw the circuit
# circuit.draw(output='mpl')
# plt.show()

#Quando le code sui computer di IBM sono lunghe, un beep può tornare comodo...
#duration = 1000  # milliseconds
#freq = 1000  # Hz
#winsound.Beep(freq, duration)