# Secure-E-documentation

# 🔐 Secure E-Documentation Verification System

A secure web-based application designed to ensure document authenticity, integrity, and verification using cryptographic hashing and QR-based validation.

---

## 📌 Features
- Secure document upload
- SHA-256 hash generation
- QR code generation for document verification
- Tamper detection using hash comparison
- Authorized verifier access
- Firebase-backed data storage
- Role-based authentication

---

## 🛠️ Tech Stack
- Python (Flask)
- Firebase
- SHA-256 Cryptographic Hashing
- QR Code Generation
- HTML, CSS, JavaScript

---

## 🔄 Workflow
1. User uploads a document
2. System generates SHA-256 hash
3. QR code is generated and linked to the hash
4. Verifier scans QR or uploads document
5. Hash comparison determines authenticity

---

## 🚀 Installation & Setup

```bash
git clone https://github.com/your-username/secure-e-documentation-verification.git
cd secure-e-documentation-verification
pip install -r requirements.txt
python app.py
