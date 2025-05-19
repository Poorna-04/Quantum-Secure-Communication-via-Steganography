from qiskit import *
import numpy as np
import matplotlib.pyplot as plt
from qiskit.visualization import plot_histogram
# Creating registers with n qubits 
n =7  # for a local backend n can go as up as 23, after that it raises a Memory Error
qr = QuantumRegister(n, name='qr')
cr = ClassicalRegister(n, name='cr')

qc = QuantumCircuit(qr, cr, name='QC')
"""
qr2 = QuantumRegister(n, name='qr')
cr2= ClassicalRegister(n, name='cr')
qc2 = QuantumCircuit(qr2, cr2, name='QC')
for i in range(n):
    qc2.h(i)
    qc2.measure(qr2,cr2)
qc2.draw(output='mpl')
simulator = Aer.get_backend('qasm_simulator')
execute(qc2, backend = simulator)
result = execute(qc2, backend = simulator).result()
k=list(result.get_counts(qc2))[0]
print(k)
"""
# Generate a random number in the range of available qubits [0,65536))
alice_key = np.random.randint(0,2**n)# we can remplace it by a key from a quantum key generator


alice_key = np.binary_repr(alice_key,n) 
print(alice_key)
for i in range(len(alice_key)):
 if alice_key[i]=='1':
    qc.x(qr[i])
B=[]
for i in range(len(alice_key)):

 if 0.5 < np.random.random():
    qc.h(qr[i])
    B.append("H")
 else:
    B.append("S")
    pass
    
qc.barrier()  
print("Alice Basis",B)
%config InlineBackend.figure_format = 'svg'
qc.draw(output='mpl')
C=[]
for i in range(len(alice_key)):
 if 0.5 < np.random.random():
    qc.h(qr[i])
    C.append("H")
    
 else:
    C.append("S")
qc.barrier()
for i in range(len(alice_key)):
 qc.measure(qr[i],cr[i])
print("Bob Basis",C)
qc.draw(output='mpl')
simulator = Aer.get_backend('qasm_simulator')
execute(qc, backend = simulator)
result = execute(qc, backend = simulator).result()
print("Bob key :",list(result.get_counts(qc))[0])
print("Bob Basis",C)

print("Alice key :",alice_key)
print("Alice Basis :",B)
def sifted_key(A_basis,B_basis,key): 
 correct_basis=[]
 sifted_key=''

 for i in range(len(A_basis)):
  if A_basis[i]==B_basis[i]:
    correct_basis.append(i)
    sifted_key+=key[i]
  else:
    pass 
 return sifted_key,correct_basis
a=sifted_key(B,C,alice_key)
print("sifted key",a[0])
print("Basis",a[1])
BB84_key=a[0]
def wordToBV(s) :
    #convert text to binar
    a_byte_array = bytearray(s, "utf8")
    byte_list = []


    for byte in a_byte_array:
        binary_representation = bin(byte)
        byte_list.append(binary_representation[9-n:])
        #chop off the "0b" at the beginning. can also truncate the binary to fit on a device with N qubits
        #binary has 2 extra digits for "0b", so it starts at 9 for our 7 bit operation. 

    print(byte_list)
    
    circuit_array = []
    
    length = len(byte_list) 
    
    for i in range(length):
    
        s = byte_list[i]


        #do all  this stuff for every letter

        # We need a circuit with n qubits, plus one ancilla qubit
        # Also need n classical bits to write the output to
        bv_circuit = QuantumCircuit(n+1, n)

        # put ancilla in state |->
        bv_circuit.h(n)
        bv_circuit.z(n)

        # Apply Hadamard gates before querying the oracle
        for i in range(n):
            bv_circuit.h(i)

        # Apply barrier 
        bv_circuit.barrier()

        # Apply the inner-product oracle
        s = s[::-1] # reverse s to fit qiskit's qubit ordering
        for q in range(n):
            if s[q] == '0':
                bv_circuit.i(q)
            else:
                bv_circuit.cx(q, n)

        # Apply barrier 
        bv_circuit.barrier()

        #Apply Hadamard gates after querying the oracle
        for i in range(n):
            bv_circuit.h(i)

        # Measurement
        for i in range(n):
            bv_circuit.measure(i, i)
            
        circuit_array.append(bv_circuit)

    
    return circuit_array
circuit_to_run = wordToBV('Qiskit')#Secret Msg
circuit_to_run[0].draw(output='mpl')
backend = BasicAer.get_backend('qasm_simulator')
shots = 4096
results = execute(circuit_to_run[::-1], backend=backend, shots=shots).result()
answer = results.get_counts()

plot_histogram(answer)
def encrypt(BB84_key, letter):
    """Calculates XOR"""
    b = int(BB84_key, 2)
    x = ord(letter)
    return format(b ^ x, "b")


def stega_encoder(LM, carrier_msg):
    """Encodes LM bits message into carrier_msg"""
    message = ""
    size = len(LM[0])
    i = 0
    for j, bitstring in enumerate(LM):
        for k, digit in enumerate(bitstring):
            while (not carrier_msg[i].isalpha()):
                message += carrier_msg[i]
                i += 1

            if digit == "1":
                letter = carrier_msg[i].upper()
                message += letter
            else:
                message += carrier_msg[i]

            i += 1
    
    if i < len(carrier_msg):
        message += carrier_msg[i:]

    return message


def stega_decoder(new_carrier_msg, BB84_key):
    """Decodes secret message from new_carrier_msg"""

    b = int(BB84_key, 2)

    message = ""
    bitstring = ""
    for char in new_carrier_msg:
        if char.isalpha():
            if char.isupper():
                bitstring += "1"
            else:
                bitstring += "0"

        if len(bitstring) == 7:
            x = int(bitstring, 2)
            message += chr(b ^ x)
            bitstring = ""

    return message
a = chr(1110100)
str(a)

encrypt(BB84_key,'q')
secret_msg='qiskit' 

L=[]
for c in secret_msg:
    L.append(encrypt(BB84_key,c))
carrier_msg='aaaa aaa aaa aaaa aaaaaaa aaaaaaa aaaaaaa aaabaaa'
new_carrier_msg=stega_encoder(L, carrier_msg)
new_carrier_msg

stega_decoder(new_carrier_msg, BB84_key)
