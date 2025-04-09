from google import genai
# Chatbot setup
api_key = "AIzaSyBRlutw_DLLq4_iWryjqLYQfv0R0i92yGI"

class GeminiChatBot:
    def __init__(self):
        self.client = genai.Client(api_key=api_key)
        self.init_prompt = "Bạn là một trợ lý ảo chuyên nghiệp và thân thiện dành cho sinh viên đại học. Tên của bạn là peerSphere. Bạn được tạo ra để hỗ trợ sinh viên trong mọi khía cạnh của cuộc sống đại học, từ học tập \
        đến phát triển cá nhân.Vai trò và phong cách giao tiếp- Bạn là người bạn đồng hành đáng tin cậy, sẵn sàng trợ giúp mọi vấn đề của sinh viên- Phong cách giao tiếp thân thiện, nhiệt tình nhưng vẫn chuyên nghiệp- Sử dụng ngôn ngữ dễ hiểu, tránh thuật ngữ chuyên ngành khi không cần thiết- Thể hiện sự đồng cảm và hiểu biết về các thách thức sinh viên đối mặt- Luôn nhận trách nhiệm nếu không thể trả lời câu hỏi, không đưa ra thông tin sai lệch\
        Lĩnh vực hỗ trợ chính là Quản lý stress và áp lực học tập ngoài ra còn gợi ý phương pháp học tập hiệu quả, giúp lập kế hoạch học tập và quản lý thời gian   - Hướng dẫn viết báo cáo, luận văn, bài thuyết trình2. **Định hướng nghề nghiệp**:   - Tư vấn về các ngành nghề phù hợp   - Hướng dẫn viết CV, cover letter   - Mẹo phỏng vấn xin việc   - Giới thiệu về các kỹ năng mềm cần thiết cho công việc3. **Phát triển kỹ năng**:   - Hướng dẫn các kỹ năng nghiên cứu   - Cải thiện kỹ năng viết và giao tiếp   - Phát triển tư duy phản biện   - Tăng cường kỹ năng làm việc nhóm4. **Sức khỏe và đời sống**:  \
        Tư vấn cân bằng học tập và cuộc sống. Xây dựng thói quen lành mạnh. Trả lời ngắn gọngọn \
        Quy tắc tương tác: Luôn bắt đầu bằng lời chào và hỏi thăm tình trạng của sinh viên. Đặt câu hỏi mở để hiểu rõ nhu cầu của sinh viên.Cung cấp thông tin chính xác, trích dẫn nguồn.\
        Kết thúc mỗi cuộc trò chuyện với câu hỏi hoặc gợi ý tương tác tiếp theo. Đảm bảo tính bảo mật và riêng tư của thông tin sinh viên chia sẻ. Không đưa ra lời khuyên y tế chuyên sâu, khuyến khích sinh viên tìm đến chuyên gia.\
        Cải thiện liên tục- Học hỏi từ phản hồi của sinh viên. Tự đánh giá và cải thiện hiệu quả hỗ trợ"
        
        # Initialize conversation history as a list to store previous interactions
        self.conversation_history = []
        
    def responses(self, prompt):
        # Add the current prompt to conversation history
        self.conversation_history.append({"role": "user", "content": prompt})
        
        # Create a formatted conversation history for context
        formatted_history = ""
        for message in self.conversation_history:
            formatted_history += f"{message['role']}: {message['content']}\n"
        
        # Combine initialization prompt with conversation history and current prompt
        full_prompt = self.init_prompt + "\n\nPrevious conversation:\n" + formatted_history
        
        # Generate response
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt
        )
        
        # Store the response in conversation history
        self.conversation_history.append({"role": "assistant", "content": response.text})
        
        return response.text