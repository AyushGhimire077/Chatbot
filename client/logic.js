const sendMessage = async () => {
  const userInput = document.getElementById("userInput"); 
  const typingAnimation = document.querySelector(".typing-animation");
 
  if (!userInput.value) {
    return console.log("User input not found");
  }

  
  const message = userInput.value;
  chatbox.innerHTML += `<div class="user-message"><b>You:</b> ${message}</div>`;
  userInput.value = ""
  
  typingAnimation.style.display = "inline-block";
  chatbox.scrollTop = chatbox.scrollHeight; 
  
  try {
    const response = await fetch("http://localhost:8000/chatbot", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: message }),
    });
    
    if (response.ok) {
      const data = await response.json();
      const AIResponse = data.message || "No response";

      const chatbox = document.getElementById("chatbox");
      chatbox.innerHTML += `<div class="ai-message"><b>AI:</b> ${AIResponse}</div>`;
      typingAnimation.style.display = "none"
    }
    else {
      const chatbox = document.getElementById("chatbox");
      typingAnimation.style.display = "none";
       chatbox.innerHTML += `<div class="ai-message">Something went wrong</div>`;
    }
    
    chatbox.scrollTop = chatbox.scrollHeight

  } catch (error) {
    console.error(error);
  }

}