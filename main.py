from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import uvicorn
import json
import random
from pathlib import Path
from chatbot import GeminiChatBot
import asyncio

# Cấu hình các file JSON tương ứng với từng option
JSON_FILES = {
    "peer_pressure": "data/peer_pressure_quiz.json",
    "academic_stress": "data/academic_stress_quiz.json", 
    "social_anxiety": "data/social_anxiety_quiz.json",
    "self_esteem": "data/self_esteem_quiz.json",
    "depression": "data/depression_quiz.json"
}

# Assessment ranges cho từng loại quiz
ASSESSMENT_CONFIGS = {
    "peer_pressure": [
        {"min": 25, "max": 30, "assessment": "Bạn kiểm soát rất tốt áp lực đồng trang lứa."},
        {"min": 18, "max": 24, "assessment": "Bạn có một số áp lực nhưng vẫn giữ được sự cân bằng."},
        {"min": 10, "max": 17, "assessment": "Bạn đang bị ảnh hưởng đáng kể bởi áp lực đồng trang lứa."},
        {"min": 0,  "max": 9,  "assessment": "Bạn có thể đang chịu áp lực lớn và cần tìm cách giải tỏa."}
    ],
    "academic_stress": [
        {"min": 25, "max": 30, "assessment": "Bạn quản lý áp lực học tập rất tốt."},
        {"min": 18, "max": 24, "assessment": "Bạn có thể điều chỉnh áp lực học tập khá hiệu quả."},
        {"min": 10, "max": 17, "assessment": "Bạn đang gặp khó khăn với áp lực học tập."},
        {"min": 0,  "max": 9,  "assessment": "Bạn đang chịu áp lực học tập rất lớn, cần tìm sự hỗ trợ."}
    ],
    "social_anxiety": [
        {"min": 25, "max": 30, "assessment": "Bạn tự tin trong các tình huống xã hội."},
        {"min": 18, "max": 24, "assessment": "Bạn có một ít lo lắng xã hội nhưng vẫn kiểm soát được."},
        {"min": 10, "max": 17, "assessment": "Bạn thường xuyên cảm thấy lo lắng trong các tình huống xã hội."},
        {"min": 0,  "max": 9,  "assessment": "Bạn có thể đang gặp phải lo âu xã hội nghiêm trọng."}
    ],
    "self_esteem": [
        {"min": 25, "max": 30, "assessment": "Bạn có lòng tự trọng tốt và tích cực."},
        {"min": 18, "max": 24, "assessment": "Bạn có lòng tự trọng ổn định."},
        {"min": 10, "max": 17, "assessment": "Lòng tự trọng của bạn cần được cải thiện."},
        {"min": 0,  "max": 9,  "assessment": "Bạn có thể đang thiếu tự tin và cần hỗ trợ."}
    ],
    "depression": [
        {"min": 25, "max": 30, "assessment": "Tâm trạng của bạn rất tích cực và ổn định."},
        {"min": 18, "max": 24, "assessment": "Bạn có tâm trạng khá tốt với một vài thăng trầm nhỏ."},
        {"min": 10, "max": 17, "assessment": "Bạn có thể đang trải qua một số khó khăn về tâm trạng."},
        {"min": 0,  "max": 9,  "assessment": "Bạn có thể đang gặp vấn đề nghiêm trọng về tâm trạng, nên tìm sự hỗ trợ."}
    ]
}

# Hàm load dữ liệu từ JSON với option
def load_quiz_data(quiz_type: str = "peer_pressure") -> Dict[int, dict]:
    if quiz_type not in JSON_FILES:
        raise ValueError(f"Quiz type '{quiz_type}' không được hỗ trợ. Các loại có sẵn: {list(JSON_FILES.keys())}")
    
    file_path = Path(JSON_FILES[quiz_type])
    if not file_path.exists():
        raise FileNotFoundError(f"File {file_path} không tồn tại.")
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # chuyển key string -> int
    return {int(k): v for k, v in data.items()}

# Xáo trộn thứ tự đáp án cho một câu hỏi
def shuffle_options(options: Dict[str, str]) -> Dict[str, str]:
    # Lấy các cặp key-value
    items = list(options.items())
    # Xáo trộn thứ tự các cặp
    random.shuffle(items)
    # Tạo dictionary mới với thứ tự đã xáo trộn
    return dict(items)

# Chọn ngẫu nhiên số câu hỏi (mặc định 10) và xáo trộn đáp án
def get_randomized_questions(quiz_type: str = "peer_pressure", limit: int = 10) -> Dict[int, Dict[str, Any]]:
    quiz_data: Dict[int, dict] = load_quiz_data(quiz_type)

    # Lấy tất cả org_id, rồi xáo trộn
    all_ids = list(quiz_data.keys())
    random.shuffle(all_ids)

    # Lấy ngẫu nhiên limit câu
    selected_ids = all_ids[:min(limit, len(all_ids))]

    # Sau đó sắp xếp lại theo org_id tăng dần
    selected_ids.sort()

    out: Dict[int, Dict[str, Any]] = {}
    for idx, orig_id in enumerate(selected_ids, start=1):
        q = quiz_data[orig_id]
        shuffled_options = shuffle_options(q["options"])
        out[idx] = {
            "id": idx,
            "original_id": orig_id,
            "question": q["question"],
            "options": shuffled_options,
            "scores": q.get("scores", {}),
            "quiz_type": quiz_type
        }

    return out

# Lấy assessment ranges theo quiz type
def get_assessment_ranges(quiz_type: str) -> List[Dict]:
    return ASSESSMENT_CONFIGS.get(quiz_type, ASSESSMENT_CONFIGS["peer_pressure"])

# Khởi tạo FastAPI
app = FastAPI(title="PeerSphere💗 - Student Support Platform")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
chatbot = GeminiChatBot()

# Pydantic models
class QuizAnswer(BaseModel):
    question_id: int    # original_id
    answer: str         # full text của đáp án

class QuizSubmission(BaseModel):
    answers: List[QuizAnswer]
    quiz_type: Optional[str] = "peer_pressure"  # Thêm quiz_type vào submission

class QuizResult(BaseModel):
    total_score: int
    assessment: str
    detailed_scores: Dict[int, int]
    detailed_answers: Optional[Dict[int, str]] = None
    quiz_type: str

class ChatMessage(BaseModel):
    message: str

# Quản lý WebSocket chat
class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def send(self, msg: str, ws: WebSocket):
        await ws.send_text(msg)

manager = ConnectionManager()

# --- Routes HTML ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/quiz", response_class=HTMLResponse)
async def quiz_page(request: Request, quiz_type: str = "peer_pressure"):
    # Kiểm tra quiz_type hợp lệ
    if quiz_type not in JSON_FILES:
        raise HTTPException(status_code=400, detail=f"Quiz type '{quiz_type}' không được hỗ trợ")
    
    return templates.TemplateResponse("quiz.html", {
        "request": request, 
        "quiz_type": quiz_type,
        "available_types": list(JSON_FILES.keys())
    })

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

# --- API Endpoints ---
@app.get("/api/quiz-types")
async def get_quiz_types():
    """Lấy danh sách các loại quiz có sẵn"""
    return {
        "available_types": list(JSON_FILES.keys()),
        "descriptions": {
            "peer_pressure": "Đánh giá áp lực đồng trang lứa",
            "academic_stress": "Đánh giá áp lực học tập", 
            "social_anxiety": "Đánh giá lo âu xã hội",
            "self_esteem": "Đánh giá lòng tự trọng",
            "depression": "Đánh giá tình trạng tâm lý"
        }
    }

@app.get("/api/original-questions")
async def original_questions(quiz_type: str = "peer_pressure"):
    """Lấy câu hỏi gốc theo loại quiz"""
    try:
        return load_quiz_data(quiz_type)
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/questions")
async def api_questions(quiz_type: str = "peer_pressure", limit: int = 10):
    """Lấy câu hỏi đã được xáo trộn theo loại quiz"""
    try:
        return JSONResponse(content=get_randomized_questions(quiz_type, limit))
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/chat", response_model=dict)
async def api_chat(msg: ChatMessage):
    try:
        return {"status": "success", "message": chatbot.responses(msg.message)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.websocket("/ws/chat")
async def websocket_chat(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            response = chatbot.responses(data)
            
            # Gửi từng ký tự một để tạo hiệu ứng gõ
            for char in response:
                await ws.send_text(char)
                await asyncio.sleep(0.015) 
            
            # Gửi ký tự đặc biệt để đánh dấu kết thúc tin nhắn
            await ws.send_text("\n<message_end>")
    except WebSocketDisconnect:
        manager.disconnect(ws)

@app.post("/api/submit", response_model=QuizResult)
async def submit_quiz(submission: QuizSubmission):
    quiz_type = submission.quiz_type or "peer_pressure"
    
    try:
        quiz_data = load_quiz_data(quiz_type)
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    total = 0
    detailed_scores: Dict[int,int] = {}
    detailed_answers: Dict[int,str] = {}

    for ans in submission.answers:
        qid = ans.question_id
        chosen_text = ans.answer

        if qid not in quiz_data:
            raise HTTPException(400, f"Câu hỏi ID={qid} không tồn tại trong quiz '{quiz_type}'.")

        question = quiz_data[qid]
        # Kiểm tra đáp án hợp lệ
        if chosen_text not in question["options"].values():
            raise HTTPException(400, f"Đáp án không hợp lệ cho câu hỏi {qid}.")

        # Lấy điểm
        score = question["scores"].get(chosen_text)
        if score is None or not isinstance(score, int):
            raise HTTPException(400, f"Lỗi lấy điểm cho đáp án câu hỏi {qid}.")

        # Ghi nhận
        total += score
        detailed_scores[qid] = score
        # Lưu lại letter A/B/C/D
        letter = next(k for k,v in question["options"].items() if v == chosen_text)
        detailed_answers[qid] = letter

    # Đánh giá tổng thể theo quiz type
    assessment_ranges = get_assessment_ranges(quiz_type)
    assessment = ""
    for r in assessment_ranges:
        if r["min"] <= total <= r["max"]:            
            assessment = r["assessment"]
            break

    return QuizResult(
        total_score=total,
        assessment=assessment,
        detailed_scores=detailed_scores,
        detailed_answers=detailed_answers,
        quiz_type=quiz_type
    )

@app.get("/result", response_class=HTMLResponse)
async def result_page(request: Request, score: int, assessment: str, quiz_type: str = "peer_pressure"):
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request, 
            "score": score, 
            "assessment": assessment,
            "quiz_type": quiz_type
        }
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)