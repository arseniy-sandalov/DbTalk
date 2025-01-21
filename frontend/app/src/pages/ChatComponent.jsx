import React, { useState, useEffect, useRef } from 'react';
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css';
import {
  MainContainer, ChatContainer, MessageList, Message, MessageInput, TypingIndicator,
  ConversationHeader, Avatar, InfoButton
} from "@chatscope/chat-ui-kit-react";
import './ChatComponent.css';

const ChatComponent = ({ token, userId }) => {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(0);
  const websocketRef = useRef(null);  // Store WebSocket instance

  useEffect(() => {
    // Fetch existing conversation history when the component mounts
    const fetchConversationHistory = async () => {
      try {
        const response = await fetch(`http://localhost:8000/get-conversation/${userId}`);
        if (response.status === 404) {
          // Create a new conversation if not found
          await createConversation();
        } else if (response.ok) {
          const data = await response.json();
          setConversations([
            {
              id: 0,
              name: "Conversation 1",
              messages: data.conversation.map((msg, index) => ({
                message: msg.content,
                sender: msg.role === 'assistant' ? "Metal Yapi AI assistant" : "user",
                direction: msg.role === 'assistant' ? "incoming" : "outgoing"
              })),
              typing: false
            }
          ]);
        } else {
          throw new Error('Failed to fetch conversation history');
        }
      } catch (error) {
        console.error('Error fetching conversation history:', error);
      }
    };

    const createConversation = async () => {
      try {
        // Create a new conversation with a welcome message
        const initialMessages = [
          {
            role: 'assistant',
            content: "Hello, I am Metal Yapi AI assistant. How can I help you?"
          }
        ];

        await fetch('http://localhost:8000/create-conversation/${userId}', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: userId,
            conversation: initialMessages
          }),
        });

        // Initialize the conversation in state
        setConversations([
          {
            id: 0,
            name: "Conversation 1",
            messages: initialMessages.map((msg) => ({
              message: msg.content,
              sender: msg.role === 'assistant' ? "Metal Yapi AI assistant" : "user",
              direction: msg.role === 'assistant' ? "incoming" : "outgoing"
            })),
            typing: false
          }
        ]);
      } catch (error) {
        console.error('Error creating new conversation:', error);
      }
    };

    fetchConversationHistory();

    // Create WebSocket connection
    websocketRef.current = new WebSocket(`ws://localhost:8000/chat/${userId}?token=${token}`);

    websocketRef.current.onopen = () => {
      console.log('WebSocket connection established');
    };

    websocketRef.current.onmessage = (event) => {
      const data = event.data;
      handleIncomingMessage(data);
    };

    websocketRef.current.onclose = () => {
      console.log('WebSocket connection closed');
    };

    websocketRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    // Cleanup on component unmount
    return () => {
      if (websocketRef.current) {
        websocketRef.current.close();
      }
    };
  }, [userId, token]);

  const saveConversationToBackend = async (messages) => {
    try {
      const response = await fetch('http://localhost:8000/save-conversation/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          conversation: messages.map(msg => ({
            role: msg.sender === "Metal Yapi AI assistant" ? "assistant" : "user",
            content: msg.message
          })),
        }),
      });
    
      const data = await response.json();
      if (!response.ok) {
        console.error("Failed to save conversation:", data);
      } else {
        console.log("Conversation saved successfully");
      }
    } catch (error) {
      console.error("Error saving conversation:", error);
    }
  };

  const handleIncomingMessage = (message) => {
    const assistantMessage = {
      message: message,
      sender: "Metal Yapi AI assistant",
      direction: "incoming"
    };
  
    setConversations(prevConversations => {
      const updatedConversations = prevConversations.map(convo => {
        if (convo.id === activeConversationId) {
          return {
            ...convo,
            messages: [...convo.messages, assistantMessage],
            typing: false
          };
        }
        return convo;
      });
      
      // Save the conversation after updating with the assistant's message
      saveConversationToBackend(updatedConversations.find(convo => convo.id === activeConversationId).messages);
      
      return updatedConversations;
    });
  };
  
  const handleSend = (message) => {
    const newMessage = {
      message: message,
      sender: "user",
      direction: "outgoing"
    };
  
    const updatedConversations = conversations.map(convo => {
      if (convo.id === activeConversationId) {
        return {
          ...convo,
          messages: [...convo.messages, newMessage],
          typing: true
        };
      }
      return convo;
    });
  
    setConversations(updatedConversations);
  
    if (websocketRef.current) {
      websocketRef.current.send(message);  // Send message via WebSocket
    }
  };

  const activeConversation = conversations.find(convo => convo.id === activeConversationId);

  return (
    <MainContainer className="chat-container">
      <ChatContainer>
        <ConversationHeader>
          <Avatar
            name="Metal Yapı AI Assistant"
            src="https://www.metalyapi.com/webclip.png"
          />
          <ConversationHeader.Content userName="Metal Yapı AI Assistant" />
          <ConversationHeader.Actions>
            <InfoButton />
          </ConversationHeader.Actions>
        </ConversationHeader>
        <MessageList
          typingIndicator={activeConversation?.typing ? <TypingIndicator content="Assistant is typing" /> : null}>
          {activeConversation?.messages.map((message, i) => (
            <Message key={i} model={message} />
          ))}
        </MessageList>
        <MessageInput
          placeholder="Type message here"
          onSend={handleSend}
        />
      </ChatContainer>
    </MainContainer>
  );
};

export default ChatComponent;
