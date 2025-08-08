from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import jwt
import json
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz

app = Flask(__name__)
app.secret_key = 'zk_ofac_kyc_provider_2025'
CORS(app)

class OFACScreeningService:
    def __init__(self):
        # Multi-database sanctions coverage
        self.sanctions_databases = {
            'ofac_sdn': [
                {"name": "VLADIMIR PUTIN", "dob": "1952-10-07", "program": "UKRAINE-EO13662"},
                {"name": "KIM JONG UN", "dob": "1984-01-08", "program": "DPRK"},
                {"name": "ALI KHAMENEI", "dob": "1939-04-19", "program": "IRAN"},
                {"name": "BASHAR AL-ASSAD", "dob": "1965-09-11", "program": "SYRIA"},
                {"name": "DRUG CARTEL LEADER", "dob": "1975-01-01", "program": "NARCOTICS"},
                {"name": "TERRORIST OPERATIVE", "dob": "1980-01-01", "program": "SDGT"}
            ],
            'eu_sanctions': [
                {"name": "MONEY LAUNDERER", "dob": "1970-01-01", "program": "AML"},
                {"name": "SANCTIONS EVADER", "dob": "1985-01-01", "program": "EVASION"},
                {"name": "CORRUPT OFFICIAL", "dob": "1965-01-01", "program": "CORRUPTION"}
            ],
            'un_security': [
                {"name": "WAR CRIMINAL", "dob": "1960-01-01", "program": "ATROCITIES"},
                {"name": "ARMS DEALER", "dob": "1955-01-01", "program": "PROLIFERATION"}
            ]
        }

        self.total_entries = sum(len(db) for db in self.sanctions_databases.values())
        print(f"📊 OFAC Database loaded: {self.total_entries} sanctioned entities")

    def screen_user(self, full_name: str, date_of_birth: str) -> dict:
        """Screen user against all sanctions databases with fuzzy matching"""

        # Check all databases
        for db_name, entries in self.sanctions_databases.items():
            for entry in entries:
                # Fuzzy name matching (85% threshold)
                name_similarity = fuzz.ratio(full_name.upper(), entry["name"])

                # High confidence match
                if name_similarity >= 85 and date_of_birth == entry["dob"]:
                    return {
                        "compliant": False,
                        "sanctioned": True,
                        "matched_entity": entry,
                        "database": db_name,
                        "confidence": name_similarity / 100.0,
                        "reason": f"High confidence match in {db_name.upper()}"
                    }

                # Medium confidence match 
                elif name_similarity >= 75:
                    print(f"⚠️ Medium confidence match: {full_name} -> {entry['name']} ({name_similarity}%)")

        return {
            "compliant": True,
            "sanctioned": False,
            "databases_checked": list(self.sanctions_databases.keys()),
            "total_entries_screened": self.total_entries,
            "screening_timestamp": datetime.now().isoformat()
        }

    def generate_user_hash(self, user_data: dict) -> str:
        """Generate cryptographic hash of user identity"""
        identity_string = f"USER:{user_data['full_name'].upper()}:{user_data['date_of_birth']}:{user_data.get('address', '')}"
        return hashlib.sha256(identity_string.encode()).hexdigest()

    def get_sanctioned_hashes(self) -> list:
        """Get all sanctioned entity hashes for ZK circuit"""
        hashes = []

        for db_name, entries in self.sanctions_databases.items():
            for entry in entries:
                entity_hash = hashlib.sha256(f"ENTITY:{entry['name']}:{entry['dob']}".encode()).hexdigest()
                hashes.append(entity_hash)

        # Pad to 1000 entries for circuit compatibility
        padded_hashes = hashes + ["0"] * (1000 - len(hashes))
        return padded_hashes[:1000]

    def issue_jwt_credential(self, user_hash: str, user_data: dict) -> str:
        """Issue JWT credential for compliant users"""
        payload = {
            'iss': 'ZK-OFAC-KYC-Provider',
            'sub': user_hash,
            'compliant': True,
            'wallet': user_data.get('wallet_address', ''),
            'screening_details': {
                'databases_checked': 3,
                'total_entries': self.total_entries,
                'screening_time': datetime.now().isoformat()
            },
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=30)
        }

        return jwt.encode(payload, app.secret_key, algorithm='HS256')

# Initialize screening service
screening_service = OFACScreeningService()

@app.route('/api/screen-user', methods=['POST'])
def screen_user():
    """Screen user against OFAC sanctions databases"""
    data = request.json

    if not data or not data.get('full_name') or not data.get('date_of_birth'):
        return jsonify({
            "success": False,
            "error": "MISSING_REQUIRED_FIELDS",
            "message": "Required: full_name, date_of_birth"
        }), 400

    try:
        # Screen user
        screening_result = screening_service.screen_user(
            data['full_name'], 
            data['date_of_birth']
        )

        if screening_result["compliant"]:
            # Generate user hash and credential
            user_hash = screening_service.generate_user_hash(data)
            credential = screening_service.issue_jwt_credential(user_hash, data)

            return jsonify({
                "success": True,
                "compliant": True,
                "user_hash": user_hash,
                "credential": credential,
                "expires_at": (datetime.now() + timedelta(days=30)).isoformat(),
                "screening_details": screening_result
            })
        else:
            # User is sanctioned
            return jsonify({
                "success": False,
                "compliant": False,
                "sanctioned": True,
                "matched_entity": screening_result["matched_entity"],
                "database": screening_result["database"],
                "confidence": screening_result["confidence"],
                "message": "User found in sanctions database"
            })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "SCREENING_ERROR", 
            "message": str(e)
        }), 500

@app.route('/api/get-sanctioned-hashes', methods=['GET'])
def get_sanctioned_hashes():
    """Get sanctioned entity hashes for ZK circuit"""
    try:
        hashes = screening_service.get_sanctioned_hashes()

        return jsonify({
            "success": True,
            "sanctioned_hashes": hashes,
            "total_sanctioned": screening_service.total_entries,
            "circuit_size": 1000,
            "databases": list(screening_service.sanctions_databases.keys())
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "HASH_GENERATION_ERROR",
            "message": str(e)
        }), 500

@app.route('/api/verify-credential', methods=['POST'])
def verify_credential():
    """Verify JWT credential"""
    data = request.json

    if not data or not data.get('credential'):
        return jsonify({
            "success": False,
            "error": "MISSING_CREDENTIAL"
        }), 400

    try:
        payload = jwt.decode(data['credential'], app.secret_key, algorithms=['HS256'])

        return jsonify({
            "success": True,
            "valid": True,
            "compliant": payload.get('compliant', False),
            "expires_at": payload.get('exp'),
            "user_hash": payload.get('sub'),
            "screening_details": payload.get('screening_details', {})
        })

    except jwt.ExpiredSignatureError:
        return jsonify({
            "success": False,
            "error": "CREDENTIAL_EXPIRED"
        }), 401

    except jwt.InvalidTokenError:
        return jsonify({
            "success": False,
            "error": "INVALID_CREDENTIAL"
        }), 401

@app.route('/api/system-status', methods=['GET'])
def system_status():
    """Get system status and statistics"""
    return jsonify({
        "system": "ZK-OFAC KYC Provider",
        "version": "1.0.0",
        "status": "operational",
        "databases": {
            "ofac_sdn_list": len(screening_service.sanctions_databases['ofac_sdn']),
            "eu_sanctions_list": len(screening_service.sanctions_databases['eu_sanctions']),
            "un_security_list": len(screening_service.sanctions_databases['un_security']),
            "total_entries": screening_service.total_entries
        },
        "features": {
            "fuzzy_matching": True,
            "multi_database_screening": True,
            "jwt_credentials": True,
            "zk_circuit_compatibility": True
        },
        "configuration": {
            "fuzzy_matching_threshold": 85.0,
            "credential_validity_days": 30,
            "circuit_size": 1000
        },
        "last_updated": datetime.now().isoformat()
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "databases_loaded": len(screening_service.sanctions_databases) > 0,
        "total_sanctions": screening_service.total_entries
    })

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with system info"""
    return jsonify({
        "system": "ZK-OFAC KYC Provider",
        "description": "Privacy-preserving OFAC sanctions screening",
        "endpoints": {
            "screen_user": "/api/screen-user",
            "get_hashes": "/api/get-sanctioned-hashes", 
            "verify_credential": "/api/verify-credential",
            "system_status": "/api/system-status",
            "health": "/api/health"
        },
        "total_sanctions": screening_service.total_entries,
        "privacy_preserved": True
    })

if __name__ == '__main__':
    print("🚀 Starting ZK-OFAC KYC Provider...")
    print(f"📊 Loaded {screening_service.total_entries} sanctioned entities")
    print("🔍 Fuzzy matching threshold: 85%")
    print("🔐 JWT credentials: 30-day validity")
    print("⚡ Zero-knowledge ready")
    print("🌐 Server: http://localhost:5002")
    print("")

    app.run(debug=True, host='0.0.0.0', port=5002)
