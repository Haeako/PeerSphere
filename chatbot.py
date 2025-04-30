from google import genai
import os
import time

api_key = os.environ["API_KEY"]

class GeminiChatBot:
    def __init__(self):
        self.client = genai.Client(api_key=api_key)
        self.init_prompt = (
            "Bạn là một trợ lý ảo chuyên nghiệp và thân thiện dành cho sinh viên đại học. "
            "Tên của bạn là peerSphere. Bạn được tạo ra để hỗ trợ sinh viên trong mọi khía cạnh của cuộc sống đại học, "
            "từ học tập đến phát triển cá nhân. "
            "Vai trò và phong cách giao tiếp: Bạn là người bạn đồng hành đáng tin cậy, sẵn sàng trợ giúp mọi vấn đề của sinh viên. "
            "Phong cách giao tiếp thân thiện, nhiệt tình nhưng vẫn chuyên nghiệp. "
            "Sử dụng ngôn ngữ dễ hiểu, tránh thuật ngữ chuyên ngành khi không cần thiết. "
            "Luôn nhận trách nhiệm nếu không thể trả lời câu hỏi, không đưa ra thông tin sai lệch. "
            "Lĩnh vực hỗ trợ: quản lý stress, phương pháp học tập, kỹ năng mềm, định hướng nghề nghiệp, sức khỏe tinh thần. "
            "Quy tắc tương tác: Bắt đầu bằng lời chào, đặt câu hỏi mở, kết thúc bằng gợi ý tương tác. "
            "Không đưa ra lời khuyên y tế chuyên sâu. "
        )
        self.conversation_history = []

    def responses(self, prompt, max_retries=5):
        self.conversation_history.append({"role": "user", "content": prompt})
        
        formatted_history = ""
        for message in self.conversation_history:
            formatted_history += f"{message['role']}: {message['content']}\n"
        
        full_prompt = self.init_prompt + "\n\nPrevious conversation:\n" + formatted_history

        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=full_prompt
                )
                self.conversation_history.append({"role": "assistant", "content": response.text})
                return response.text
            
            except genai.errors.ServerError as e:
                print("Mình đang quá tải, đợi mình một thời gian nha... ")
                time.sleep(2 ** attempt)
            except genai.errors.PermissionDeniedError as e:
                return "Lỗi: Không có quyền truy cập model hoặc sai API key."
            except genai.errors.InvalidArgumentError as e:
                return f"Lỗi tham số không hợp lệ: {str(e)}"
            except Exception as e:
                return f"Lỗi không xác định: {str(e)}"
        
        return "Xin lỗi, hiện tại hệ thống đang quá tải. Vui lòng thử lại sau."

