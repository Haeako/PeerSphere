document.addEventListener('DOMContentLoaded', function() {
    const chatBox = document.getElementById('chatMessages');
    const userInput = document.getElementById('userMessage');
    const sendButton = document.getElementById('sendButton');
    const typingIndicator = document.getElementById('typingIndicator');
    let ws;
  
    // Connect to WebSocket
    function connectWebSocket() {
      ws = new WebSocket(`ws://${window.location.host}/ws/chat`);
      
      ws.onopen = function() {
        console.log('WebSocket connected');
        // Add a subtle animation to indicate connection
        sendButton.classList.add('pulse');
        setTimeout(() => sendButton.classList.remove('pulse'), 1000);
      };
      
      ws.onmessage = function(event) {
        // Hide typing indicator with fade out
        typingIndicator.style.animation = 'fadeOut 0.3s forwards';
        
        setTimeout(() => {
          // Hide typing indicator
          typingIndicator.style.display = 'none';
          
          // Add bot message with staggered typing effect
          appendMessage('bot', event.data, true);
          
          // Scroll to bottom with smooth animation
          smoothScrollToBottom();
        }, 300);
      };
      
      ws.onclose = function() {
        console.log('WebSocket disconnected');
        // Show reconnecting message
        const reconnectMsg = document.createElement('div');
        reconnectMsg.className = 'reconnect-message fade-in';
        reconnectMsg.innerHTML = '<div class="spinner-small"></div> Đang kết nối lại...';
        chatBox.appendChild(reconnectMsg);
        
        // Try to reconnect after 2 seconds
        setTimeout(connectWebSocket, 2000);
      };
      
      ws.onerror = function(error) {
        console.error('WebSocket error:', error);
        // Show error message
        const errorMsg = document.createElement('div');
        errorMsg.className = 'error-message slide-in';
        errorMsg.textContent = 'Lỗi kết nối. Đang thử lại...';
        chatBox.appendChild(errorMsg);
      };
    }
    
    connectWebSocket();
  
    // Smooth scroll to bottom of chat
    function smoothScrollToBottom() {
      const scrollHeight = chatBox.scrollHeight;
      const duration = 300; // ms
      const start = chatBox.scrollTop;
      const change = scrollHeight - start - chatBox.clientHeight;
      let startTime = null;
      
      function animateScroll(timestamp) {
        if (!startTime) startTime = timestamp;
        const progress = timestamp - startTime;
        const percent = Math.min(progress / duration, 1);
        
        chatBox.scrollTop = start + change * easeInOutQuad(percent);
        
        if (progress < duration) {
          window.requestAnimationFrame(animateScroll);
        }
      }
      
      // Easing function for smoother animation
      function easeInOutQuad(t) {
        return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
      }
      
      window.requestAnimationFrame(animateScroll);
    }
  
    // Append message to chat with typing effect for bot messages
    function appendMessage(sender, text, useTypingEffect = false) {
      const messageDiv = document.createElement('div');
      messageDiv.className = sender === 'user' ? 'message user-message' : 'message bot-message';
      
      const contentDiv = document.createElement('div');
      contentDiv.className = 'message-content';
      
      if (useTypingEffect && sender === 'bot') {
        // Start with empty content for typing effect
        contentDiv.textContent = '';
        messageDiv.appendChild(contentDiv);
        
        // Add time element
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = `Hôm nay, lúc ${new Date().toLocaleTimeString()}`;
        messageDiv.appendChild(timeDiv);
        
        // Add to chat
        chatBox.appendChild(messageDiv);
        
        // Scroll to see the new message
        smoothScrollToBottom();
        
        // Start typing effect
        let i = 0;
        const typingSpeed = 30; // ms per character
        
        function typeNextChar() {
          if (i < text.length) {
            contentDiv.textContent += text.charAt(i);
            i++;
            smoothScrollToBottom();
            
            // Random variation in typing speed
            const randomDelay = typingSpeed + Math.random() * 20;
            setTimeout(typeNextChar, randomDelay);
          }
        }
        
        typeNextChar();
      } else {
        // Regular message without typing effect
        contentDiv.textContent = text;
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = `Hôm nay, lúc ${new Date().toLocaleTimeString()}`;
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeDiv);
        
        chatBox.appendChild(messageDiv);
      }
    }
  
    // Send message with animation
    function sendMessage() {
      const message = userInput.value.trim();
      if (message && ws && ws.readyState === WebSocket.OPEN) {
        // Add user message to chat with slide-in animation
        appendMessage('user', message);
        
        // Send to server
        ws.send(message);
        
        // Show typing indicator with fade-in
        typingIndicator.style.display = 'block';
        typingIndicator.style.animation = 'fadeIn 0.3s forwards';
        
        // Clear input with animation
        userInput.style.transition = 'all 0.3s';
        userInput.style.background = '#f8f9fa';
        setTimeout(() => {
          userInput.value = '';
          userInput.style.background = '';
        }, 100);
        
        // Scroll to bottom
        smoothScrollToBottom();
        
        // Add subtle animation to send button
        sendButton.classList.add('bounce');
        setTimeout(() => sendButton.classList.remove('bounce'), 1000);
      }
    }
  
    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keypress', function(event) {
      if (event.key === 'Enter') {
        sendMessage();
      }
    });
    
    // Typing animation
    userInput.addEventListener('input', function() {
      if (this.value.trim() !== '') {
        sendButton.classList.add('pulse');
      } else {
        sendButton.classList.remove('pulse');
      }
    });
    
    // Add smooth focus effects
    userInput.addEventListener('focus', function() {
      this.parentElement.classList.add('focused');
    });
    
    userInput.addEventListener('blur', function() {
      this.parentElement.classList.remove('focused');
    });
    
    // Handle browser resize to keep chat scrolled to bottom
    window.addEventListener('resize', smoothScrollToBottom);
  });