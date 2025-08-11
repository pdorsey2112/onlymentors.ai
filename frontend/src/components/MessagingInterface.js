import React, { useState, useEffect } from 'react';

const MessagingInterface = ({ creatorId }) => {
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Mock data for demonstration
  useEffect(() => {
    const mockConversations = [
      {
        id: 'conv_1',
        user_name: 'John Doe',
        user_email: 'john@example.com',
        last_message: 'Thank you for the great advice!',
        last_message_time: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
        unread_count: 2
      },
      {
        id: 'conv_2', 
        user_name: 'Sarah Smith',
        user_email: 'sarah@example.com',
        last_message: 'Could you help me with my business strategy?',
        last_message_time: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
        unread_count: 0
      }
    ];
    setConversations(mockConversations);
  }, []);

  const handleConversationSelect = (conversation) => {
    setSelectedConversation(conversation);
    
    // Mock messages for the conversation
    const mockMessages = [
      {
        id: 'msg_1',
        sender_type: 'user',
        sender_name: conversation.user_name,
        content: 'Hi! I really enjoyed your content on leadership. Could you give me some advice?',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 4), // 4 hours ago
        read: true
      },
      {
        id: 'msg_2',
        sender_type: 'creator',
        sender_name: 'You',
        content: 'Thank you for reaching out! I\'d be happy to help. What specific area of leadership are you looking to improve?',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 3), // 3 hours ago
        read: true
      },
      {
        id: 'msg_3',
        sender_type: 'user',
        sender_name: conversation.user_name,
        content: 'I\'m struggling with team motivation and communication. Any tips?',
        created_at: new Date(Date.now() - 1000 * 60 * 60), // 1 hour ago
        read: false
      }
    ];
    setMessages(mockMessages);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedConversation) return;

    setIsLoading(true);

    // Create new message
    const message = {
      id: `msg_${Date.now()}`,
      sender_type: 'creator',
      sender_name: 'You',
      content: newMessage,
      created_at: new Date(),
      read: true
    };

    // Add to messages
    setMessages(prev => [...prev, message]);
    setNewMessage('');

    // Update conversation last message
    setConversations(prev =>
      prev.map(conv =>
        conv.id === selectedConversation.id
          ? { ...conv, last_message: newMessage, last_message_time: new Date() }
          : conv
      )
    );

    setIsLoading(false);
  };

  const formatTime = (date) => {
    const now = new Date();
    const diffMs = now - date;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) {
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } else if (diffHours > 0) {
      return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else {
      const diffMinutes = Math.floor(diffMs / (1000 * 60));
      return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
    }
  };

  return (
    <div className="flex h-[600px] bg-white rounded-lg border border-gray-200 overflow-hidden">
      {/* Conversations List */}
      <div className="w-1/3 border-r border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Messages</h3>
          <p className="text-sm text-gray-600">{conversations.length} conversation{conversations.length !== 1 ? 's' : ''}</p>
        </div>
        
        <div className="overflow-y-auto h-full">
          {conversations.length === 0 ? (
            <div className="p-6 text-center">
              <div className="text-gray-400 mb-2">
                <svg className="w-12 h-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.954 8.954 0 01-4.906-1.414L3 21l2.414-5.094A8.954 8.954 0 013 12c0-4.418 3.582-8 8-8s8 3.582 8 8z" />
                </svg>
              </div>
              <p className="text-gray-600 text-sm">No messages yet</p>
              <p className="text-gray-500 text-xs mt-1">Messages from subscribers will appear here</p>
            </div>
          ) : (
            conversations.map(conversation => (
              <div
                key={conversation.id}
                onClick={() => handleConversationSelect(conversation)}
                className={`p-4 cursor-pointer hover:bg-gray-50 border-b border-gray-100 ${
                  selectedConversation?.id === conversation.id ? 'bg-purple-50 border-purple-200' : ''
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center mb-1">
                      <p className="text-sm font-semibold text-gray-900 truncate">
                        {conversation.user_name}
                      </p>
                      {conversation.unread_count > 0 && (
                        <span className="ml-2 bg-purple-600 text-white text-xs rounded-full px-2 py-1">
                          {conversation.unread_count}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 truncate">{conversation.last_message}</p>
                  </div>
                  <div className="flex-shrink-0 ml-2">
                    <p className="text-xs text-gray-500">
                      {formatTime(conversation.last_message_time)}
                    </p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Messages View */}
      <div className="flex-1 flex flex-col">
        {selectedConversation ? (
          <>
            {/* Message Header */}
            <div className="p-4 border-b border-gray-200 bg-gray-50">
              <h4 className="text-lg font-semibold text-gray-900">
                {selectedConversation.user_name}
              </h4>
              <p className="text-sm text-gray-600">{selectedConversation.user_email}</p>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map(message => (
                <div
                  key={message.id}
                  className={`flex ${message.sender_type === 'creator' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.sender_type === 'creator'
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-200 text-gray-900'
                    }`}
                  >
                    <p className="text-sm">{message.content}</p>
                    <p
                      className={`text-xs mt-1 ${
                        message.sender_type === 'creator' ? 'text-purple-200' : 'text-gray-500'
                      }`}
                    >
                      {formatTime(message.created_at)}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Message Input */}
            <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-200">
              <div className="flex space-x-3">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Type a message..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
                <button
                  type="submit"
                  disabled={!newMessage.trim() || isLoading}
                  className="px-6 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? '...' : 'Send'}
                </button>
              </div>
            </form>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="text-gray-400 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.954 8.954 0 01-4.906-1.414L3 21l2.414-5.094A8.954 8.954 0 013 12c0-4.418 3.582-8 8-8s8 3.582 8 8z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Select a conversation</h3>
              <p className="text-gray-600">Choose a conversation from the left to start messaging</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessagingInterface;