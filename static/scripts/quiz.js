document.addEventListener("DOMContentLoaded", function() {
  let currentQuestion = 0;
  let answers = {};
  let questions = [];

  // Lấy dữ liệu câu hỏi từ API
  async function loadQuestions() {
    try {
      const quizContainer = document.getElementById("quiz-container");
      
      // Hiệu ứng đang tải
      quizContainer.innerHTML = `
        <div class="loading">
          <div class="spinner"></div>
          <p>Đang tải câu hỏi...</p>
        </div>
      `;
      
      const response = await fetch("/api/questions");
      if (!response.ok) throw new Error("Không thể tải câu hỏi từ server");
      let data = await response.json();
      
      // Nếu data trả về dạng object, chuyển đổi thành mảng
      if (!Array.isArray(data)) {
        data = Object.keys(data)
                     .sort((a, b) => a - b)
                     .map(key => data[key]);
      }
      questions = data;
      
      // Hiển thị câu hỏi đầu tiên với animation fade in
      quizContainer.innerHTML = '';
      showQuestion();
      
      // Thêm hiệu ứng hover khi mới vào trang
      quizContainer.classList.add('initial-hover');
      setTimeout(() => {
        quizContainer.classList.remove('initial-hover');
      }, 1500);
      
    } catch (error) {
      document.getElementById("quiz-container").innerHTML = `
        <div class="error-message">
          <p>Lỗi: ${error.message}</p>
          <button class="btn-nav" onclick="location.reload()">Thử lại</button>
        </div>
      `;
    }
  }

  // Hiển thị câu hỏi với animation
  function showQuestion() {
    const quizContainer = document.getElementById("quiz-container");
    
    // Nếu hết câu hỏi, hiển thị nút nộp bài
    if (currentQuestion >= questions.length) {
      const completionContent = `
        <div class="completion-screen">
          <h2>Hoàn thành!</h2>
          <div class="progress-container">
            <div class="progress">
              <div class="progress-bar" style="width: 100%"></div>
            </div>
            <p>${questions.length} / ${questions.length}</p>
          </div>
          <button class="btn-submit" onclick="submitQuiz()">Nộp bài</button>
        </div>
      `;
      
      // Thêm div mới với animation slide-in
      const newDiv = document.createElement('div');
      newDiv.className = 'question-slide slide-in';
      newDiv.innerHTML = completionContent;
      
      // Xóa div hiện tại với animation slide-out
      const currentSlide = document.querySelector('.question-slide');
      if (currentSlide) {
        currentSlide.classList.add('slide-out');
        setTimeout(() => {
          currentSlide.remove();
          quizContainer.appendChild(newDiv);
        }, 300);
      } else {
        quizContainer.appendChild(newDiv);
      }
      
      return;
    }

    const q = questions[currentQuestion];
    const questionId = q.id || currentQuestion;
    
    // Tính phần trăm tiến độ
    const progressPercent = ((currentQuestion + 1) / questions.length) * 100;
    
    // Tạo HTML cho các option
    const optionsHTML = Object.entries(q.options).map(([key, value]) => {
      const isChecked = answers[questionId] === key ? 'checked' : '';
      return `
        <label class="option-label">
          <input type="radio" name="answer" value="${key}" ${isChecked}>
          <span class="option-text">${key}: ${value}</span>
        </label>
      `;
    }).join('');

    // Tạo HTML cho câu hỏi
    const questionContent = `
      <div class="progress-container">
        <div class="progress">
          <div class="progress-bar" style="width: ${progressPercent}%"></div>
        </div>
        <p>${currentQuestion + 1} / ${questions.length}</p>
      </div>
      
      <h3 class="question-title">${q.question}</h3>
      
      <div class="options-container">
        ${optionsHTML}
      </div>
      
      <div class="nav-buttons">
        ${currentQuestion > 0 ? '<button class="btn-nav" onclick="prevQuestion()">Trước</button>' : ''}
        <button class="btn-nav" onclick="nextQuestion()">${currentQuestion === questions.length - 1 ? "Nộp bài" : "Tiếp theo"}</button>
      </div>
    `;
    
    // Tạo div mới với animation slide-in
    const newDiv = document.createElement('div');
    newDiv.className = 'question-slide slide-in';
    newDiv.innerHTML = questionContent;
    
    // Xóa div hiện tại với animation slide-out
    const currentSlide = document.querySelector('.question-slide');
    if (currentSlide) {
      currentSlide.classList.add('slide-out');
      setTimeout(() => {
        currentSlide.remove();
        quizContainer.appendChild(newDiv);
      }, 300); // Thời gian của animation slide-out
    } else {
      quizContainer.appendChild(newDiv);
    }
  }

  // Chuyển sang câu hỏi trước với animation
  window.prevQuestion = function() {
    if (currentQuestion > 0) {
      // Thêm class slide-out-reverse để animation ngược lại
      const currentSlide = document.querySelector('.question-slide');
      if (currentSlide) {
        currentSlide.classList.add('slide-out-reverse');
        
        setTimeout(() => {
          currentSlide.remove();
          currentQuestion--;
          
          // Tạo div mới với class slide-in-reverse
          const quizContainer = document.getElementById("quiz-container");
          const newDiv = document.createElement('div');
          newDiv.className = 'question-slide slide-in-reverse';
          
          // Sử dụng showQuestion để tạo nội dung, sau đó thay thế class
          const tempContainer = document.createElement('div');
          tempContainer.id = 'temp-container';
          document.body.appendChild(tempContainer);
          
          const originalContainer = document.getElementById('quiz-container');
          const originalId = originalContainer.id;
          originalContainer.id = 'original-container';
          tempContainer.id = 'quiz-container';
          
          showQuestion();
          
          const newContent = tempContainer.innerHTML;
          tempContainer.remove();
          
          originalContainer.id = originalId;
          newDiv.innerHTML = newContent;
          quizContainer.appendChild(newDiv);
          
          // Xóa class slide-in và thay bằng slide-in-reverse
          const innerSlide = newDiv.querySelector('.question-slide');
          if (innerSlide) {
            const content = innerSlide.innerHTML;
            newDiv.innerHTML = content;
          }
        }, 300);
      }
    }
  };

  // Xử lý khi chuyển câu hỏi tiếp theo
  window.nextQuestion = function() {
    const selected = document.querySelector("input[name='answer']:checked");
    if (!selected) {
      // Hiệu ứng rung lắc nếu chưa chọn câu trả lời
      const optionsContainer = document.querySelector('.options-container');
      optionsContainer.classList.add('shake');
      
      setTimeout(() => {
        optionsContainer.classList.remove('shake');
      }, 500);
      
      // Hiển thị thông báo lỗi
      if (!document.querySelector('.error-message')) {
        const errorMsg = document.createElement('p');
        errorMsg.className = 'error-message';
        errorMsg.textContent = 'Vui lòng chọn câu trả lời!';
        document.querySelector('.nav-buttons').before(errorMsg);
        
        // Tự động xóa thông báo sau 3 giây
        setTimeout(() => {
          errorMsg.remove();
        }, 3000);
      }
      
      return;
    }
    
    // Lưu câu trả lời
    const questionId = questions[currentQuestion].id || currentQuestion;
    answers[questionId] = selected.value;
    
    // Chuyển sang câu tiếp theo
    currentQuestion++;
    showQuestion();
  };

  // Hàm gửi bài làm đến endpoint submit
  window.submitQuiz = async function() {
    try {
      // Hiển thị loading
      const quizContainer = document.getElementById("quiz-container");
      quizContainer.innerHTML = `
        <div class="submitting">
          <div class="spinner"></div>
          <p>Đang nộp bài...</p>
        </div>
      `;
      
      const payload = {
        answers: Object.entries(answers).map(([id, answer]) => ({
          question_id: parseInt(id),
          answer: answer
        }))
      };
      
      const response = await fetch("/api/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) throw new Error("Nộp bài không thành công");
      const result = await response.json();
      
      // Hiển thị thành công trước khi chuyển trang
      quizContainer.innerHTML = `
        <div class="success-message">
          <div class="success-icon">✓</div>
          <p>Nộp bài thành công!</p>
          <p>Đang chuyển hướng...</p>
        </div>
      `;
      
      // Chuyển hướng sau 1.5 giây
      setTimeout(() => {
        window.location.href = `/result?score=${result.total_score}&assessment=${encodeURIComponent(result.assessment)}`;
      }, 1500);
      
    } catch (error) {
      document.getElementById("quiz-container").innerHTML = `
        <div class="error-message">
          <p>Lỗi khi nộp bài: ${error.message}</p>
          <button class="btn-nav" onclick="submitQuiz()">Thử lại</button>
        </div>
      `;
    }
  };

  loadQuestions();
});