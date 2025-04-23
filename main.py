from fastapi import FastAPI, Request, Form, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import json
import random
from chatbot import *
from quiz_data import *

# hehe
app = FastAPI(title="PeerSphere - Student Support Platform")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Define models
class QuizAnswer(BaseModel):
    question_id: int
    answer: str  # 'A', 'B', 'C', or 'D'

class QuizSubmission(BaseModel):
    answers: List[QuizAnswer]

# Cập nhật model Pydantic để hỗ trợ detailed_answers
class QuizResult(BaseModel):
    total_score: int
    assessment: str
    detailed_scores: Dict[int, int]
    detailed_answers: Optional[Dict[int, str]] = None


class ChatMessage(BaseModel):
    message: str


# Create chatbot instance
chatbot = GeminiChatBot()

# Assessment scoring ranges
assessment_ranges = [
    {"min": 25, "max": 30, "assessment": "Bạn kiểm soát rất tốt áp lực đồng trang lứa."},
    {"min": 18, "max": 24, "assessment": "Bạn có một số áp lực nhưng vẫn giữ được sự cân bằng."},
    {"min": 10, "max": 17, "assessment": "Bạn đang bị ảnh hưởng đáng kể bởi áp lực đồng trang lứa."},
    {"min": 0, "max": 9, "assessment": "Bạn có thể đang chịu áp lực lớn và cần tìm cách giải tỏa."}
]

# WebSocket connection manager for chat
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

# Hàm randomize câu hỏi và đáp án (giữ nguyên kí tự A, B, C, D)
# Hàm randomize câu hỏi và đáp án (giữ nguyên điểm số)
def get_randomized_questions():
    # Tạo bản sao của quiz_questions để không ảnh hưởng dữ liệu gốc
    questions_copy = {k: v.copy() for k, v in quiz_questions.items()}
    
    # Lấy danh sách các ID câu hỏi
    question_ids = list(questions_copy.keys())
    
    # Trộn ngẫu nhiên thứ tự các ID câu hỏi
    random.shuffle(question_ids)
    
    # Giới hạn số lượng câu hỏi là 10 (nếu có hơn 10 câu)
    if len(question_ids) > 10:
        question_ids = question_ids[:10]
    
    # Tạo dict mới với thứ tự câu hỏi đã trộn
    randomized_questions = {}
    
    for index, q_id in enumerate(question_ids, 1):
        # Lấy câu hỏi từ bản gốc
        question_data = questions_copy[q_id].copy()
        
        # Đưa câu hỏi vào dict kết quả
        randomized_questions[index] = question_data
        randomized_questions[index]["id"] = index  # Cập nhật ID câu hỏi
    
    return randomized_questions

# Routes

@app.get("/api/original-questions")
async def get_original_questions():
    return quiz_questions

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/quiz", response_class=HTMLResponse)
async def quiz_page(request: Request):
    return templates.TemplateResponse("quiz.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/api/questions")
async def get_questions():
    # Lấy câu hỏi đã trộn ngẫu nhiên
    randomized_questions = get_randomized_questions()
    return JSONResponse(content=randomized_questions)

@app.post("/api/chat", response_model=dict)
async def chat_endpoint(message: ChatMessage):
    try:
        response = chatbot.responses(message.message)
        return {"status": "success", "message": response}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            
            # Process the message through the chatbot
            response = chatbot.responses(data)
            
            # Send the response back
            await manager.send_message(response, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/submit", response_model=QuizResult)
async def submit_quiz(submission: QuizSubmission):
    # Calculate score
    total_score = 0
    detailed_scores = {}
    detailed_answers = {}
    
    for answer in submission.answers:
        original_question_id = answer.question_id
        
        if original_question_id not in quiz_questions:
            raise HTTPException(status_code=400, detail=f"Invalid question ID: {original_question_id}")
        
        # Lấy câu hỏi gốc
        original_question = quiz_questions[original_question_id]
        
        # Tìm điểm số của câu trả lời
        # Tìm key của đáp án dựa trên nội dung đáp án
        answer_key = next(
            (key for key, value in original_question['options'].items() 
             if value == answer.answer), 
            None
        )
        
        if answer_key is None:
            raise HTTPException(status_code=400, detail=f"Invalid answer for question {original_question_id}")
        
        # Lấy điểm từ scores của câu hỏi gốc
        answer_score = original_question['scores'][answer.answer]
        
        total_score += answer_score
        detailed_scores[original_question_id] = answer_score
        detailed_answers[original_question_id] = answer_key  # Lưu key A, B, C, D
    
    # Determine assessment
    assessment = ""
    for range_info in assessment_ranges:
        if range_info["min"] <= total_score <= range_info["max"]:
            assessment = range_info["assessment"]
            break
    
    return QuizResult(
        total_score=total_score,
        assessment=assessment,
        detailed_scores=detailed_scores,
        detailed_answers=detailed_answers
    )

@app.get("/result", response_class=HTMLResponse)
async def result_page(request: Request, score: int, assessment: str, detailed_scores: Optional[str] = None, detailed_answers: Optional[str] = None):
    context = {
        "request": request, 
        "score": score, 
        "assessment": assessment
    }
    
    # Xử lý detailed_scores nếu được truyền
    if detailed_scores:
        try:
            context["detailed_scores"] = json.loads(detailed_scores)
        except:
            pass
    
    # Xử lý detailed_answers nếu được truyền
    if detailed_answers:
        try:
            context["detailed_answers"] = json.loads(detailed_answers)
        except:
            pass
    elif detailed_scores:
        # Nếu chỉ có detailed_scores, thử lấy từ localStorage
        context["detailed_answers"] = {
            1: "Chúc mừng họ và xem đó là động lực để cố gắng hơn.",
            2: "Tôi sẽ cân nhắc tham gia nếu thấy phù hợp với bản thân.",
            3: "Hiểu rằng đó chỉ là một phần cuộc sống của họ và không ảnh hưởng đến mình.",
            4: "Hiểu rằng mỗi người có một con đường riêng và tập trung vào mục tiêu của mình.",
            5: "Tìm hiểu xem có công việc nào phù hợp với mình không.",
            6: "Chỉ tham gia nếu không ảnh hưởng đến tài chính cá nhân.",
            7: "Học hỏi từ họ nhưng vẫn giữ vững con đường riêng của mình.",
            8: "Vẫn tận hưởng cuộc sống độc thân và chờ duyên đến.",
            9: "Cố gắng học hỏi và cải thiện kỹ năng của bản thân.",
            10: "Chúc mừng họ và không để nó ảnh hưởng đến mình."
        }
            
    return templates.TemplateResponse("result.html", context)

# Form submission endpoint (alternative to JSON API)
@app.post("/submit-form", response_class=HTMLResponse)
async def submit_form(request: Request):
    form_data = await request.form()
    
    # Process form data
    total_score = 0
    detailed_scores = {}
    
    for question_id in range(1, len(quiz_questions) + 1):
        answer_key = form_data.get(f"question_{question_id}")
        
        if not answer_key:
            return templates.TemplateResponse(
                "quiz.html", 
                {
                    "request": request, 
                    "questions": quiz_questions,
                    "error": "Vui lòng trả lời tất cả các câu hỏi"
                }
            )
        
        score = quiz_questions[question_id]["scores"][answer_key]
        total_score += score
        detailed_scores[question_id] = score
    
    # Determine assessment
    assessment = ""
    for range_info in assessment_ranges:
        if range_info["min"] <= total_score <= range_info["max"]:
            assessment = range_info["assessment"]
            break
    
    return templates.TemplateResponse(
        "result.html", 
        {
            "request": request, 
            "score": total_score, 
            "assessment": assessment,
            "detailed_scores": detailed_scores  # Biến này đã được truyền đúng cách
        }
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)