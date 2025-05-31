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
    "study": "data/study.json",
    "finace": "data/taichinh.json", 
    "nghinh": "data/nghinh.json",
    "hobby": "data/sothich.json",
    "lifestyle": "data/mck.json"
}

# Assessment ranges cho từng loại quiz
ASSESSMENT_CONFIGS = {
    "study": [
        {
            "min": 27, "max": 30,
            "meaning": "Rất thấp",
            "assessment": "Bạn kiểm soát rất tốt áp lực đồng trang lứa.",
            "advice": [
                "Duy trì sự tự tin và thái độ tích cực về bản thân.",
                "Truyền cảm hứng, hỗ trợ bạn bè xây dựng hình ảnh tích cực.",
                "Chia sẻ quan điểm về vẻ đẹp đa dạng, không khuôn mẫu."
            ]
        },
        {
            "min": 20, "max": 26,
            "meaning": "Thấp",
            "assessment": "Bạn có một số áp lực nhưng vẫn giữ được sự cân bằng.",
            "advice": [
                "Tự nâng cao nhận thức về giá trị bản thân không chỉ qua ngoại hình.",
                "Học cách bảo vệ cảm xúc khi tiếp nhận các bình luận về ngoại hình.",
                "Tập trung phát triển kỹ năng, sở thích cá nhân để tăng tự tin."
            ]
        },
        {
            "min": 10, "max": 19,
            "meaning": "Trung bình",
            "assessment": "Bạn đang bị ảnh hưởng đáng kể bởi áp lực đồng trang lứa.",
            "advice": [
                "Tập luyện kỹ năng tự chấp nhận và yêu thương bản thân.",
                "Tránh so sánh tiêu cực, thực hành mindfulness hoặc thiền.",
                "Tìm sự hỗ trợ từ gia đình, bạn bè hoặc chuyên gia tâm lý khi cần.",
                "Tham gia các hoạt động giúp nâng cao hình ảnh bản thân."
            ]
        },
        {
            "min": 0, "max": 9,
            "meaning": "Cao",
            "assessment": "Bạn có thể đang chịu áp lực lớn và cần tìm cách giải tỏa.",
            "advice": [
                "Tìm kiếm hỗ trợ tâm lý chuyên nghiệp hoặc tư vấn.",
                "Thực hiện các phương pháp chăm sóc sức khỏe tâm thần như thiền, yoga, tập thể dục.",
                "Giới hạn tiếp xúc với mạng xã hội hoặc các nguồn gây áp lực.",
                "Đặt mục tiêu cải thiện ngoại hình lành mạnh, tránh áp lực tiêu cực.",
                "Xây dựng môi trường sống tích cực, được khích lệ và hỗ trợ."
            ]
        }
    ],
    "finace": [
        {
            "min": 27, "max": 30,
            "meaning": "Rất thấp",
            "assessment": "Bạn rất tự tin, không bị áp lực về tài chính khi so sánh với bạn bè.",
            "advice": [
                "Duy trì tư duy tích cực và thái độ hài lòng với hiện tại.",
                "Chia sẻ kinh nghiệm quản lý tài chính cá nhân với bạn bè.",
                "Hỗ trợ bạn bè khi họ gặp khó khăn tài chính nếu có thể."
            ]
        },
        {
            "min": 20, "max": 26,
            "meaning": "Thấp",
            "assessment": "Bạn có chút áp lực nhưng biết cách kiểm soát và không ảnh hưởng nhiều đến tâm trạng.",
            "advice": [
                "Tiếp tục duy trì thói quen lập kế hoạch chi tiêu hợp lý.",
                "Tìm hiểu thêm kỹ năng quản lý tài chính cá nhân.",
                "Học cách so sánh tích cực, lấy bạn bè làm động lực chứ không phải áp lực.",
                "Trao đổi, chia sẻ cảm xúc với người thân hoặc bạn bè tin cậy."
            ]
        },
        {
            "min": 10, "max": 19,
            "meaning": "Trung bình",
            "assessment": "Bạn cảm thấy áp lực khá nhiều về tài chính, đôi khi bị ảnh hưởng tâm lý.",
            "advice": [
                "Xây dựng ngân sách chi tiêu chi tiết để kiểm soát tài chính.",
                "Học các kỹ năng kiếm thêm thu nhập như làm thêm hoặc kinh doanh nhỏ.",
                "Tham gia các nhóm hỗ trợ tinh thần hoặc tư vấn tâm lý nếu cảm thấy quá căng thẳng.",
                "Tập trung phát triển kỹ năng bản thân để tăng cơ hội nghề nghiệp.",
                "Hạn chế so sánh tiêu cực với bạn bè, tập trung vào điểm mạnh của mình."
            ]
        },
        {
            "min": 0, "max": 9,
            "meaning": "Cao",
            "assessment": "Bạn bị áp lực tài chính đồng trang lứa lớn, có thể ảnh hưởng xấu đến tinh thần và tự tin.",
            "advice": [
                "Tìm kiếm sự tư vấn chuyên nghiệp về quản lý tài chính hoặc tâm lý.",
                "Ưu tiên chăm sóc sức khỏe tâm thần: thiền, tập thể dục, nghỉ ngơi hợp lý.",
                "Học cách nói “không” với các chi tiêu không cần thiết để giảm áp lực.",
                "Xác định mục tiêu tài chính ngắn hạn, dễ đạt được để tạo động lực.",
                "Tham gia các khóa học kỹ năng mềm, phát triển nghề nghiệp để cải thiện thu nhập.",
                "Tìm kiếm sự hỗ trợ từ gia đình, bạn bè hoặc cộng đồng khi cần."
            ]
        }
    ],
    "nghinh": [
        {
            "min": 27, "max": 30,
            "meaning": "Rất thấp",
            "assessment": "Bạn rất tự tin về ngoại hình, ít bị áp lực từ bạn bè.",
            "advice": [
                "Duy trì sự tự tin và thái độ tích cực về bản thân.",
                "Truyền cảm hứng, hỗ trợ bạn bè xây dựng hình ảnh tích cực.",
                "Chia sẻ quan điểm về vẻ đẹp đa dạng, không khuôn mẫu."
            ]
        },
        {
            "min": 20, "max": 26,
            "meaning": "Thấp",
            "assessment": "Bạn có chút áp lực nhưng kiểm soát tốt cảm xúc và hình ảnh của mình.",
            "advice": [
                "Tự nâng cao nhận thức về giá trị bản thân không chỉ qua ngoại hình.",
                "Học cách bảo vệ cảm xúc khi tiếp nhận các bình luận về ngoại hình.",
                "Tập trung phát triển kỹ năng, sở thích cá nhân để tăng tự tin."
            ]
        },
        {
            "min": 10, "max": 19,
            "meaning": "Trung bình",
            "assessment": "Bạn chịu áp lực khá nhiều, có lúc cảm thấy thiếu tự tin về ngoại hình.",
            "advice": [
                "Tập luyện kỹ năng tự chấp nhận và yêu thương bản thân.",
                "Tránh so sánh tiêu cực, thực hành mindfulness hoặc thiền.",
                "Tìm sự hỗ trợ từ gia đình, bạn bè hoặc chuyên gia tâm lý khi cần.",
                "Tham gia các hoạt động giúp nâng cao hình ảnh bản thân."
            ]
        },
        {
            "min": 0, "max": 9,
            "meaning": "Cao",
            "assessment": "Bạn chịu áp lực lớn, có thể ảnh hưởng tiêu cực đến sức khỏe tâm thần.",
            "advice": [
                "Tìm kiếm hỗ trợ tâm lý chuyên nghiệp hoặc tư vấn.",
                "Thực hiện các phương pháp chăm sóc sức khỏe tâm thần như thiền, yoga, tập thể dục.",
                "Giới hạn tiếp xúc với mạng xã hội hoặc các nguồn gây áp lực.",
                "Đặt mục tiêu cải thiện ngoại hình lành mạnh, tránh áp lực tiêu cực.",
                "Xây dựng môi trường sống tích cực, được khích lệ và hỗ trợ."
            ]
        }
    ],
    "hobby": [
        {
            "min": 27, "max": 30,
            "meaning": "Rất thấp",
            "assessment": "Bạn rất tự tin với sở thích và thói quen của mình, không bị áp lực từ bạn bè.",
            "advice": [
                "Duy trì sự tự tin và thái độ tích cực.",
                "Khuyến khích sự đa dạng và khác biệt trong nhóm bạn.",
                "Chia sẻ và học hỏi từ sự khác biệt của nhau."
            ]
        },
        {
            "min": 20, "max": 26,
            "meaning": "Thấp",
            "assessment": "Bạn có chút áp lực nhưng kiểm soát tốt và duy trì sự cân bằng.",
            "advice": [
                "Giữ vững sở thích cá nhân đồng thời linh hoạt khi cần.",
                "Thể hiện quan điểm rõ ràng và biết cách từ chối lịch sự.",
                "Giao tiếp cởi mở với bạn bè về sở thích của mình."
            ]
        },
        {
            "min": 10, "max": 19,
            "meaning": "Trung bình",
            "assessment": "Bạn chịu áp lực khá nhiều và đôi khi cảm thấy khó khăn với sự khác biệt.",
            "advice": [
                "Thực hành kỹ năng chấp nhận bản thân và sự khác biệt.",
                "Tránh so sánh tiêu cực, tập trung phát triển cá nhân.",
                "Tìm sự hỗ trợ từ bạn bè thân thiết hoặc chuyên gia khi cần.",
                "Tham gia các hoạt động giúp nâng cao sự tự tin và kỹ năng xã hội."
            ]
        },
        {
            "min": 0, "max": 9,
            "meaning": "Cao",
            "assessment": "Bạn bị áp lực lớn, cảm thấy khó hòa nhập và thiếu tự tin với sở thích, thói quen cá nhân.",
            "advice": [
                "Tìm kiếm tư vấn tâm lý hoặc tham gia nhóm hỗ trợ.",
                "Thực hành chăm sóc sức khỏe tâm thần như thiền, thể dục.",
                "Học cách đặt giới hạn và nói “không” khi cần.",
                "Tìm kiếm môi trường, nhóm bạn phù hợp với mình hơn.",
                "Đặt mục tiêu phát triển bản thân theo cách lành mạnh và tích cực."
            ]
        }
    ],
    "lifestyle": [
        {
            "min": 27, "max": 30,
            "meaning": "Rất thấp",
            "assessment": "Bạn rất tự tin với phong cách sống cá nhân, ít bị áp lực từ bạn bè.",
            "advice": [
                "Duy trì sự tự tin và thái độ tích cực.",
                "Khuyến khích sự đa dạng và tôn trọng phong cách khác nhau.",
                "Chia sẻ và học hỏi từ sự khác biệt của nhau."
            ]
        },
        {
            "min": 20, "max": 26,
            "meaning": "Thấp",
            "assessment": "Bạn có chút áp lực nhưng kiểm soát tốt cảm xúc và giữ sự cân bằng.",
            "advice": [
                "Giữ vững quan điểm cá nhân đồng thời linh hoạt khi cần.",
                "Giao tiếp cởi mở và rõ ràng với bạn bè.",
                "Thể hiện sự tôn trọng và đặt giới hạn khi cần."
            ]
        },
        {
            "min": 10, "max": 19,
            "meaning": "Trung bình",
            "assessment": "Bạn chịu áp lực khá nhiều và đôi khi khó giữ vững bản thân.",
            "advice": [
                "Thực hành kỹ năng chấp nhận bản thân và sự khác biệt.",
                "Tập trung phát triển cá nhân, tránh so sánh tiêu cực.",
                "Tìm hỗ trợ từ bạn bè thân thiết hoặc chuyên gia khi cần.",
                "Tham gia các hoạt động nâng cao tự tin và kỹ năng xã hội."
            ]
        },
        {
            "min": 0, "max": 9,
            "meaning": "Cao",
            "assessment": "Bạn bị áp lực lớn, cảm thấy khó hòa nhập và thiếu tự tin.",
            "advice": [
                "Tìm kiếm tư vấn tâm lý hoặc nhóm hỗ trợ.",
                "Thực hành chăm sóc sức khỏe tâm thần như thiền, thể dục.",
                "Học cách đặt giới hạn và nói “không”.",
                "Tìm môi trường bạn bè phù hợp và tích cực.",
                "Đặt mục tiêu phát triển bản thân theo cách lành mạnh."
            ]
        }
    ]
}

# Hàm load dữ liệu từ JSON với option
def load_quiz_data(quiz_type: str = "study") -> Dict[int, dict]:
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
def get_randomized_questions(quiz_type: str = "study", limit: int = 10) -> Dict[int, Dict[str, Any]]:
    quiz_data: Dict[int, dict] = load_quiz_data(quiz_type)

    # Lấy tất cả org_id, rồi xáo trộn
    all_ids = list(quiz_data.keys())
    random.shuffle(all_ids)

    # Lấy ngẫu nhiên limit câu
    selected_ids = all_ids[:min(limit, len(all_ids))]

    # BỎ DÒNG NÀY NẾU MUỐN THỨ TỰ CÂU HỎI CHỌN RA CŨNG NGẪU NHIÊN
    # selected_ids.sort() # <<<< BỎ DÒNG NÀY

    out: Dict[int, Dict[str, Any]] = {}
    # idx sẽ là 1, 2, 3,... theo thứ tự trong selected_ids (đã được shuffle hoặc shuffle rồi sort)
    for idx, orig_id in enumerate(selected_ids, start=1):
        q = quiz_data[orig_id]
        shuffled_options = shuffle_options(q["options"])
        out[idx] = {
            "id": idx, # Đây là ID mới của câu hỏi trong quiz hiện tại (1, 2, 3,...)
            "original_id": orig_id, # Đây là ID gốc của câu hỏi trong file JSON
            "question": q["question"],
            "options": shuffled_options,
            "scores": q.get("scores", {}),
            "quiz_type": quiz_type
        }

    return out

# Lấy assessment ranges theo quiz type
def get_assessment_ranges(quiz_type: str) -> List[Dict]:
    return ASSESSMENT_CONFIGS.get(quiz_type, [])

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
    quiz_type: Optional[str] = "study"  # Thêm quiz_type vào submission

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
async def quiz_page(request: Request, quiz_type: str = "study"):
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
            "study": "Đánh giá áp lực học tập",
            "finace": "Đánh giá áp lực về tài chính", 
            "nghinh": "Đánh giá áp lực về ngoại hình",
            "hobby": "Đánh giá áp lực về sở thích",
            "lifestyle": "Đánh giá áp lực về phong cách sống"
        }
    }

@app.get("/api/original-questions")
async def original_questions(quiz_type: str = "study"):
    """Lấy câu hỏi gốc theo loại quiz"""
    try:
        return load_quiz_data(quiz_type)
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/questions")
async def api_questions(quiz_type: str = "study", limit: int = 10):
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
    quiz_type = submission.quiz_type or "study"
    
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
async def result_page(request: Request, score: int, assessment: str, quiz_type: str = "study"):
    assessment_ranges = ASSESSMENT_CONFIGS.get(quiz_type, [])
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "score": score,
            "assessment": assessment,
            "quiz_type": quiz_type,
            "assessment_ranges": assessment_ranges
        }
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)