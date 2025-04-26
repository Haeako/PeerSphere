# PeerSphere

<div id="vietnamese-version">

# 🇻🇳 Tiếng Việt

## 🔖 Giới Thiệu

Chắc hẳn ai trong chúng ta cũng từng chịu rất nhiều áp lực. Những áp lực ấy có thể đến từ rất nhiều hướng: gia đình, đồng nghiệp và đặc biệt là bạn bè đồng trang lứa. Chúng ta có hẳn một hiện tượng tâm lý - xã hội gọi là ***áp lực đồng trang lứa (peer pressure)***. Đây là một hành vi khi chúng ta cố gắng thay đổi bản thân để bắt kịp các bạn bè hoặc cộng đồng xung quanh. Điều này diễn ra đặc biệt thường xuyên khi chúng ta bước vào một môi trường mới. Đó là lúc mà chúng ta cảm nhận được rõ ràng nhất ***áp lực đồng trang lứa***.

> Nhóm thực hiện project này đã từng trải qua cảm giác đó và hiểu được việc hiểu bản thân đang mắc kẹt ở tình trạng này ở hướng tốt hay xấu và giải pháp để cải thiện bản thân.

## 📖 Nội Dung

PeerSphere website được xây dựng nên với 2 tính năng chính để hỗ trợ cho các bạn sinh viên: Bài test kiểm tra mức độ `áp lực đồng trang lứa` và một con `chatbot AI`.

### ⭐ Bài test kiểm tra

Đây là một bài kiểm tra nhanh với số lượng câu hỏi gồm 10 câu được lấy ra từ ngân hàng câu hỏi mà chúng mình đã chuẩn bị. Mỗi câu hỏi đều có chức năng đánh giá một khía cạnh nào đó đối với tình trạng áp lực đồng trang lứa của sinh viên và mỗi câu trả lời tương ứng với câu hỏi sẽ có một mức điểm cụ thể. Sau khi trả lời hết 10 câu thì sẽ có điểm tổng hợp để đánh giá tình trạng của người làm theo mức độ của từng khung điểm.

<div align="center">
  <img src="https://github.com/user-attachments/assets/8930b6d8-68ea-495d-8f00-240ee97ca45a" alt="Bài Test" width="600">
  <br>
  <img src="https://github.com/user-attachments/assets/82f00831-99e4-4caa-a9f6-281105dcb82e" alt="Kết Quả" width="600">
</div>

### ⭐ Chatbot AI 

Đây là một con trí tuệ nhân tạo được nhóm xây dựng với khả năng như một chuyên gia tâm lý, có thể trò chuyện và tâm sự với người dùng như một người bạn. Ngoài ra, chatbot cũng có kiến thức về lĩnh vực tâm lý và sẵn sàng trả lời những câu hỏi mà người dùng thắc mắc.

<div align="center">
  <img src="https://github.com/user-attachments/assets/101a2cc6-bfe4-420f-8a69-aacae87867f9" alt="Chatbot" width="600">
</div>

## ⚙️ Cài Đặt

### Yêu cầu:
- Python: `3.12.x`

### Cài đặt API Key:
Thiết lập API Key của bạn vào biến môi trường:

**Linux/macOS:**
```bash
export API_KEY="INSERT_HERE"
```

**Windows:**
```powershell
$env:API_KEY="INSERT_HERE"
```

### Cài đặt thư viện:
```bash
pip install -r requirement.txt
```

### Chạy ứng dụng:
```bash
uvicorn main:app --reload
```

> Cuối cùng, nhóm thực hiện hy vọng các bạn sẽ enjoy hết mức với trang web của chúng mình!

</div>

<hr>

<div id="english-version">

# 🇬🇧 English

## 🔖 Introduction

Each of us has experienced various pressures in life. These pressures can come from many directions: family, colleagues, and especially from our peers. This psychological and social phenomenon is called ***peer pressure***. It's a behavior where we try to change ourselves to keep up with friends or surrounding communities. This occurs especially frequently when we enter a new environment - that's when we feel ***peer pressure*** most intensely.

> Our project team has experienced these feelings firsthand and understands the importance of recognizing whether this pressure leads to positive or negative outcomes, and finding solutions for self-improvement.

## 📖 Content

The peerSphere website is built with two main features to support students: A `peer pressure assessment test` and an `AI chatbot`.

### ⭐ Assessment Test

This is a quick test consisting of 10 questions drawn from our prepared question bank. Each question evaluates a specific aspect of peer pressure experienced by students, with each answer corresponding to a specific score. After answering all 10 questions, participants receive a total score that evaluates their situation based on predefined scoring ranges.

<div align="center">
  <img src="https://github.com/user-attachments/assets/8930b6d8-68ea-495d-8f00-240ee97ca45a" alt="Assessment Test" width="600">
  <br>
  <img src="https://github.com/user-attachments/assets/82f00831-99e4-4caa-a9f6-281105dcb82e" alt="Results" width="600">
</div>

### ⭐ AI Chatbot

This is an artificial intelligence created by our team with capabilities similar to a psychologist, able to chat and connect with users as a friend. Additionally, the chatbot has knowledge in the field of psychology and is ready to answer questions that users may have.

<div align="center">
  <img src="https://github.com/user-attachments/assets/101a2cc6-bfe4-420f-8a69-aacae87867f9" alt="Chatbot" width="600">
</div>

## ⚙️ Setup

### Requirements:
- Python: `3.12.x`

### API Key Setup:
Set your API Key as an environment variable:

**Linux/macOS:**
```bash
export API_KEY="INSERT_HERE"
```

**Windows:**
```powershell
$env:API_KEY="INSERT_HERE"
```

### Install Dependencies:
```bash
pip install -r requirement.txt
```

### Run Application:
```bash
uvicorn main:app --reload
```

> Finally, our team hopes you'll fully enjoy our website!

</div>