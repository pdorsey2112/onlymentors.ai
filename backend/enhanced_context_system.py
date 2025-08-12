# OnlyMentors.ai - User Question Context System Documentation & Enhancement
# Option 4: User Question Context System Explanation and Improvement

"""
CURRENT USER QUESTION CONTEXT SYSTEM ANALYSIS:

The OnlyMentors.ai platform currently implements a sophisticated question-response system with the following context retention and conversation management:

1. **Question Storage System**:
   - All user questions are stored in MongoDB `questions` collection
   - Each question document contains:
     * question_id (UUID)
     * user_id (links to user)
     * category (business, sports, health, science, relationships)
     * mentor_ids (array of selected mentors)
     * question (the actual question text)
     * responses (array of mentor responses)
     * created_at (timestamp)

2. **Session-Based Context Management**:
   - Each mentor-question interaction creates a unique session_id
   - Session ID format: "mentor_{mentor_id}_{hash(question) % 10000}"
   - LlmChat uses session_id for conversation continuity
   - This enables context retention across similar questions to the same mentor

3. **Current Limitations**:
   - No cross-question context (each question is independent)
   - No conversation threads or follow-up question handling
   - Limited conversation memory beyond individual sessions
   - No user conversation history integration with mentor responses

4. **User History Access**:
   - GET /api/questions/history provides last 50 questions
   - Sorted by created_at (most recent first)
   - Full context available including mentor responses

PROPOSED ENHANCEMENTS:

The following improvements will create a more intelligent, context-aware conversation system.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
import uuid

# Enhanced Models for Improved Context System

class ConversationThread(BaseModel):
    thread_id: str
    user_id: str
    mentor_id: str
    title: str
    category: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    is_active: bool = True

class ConversationMessage(BaseModel):
    message_id: str
    thread_id: str
    user_id: str
    mentor_id: str
    message_type: str  # "question" or "response"
    content: str
    context_summary: Optional[str] = None
    created_at: datetime

class ContextualQuestionRequest(BaseModel):
    category: str
    mentor_ids: List[str]
    question: str
    thread_id: Optional[str] = None  # For follow-up questions
    include_history: bool = True

class EnhancedContext:
    """Enhanced context management for user questions and mentor responses"""
    
    @staticmethod
    def generate_thread_id():
        return f"thread_{uuid.uuid4().hex[:12]}"
    
    @staticmethod
    def generate_message_id():
        return f"msg_{uuid.uuid4().hex[:12]}"
    
    @staticmethod
    async def create_conversation_thread(db, user_id: str, mentor_id: str, 
                                       first_question: str, category: str) -> str:
        """Create a new conversation thread between user and mentor"""
        thread_id = EnhancedContext.generate_thread_id()
        
        # Generate thread title from first question (first 50 chars)
        title = first_question[:50] + "..." if len(first_question) > 50 else first_question
        
        thread_doc = {
            "thread_id": thread_id,
            "user_id": user_id,
            "mentor_id": mentor_id,
            "title": title,
            "category": category,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "message_count": 0,
            "is_active": True
        }
        
        await db.conversation_threads.insert_one(thread_doc)
        return thread_id
    
    @staticmethod
    async def add_message_to_thread(db, thread_id: str, user_id: str, 
                                  mentor_id: str, message_type: str, 
                                  content: str, context_summary: str = None):
        """Add a message to a conversation thread"""
        message_id = EnhancedContext.generate_message_id()
        
        message_doc = {
            "message_id": message_id,
            "thread_id": thread_id,
            "user_id": user_id,
            "mentor_id": mentor_id,
            "message_type": message_type,
            "content": content,
            "context_summary": context_summary,
            "created_at": datetime.utcnow()
        }
        
        await db.conversation_messages.insert_one(message_doc)
        
        # Update thread message count and timestamp
        await db.conversation_threads.update_one(
            {"thread_id": thread_id},
            {
                "$inc": {"message_count": 1},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return message_id
    
    @staticmethod
    async def get_conversation_history(db, thread_id: str, limit: int = 10) -> List[Dict]:
        """Get conversation history for context"""
        messages = await db.conversation_messages.find(
            {"thread_id": thread_id}
        ).sort("created_at", 1).limit(limit).to_list(limit)
        
        return messages
    
    @staticmethod
    async def build_contextual_prompt(db, mentor: Dict, current_question: str, 
                                    thread_id: str = None) -> str:
        """Build enhanced prompt with conversation context"""
        
        base_prompt = f"""You are {mentor['name']}, {mentor['expertise']}. {mentor['wiki_description']}

Personality and Communication Style:
- Respond as if you are actually {mentor['name']}
- Use your authentic voice, personality, and speaking patterns
- Draw from your real-life experiences, achievements, and philosophy
- Provide practical, actionable advice based on your expertise
- Keep responses conversational yet insightful (2-3 paragraphs)
- Use "I" statements and personal anecdotes where appropriate
- Reflect your known values, beliefs, and approach to life/work

Areas of Expertise: {mentor['expertise']}"""

        if thread_id:
            # Get conversation history for context
            history = await EnhancedContext.get_conversation_history(db, thread_id, limit=5)
            
            if history:
                context_prompt = "\n\nCONVERSATION CONTEXT:\n"
                context_prompt += "Previous messages in this conversation:\n"
                
                for msg in history:
                    if msg["message_type"] == "question":
                        context_prompt += f"User asked: {msg['content']}\n"
                    else:
                        context_prompt += f"You responded: {msg['content'][:200]}...\n"
                
                context_prompt += f"\nNow the user is asking: {current_question}\n"
                context_prompt += "Please provide a response that acknowledges this conversation history and builds upon previous discussions when relevant."
                
                return base_prompt + context_prompt
        
        return base_prompt + f"\n\nUser Question: {current_question}\n\nYour response should feel authentic to who you are as a person and thought leader."
    
    @staticmethod
    async def get_user_conversation_threads(db, user_id: str, mentor_id: str = None) -> List[Dict]:
        """Get user's conversation threads, optionally filtered by mentor"""
        query = {"user_id": user_id, "is_active": True}
        if mentor_id:
            query["mentor_id"] = mentor_id
        
        threads = await db.conversation_threads.find(query).sort("updated_at", -1).to_list(50)
        return threads
    
    @staticmethod
    async def create_context_summary(content: str) -> str:
        """Create a brief summary for context (can be enhanced with AI)"""
        # Simple summary for now - can be enhanced with LLM summarization
        words = content.split()
        if len(words) <= 20:
            return content
        return " ".join(words[:20]) + "..."

# Enhanced Question Processing System

class EnhancedQuestionProcessor:
    """Enhanced question processing with context awareness"""
    
    @staticmethod
    async def process_contextual_question(db, question_data: ContextualQuestionRequest, 
                                        current_user: Dict, mentor: Dict) -> Dict:
        """Process question with enhanced context management"""
        
        thread_id = question_data.thread_id
        
        # Create new thread if this is a new conversation
        if not thread_id:
            thread_id = await EnhancedContext.create_conversation_thread(
                db, current_user["user_id"], mentor["id"], 
                question_data.question, question_data.category
            )
        
        # Add user question to conversation thread
        await EnhancedContext.add_message_to_thread(
            db, thread_id, current_user["user_id"], mentor["id"],
            "question", question_data.question
        )
        
        # Build contextual prompt
        contextual_prompt = await EnhancedContext.build_contextual_prompt(
            db, mentor, question_data.question, thread_id if question_data.include_history else None
        )
        
        # Generate mentor response with context
        response_text = await EnhancedQuestionProcessor.generate_contextual_response(
            mentor, question_data.question, contextual_prompt, thread_id
        )
        
        # Add mentor response to conversation thread
        context_summary = await EnhancedContext.create_context_summary(response_text)
        await EnhancedContext.add_message_to_thread(
            db, thread_id, current_user["user_id"], mentor["id"],
            "response", response_text, context_summary
        )
        
        return {
            "thread_id": thread_id,
            "mentor": mentor,
            "response": response_text,
            "context_enabled": question_data.include_history
        }
    
    @staticmethod
    async def generate_contextual_response(mentor: Dict, question: str, 
                                         contextual_prompt: str, thread_id: str):
        """Generate mentor response with enhanced context"""
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            import os
            
            # Use thread_id as session_id for conversation continuity
            session_id = f"thread_{thread_id}" if thread_id else f"mentor_{mentor['id']}_{hash(question) % 10000}"
            
            # Initialize LLM chat with contextual prompt
            chat = LlmChat(
                api_key=os.getenv("OPENAI_API_KEY"),
                session_id=session_id,
                system_message=contextual_prompt
            ).with_model("openai", "gpt-4o-mini")
            
            # Create user message
            user_message = UserMessage(text=question)
            
            # Get AI response with timeout handling
            import asyncio
            response = await asyncio.wait_for(chat.send_message(user_message), timeout=30.0)
            
            return response.strip()
            
        except Exception as e:
            print(f"❌ Enhanced LLM API Error for {mentor['name']}: {str(e)}")
            return f"Thank you for your question about '{question}'. Based on my experience in {mentor['expertise']}, I believe this is an important topic that requires thoughtful consideration. While I'd love to provide a detailed response right now, I encourage you to explore this further and perhaps rephrase your question for the best guidance. {mentor['wiki_description']}"

# Conversation Analytics and Insights

class ConversationAnalytics:
    """Analytics for conversation patterns and context usage"""
    
    @staticmethod
    async def get_conversation_stats(db, user_id: str) -> Dict:
        """Get user's conversation statistics"""
        
        # Count total threads
        thread_count = await db.conversation_threads.count_documents({
            "user_id": user_id, 
            "is_active": True
        })
        
        # Count total messages
        message_count = await db.conversation_messages.count_documents({
            "user_id": user_id
        })
        
        # Get most active mentors
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$mentor_id", 
                "message_count": {"$sum": 1}
            }},
            {"$sort": {"message_count": -1}},
            {"$limit": 5}
        ]
        
        most_active = await db.conversation_messages.aggregate(pipeline).to_list(5)
        
        # Get conversation frequency (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_activity = await db.conversation_messages.count_documents({
            "user_id": user_id,
            "created_at": {"$gte": thirty_days_ago}
        })
        
        return {
            "total_threads": thread_count,
            "total_messages": message_count,
            "most_active_mentors": most_active,
            "recent_activity_30d": recent_activity,
            "avg_messages_per_thread": message_count / thread_count if thread_count > 0 else 0
        }
    
    @staticmethod
    async def get_context_effectiveness_metrics(db, user_id: str) -> Dict:
        """Analyze the effectiveness of contextual conversations"""
        
        # Get threads with multiple messages (indicating ongoing conversations)
        active_threads = await db.conversation_threads.find({
            "user_id": user_id,
            "message_count": {"$gte": 4},  # At least 2 questions and 2 responses
            "is_active": True
        }).to_list(100)
        
        context_metrics = {
            "multi_turn_conversations": len(active_threads),
            "avg_messages_per_active_thread": 0,
            "longest_conversation": 0,
            "mentors_with_ongoing_conversations": len(set(t["mentor_id"] for t in active_threads))
        }
        
        if active_threads:
            context_metrics["avg_messages_per_active_thread"] = sum(t["message_count"] for t in active_threads) / len(active_threads)
            context_metrics["longest_conversation"] = max(t["message_count"] for t in active_threads)
        
        return context_metrics