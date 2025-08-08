/**
 * ZK-OFAC Client Library
 * Zero-Knowledge OFAC Compliance Proof Generation
 */

class ZKOFACClient {
    constructor(options = {}) {
        this.kycProviderUrl = options.kycProviderUrl || 'http://localhost:5002';
        this.contractAddress = options.contractAddress || null;
        this.web3 = null;
        this.contract = null;
        this.userAccount = null;
    }

    /**
     * Initialize Web3 connection
     */
    async initializeWeb3() {
        if (typeof window !== 'undefined' && window.ethereum) {
            // Modern dapp browsers
            try {
                this.web3 = new Web3(window.ethereum);
                await window.ethereum.request({ method: 'eth_requestAccounts' });

                const accounts = await this.web3.eth.getAccounts();
                this.userAccount = accounts[0];

                console.log('✅ Web3 initialized, account:', this.userAccount);
                return true;

            } catch (error) {
                console.error('❌ Web3 initialization failed:', error);
                throw error;
            }
        } else {
            console.warn('⚠️ MetaMask not detected, using demo mode');
            this.userAccount = '0x742d35Cc6634C0532925a3b8D451651e077cc848';
            return false;
        }
    }

    /**
     * Screen user with KYC provider
     */
    async screenUser(userData) {
        try {
            console.log('🔍 Screening user with KYC provider...');

            const response = await fetch(`${this.kycProviderUrl}/api/screen-user`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            console.log('📋 Screening result:', result.compliant ? '✅ PASSED' : '❌ FAILED');

            return result;

        } catch (error) {
            console.error('❌ User screening failed:', error);
            throw error;
        }
    }

    /**
     * Get sanctioned entity hashes for ZK circuit
     */
    async getSanctionedHashes() {
        try {
            console.log('📊 Fetching sanctioned hashes for ZK circuit...');

            const response = await fetch(`${this.kycProviderUrl}/api/get-sanctioned-hashes`);
            const result = await response.json();

            if (!result.success) {
                throw new Error(result.message || 'Failed to fetch sanctioned hashes');
            }

            console.log(`📈 Retrieved ${result.total_sanctioned} sanctioned entities`);

            return result.sanctioned_hashes;

        } catch (error) {
            console.error('❌ Failed to get sanctioned hashes:', error);
            throw error;
        }
    }

    /**
     * Generate ZK compliance proof (simulated)
     */
    async generateZKProof(userData, sanctionedHashes) {
        try {
            console.log('🔐 Generating zero-knowledge compliance proof...');

            // Generate user identity hash
            const userIdentity = `USER:${userData.full_name.toUpperCase()}:${userData.date_of_birth}`;
            const userHash = await this.sha256(userIdentity);

            // Generate bank details hash
            const bankDetails = `BANK:${userData.bank_account || ''}`;
            const bankHash = await this.sha256(bankDetails);

            // Generate random salt
            const salt = this.generateRandomSalt();

            // Simulate proof generation (in production, would use snarkjs)
            console.log('⚙️ Computing ZK circuit witness...');
            await this.delay(1500); // Simulate computation time

            console.log('🧮 Generating zk-SNARK proof...');
            await this.delay(1000); // Simulate proof generation

            // Check if user is sanctioned (simple simulation)
            const userDataHash = await this.sha256(`${userHash}:${bankHash}:${salt}`);
            const isSanctioned = sanctionedHashes.slice(0, 20).includes(userDataHash); // Check first 20

            const proof = {
                a: ["0x1234567890abcdef", "0xfedcba0987654321"],
                b: [["0xabcd1234", "0x5678efgh"], ["0x9876ijkl", "0x4321mnop"]],
                c: ["0xdeadbeef", "0xcafebabe"],
                publicSignals: [
                    isSanctioned ? "0" : "1",  // isCompliant (0 = sanctioned, 1 = compliant)
                    userDataHash.slice(0, 42)   // commitmentHash
                ]
            };

            const result = {
                proof: proof,
                publicSignals: proof.publicSignals,
                isCompliant: !isSanctioned,
                isSanctioned: isSanctioned,
                commitmentHash: proof.publicSignals[1],
                generationTime: Date.now(),
                circuitConstraints: 3500,
                provingTimeMs: 2500,
                proofSizeBytes: 128
            };

            console.log('✅ ZK proof generated successfully');
            console.log(`🔒 User is ${result.isCompliant ? 'COMPLIANT' : 'SANCTIONED'}`);
            console.log(`📊 Proof size: ${result.proofSizeBytes} bytes`);

            return result;

        } catch (error) {
            console.error('❌ ZK proof generation failed:', error);
            throw error;
        }
    }

    /**
     * Verify ZK proof locally (simulated)
     */
    async verifyProof(proof, publicSignals) {
        try {
            console.log('🔍 Verifying ZK proof locally...');

            // Simulate verification time
            await this.delay(50);

            // Simple validation checks
            const isValidStructure = (
                proof.a && proof.a.length === 2 &&
                proof.b && proof.b.length === 2 &&
                proof.c && proof.c.length === 2 &&
                publicSignals && publicSignals.length === 2
            );

            const isValidSignals = (
                publicSignals[0] === "0" || publicSignals[0] === "1"
            );

            const isValid = isValidStructure && isValidSignals;

            console.log(isValid ? '✅ Proof verified successfully' : '❌ Proof verification failed');

            return isValid;

        } catch (error) {
            console.error('❌ Proof verification error:', error);
            return false;
        }
    }

    /**
     * Complete compliance verification flow
     */
    async verifyCompliance(userData) {
        try {
            console.log('🚀 Starting complete compliance verification...');

            // Step 1: Screen user with KYC provider
            const screeningResult = await this.screenUser(userData);

            if (!screeningResult.compliant) {
                return {
                    success: false,
                    stage: 'screening',
                    message: 'User failed OFAC screening',
                    details: screeningResult
                };
            }

            // Step 2: Get sanctioned hashes for ZK circuit
            const sanctionedHashes = await this.getSanctionedHashes();

            // Step 3: Generate ZK proof
            const zkProof = await this.generateZKProof(userData, sanctionedHashes);

            // Step 4: Verify proof locally
            const isValidProof = await this.verifyProof(zkProof.proof, zkProof.publicSignals);

            if (!isValidProof) {
                throw new Error('Generated proof failed local verification');
            }

            console.log('🎉 Compliance verification completed successfully!');

            return {
                success: true,
                compliant: zkProof.isCompliant,
                screeningResult: screeningResult,
                zkProof: zkProof,
                proofVerified: isValidProof,
                completedAt: new Date().toISOString()
            };

        } catch (error) {
            console.error('❌ Compliance verification failed:', error);
            return {
                success: false,
                error: error.message,
                stage: 'unknown'
            };
        }
    }

    /**
     * Simulate P2P payment authorization
     */
    async authorizePayment(recipientAddress, amount, currency = 'USD') {
        try {
            console.log(`💸 Authorizing payment: ${amount} ${currency} to ${recipientAddress}`);

            // Simulate smart contract interaction
            await this.delay(500);

            const transactionHash = `0x${this.generateRandomSalt().slice(0, 64)}`;

            console.log('✅ Payment authorized successfully');
            console.log(`📋 Transaction hash: ${transactionHash}`);

            return {
                success: true,
                transactionHash: transactionHash,
                amount: amount,
                currency: currency,
                recipient: recipientAddress,
                timestamp: new Date().toISOString()
            };

        } catch (error) {
            console.error('❌ Payment authorization failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Get system status
     */
    async getSystemStatus() {
        try {
            const response = await fetch(`${this.kycProviderUrl}/api/system-status`);
            const result = await response.json();
            return result;
        } catch (error) {
            console.error('❌ Failed to get system status:', error);
            throw error;
        }
    }

    // Utility functions
    async sha256(input) {
        const encoder = new TextEncoder();
        const data = encoder.encode(input);
        const hashBuffer = await crypto.subtle.digest('SHA-256', data);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        return '0x' + hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    }

    generateRandomSalt() {
        const array = new Uint8Array(32);
        crypto.getRandomValues(array);
        return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Export for Node.js and browser
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ZKOFACClient;
}

if (typeof window !== 'undefined') {
    window.ZKOFACClient = ZKOFACClient;

    // Global demo function
    window.demoZKCompliance = async function() {
        console.log('🎬 Starting ZK-OFAC Compliance Demo...');

        const client = new ZKOFACClient();

        try {
            await client.initializeWeb3();

            const testUsers = [
                {
                    full_name: 'Alice Johnson',
                    date_of_birth: '1992-03-15',
                    address: '123 Main St, New York, NY',
                    phone: '+1-555-0123',
                    email: 'alice@example.com',
                    bank_account: 'ACC123456789',
                    wallet_address: client.userAccount
                },
                {
                    full_name: 'Vladimir Putin',
                    date_of_birth: '1952-10-07',
                    address: 'Kremlin, Moscow',
                    phone: '+7-xxx-xxx-xxxx',
                    email: 'sanctioned@example.com'
                }
            ];

            console.log('\n👤 Testing compliant user...');
            const aliceResult = await client.verifyCompliance(testUsers[0]);
            console.log('Alice result:', aliceResult.success ? '✅ COMPLIANT' : '❌ NOT COMPLIANT');

            if (aliceResult.success && aliceResult.compliant) {
                console.log('\n💸 Testing P2P payment...');
                const paymentResult = await client.authorizePayment('0x742d35Cc6634C0532925a3b8D451651e077cc848', 1000);
                console.log('Payment result:', paymentResult.success ? '✅ AUTHORIZED' : '❌ REJECTED');
            }

            console.log('\n🚨 Testing sanctioned user...');
            const putinResult = await client.verifyCompliance(testUsers[1]);
            console.log('Putin result:', putinResult.success ? '✅ PASSED' : '❌ BLOCKED (Expected)');

            console.log('\n🎉 ZK-OFAC Demo Completed!');
            console.log('📊 System Statistics:', await client.getSystemStatus());

            return {
                compliantUser: aliceResult,
                sanctionedUser: putinResult,
                systemWorking: true
            };

        } catch (error) {
            console.error('❌ Demo failed:', error);
            return { error: error.message };
        }
    };
}
