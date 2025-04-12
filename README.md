# FastAPI + SQLite + Web3.py 블록체인 백엔드 데모

이 프로젝트는 FastAPI를 사용하여 SQLite 데이터베이스와 Web3.py를 활용한 ERC-20 토큰 전송 기능을 구현한 예제입니다. 본 프로젝트는 메타마스크와 같은 클라이언트 지갑 없이, 백엔드 서버에서 개인 키를 직접 관리하는 방식을 사용합니다.

> **⚠️ 경고:** 개인 키를 서버에서 관리하는 방식은 매우 위험합니다. 이 프로젝트는 오직 테스트 네트워크(Sepolia 등)와 테스트 자산만 사용하여 작동 원리를 이해하는 용도로만 사용해야 합니다. 실제 운영 환경에 절대로 적용하지 마세요.

---

## 📂 프로젝트 구조

```
project-root/
├── main.py
├── routers/
│   ├── posts.py
│   ├── comments.py
│   ├── token_transfer.py
│   ├── external.py
│   ├── llm_execution.py
│   └── dummy.py
├── models/
│   └── models.py
├── database/
│   └── connection.py
├── services/
│   └── blockchain.py
├── .env
└── requirements.txt
```

---

## 🚀 설치 및 실행 방법

### 1. 레포지토리 클론 및 가상환경 생성

```bash
git clone <repo-url>
cd backend
python -m venv .venv
source .venv/bin/activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. `.env` 파일 작성

아래 내용을 참고하여 프로젝트 루트 폴더에 `.env` 파일을 작성합니다.

```dotenv
RPC_URL="https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID"
PRIVATE_KEY="0xYOUR_TESTNET_PRIVATE_KEY"
```

### 4. 서버 실행

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

이제 서버는 다음 주소에서 확인할 수 있습니다.

```
http://localhost:8000/docs
```

---

## 📚 구현된 기능

### ✅ 데이터베이스 (SQLite)

- 본문(Post) 작성 및 조회
- 댓글(Comment) 작성 및 조회

### ✅ 블록체인 (Web3.py)

- ERC-20 토큰 전송 (백엔드 개인 키 사용)
- 트랜잭션 상태 확인

### ✅ 추가 기능

- 외부 데이터 API (External)
- LLM 실행 API
- 테스트용 더미 데이터 API

---

## 🌐 API 사용 예시

Swagger UI에서 편리하게 API 테스트가 가능합니다.

```
http://localhost:8000/docs
```

ERC-20 토큰 전송 요청 예시:

- POST `/blockchain/transfer-token/`

```json
{
  "token_address": "0xYOUR_ERC20_TOKEN_ADDRESS_ON_SEPOLIA",
  "recipient_address": "0xRECIPIENT_ADDRESS",
  "amount": "1.5"
}
```

응답 예시:

```json
{
  "message": "토큰 전송이 성공적으로 요청되었습니다.",
  "tx_hash": "0x123abc...",
  "explorer_link": "https://sepolia.etherscan.io/tx/0x123abc..."
}
```

---

## 📌 주의사항

- 본 프로젝트는 철저히 학습 목적 및 데모용입니다.
- 개인 키는 반드시 테스트넷에서만 사용하세요.
- 실제 운영환경에서는 MetaMask 또는 WalletConnect 등 안전한 방식의 개인 키 관리 방법을 사용해야 합니다.

---

## 📝 요구사항

필수 패키지:

- FastAPI
- Uvicorn
- SQLModel
- Web3.py (7.x 이상)
- python-dotenv
- python-multipart

`requirements.txt` 예시:

```
fastapi
uvicorn
sqlmodel
web3
python-dotenv
python-multipart
```

---

## 📧 문의사항

이 프로젝트에 대한 질문이나 피드백은 자유롭게 이슈를 남겨주세요.