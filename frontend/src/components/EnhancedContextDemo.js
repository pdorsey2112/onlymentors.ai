import React, { useState, useEffect, useRef } from 'react';
import { getBackendURL } from '../config';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { 
  MessageSquare, History, BarChart3, Archive, RefreshCw, 
  User, Bot, Clock, Hash, ArrowRight, Zap, Info
} from 'lucide-react';

const EnhancedContextDemo = ({ onClose }) => {
  const [activeTab, setActiveTab] = useState('explanation');
  const [threads, setThreads] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [selectedThread, setSelectedThread] = useState(null);
  const [threadMessages, setThreadMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Demo conversation data
  const [demoQuestion, setDemoQuestion] = useState('What are the key principles for building a successful startup?');
  const [selectedMentor, setSelectedMentor] = useState('steve_jobs');
  const [includeHistory, setIncludeHistory] = useState(true);

  useEffect(() => {
    if (activeTab === 'threads') {
      loadConversationThreads();
    } else if (activeTab === 'analytics') {
      loadAnalytics();
    }
  }, [activeTab]);

  const loadConversationThreads = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('auth_token');
      const backendURL = getBackendURL();
      
      const response = await fetch(`${backendURL}/api/conversations/threads`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setThreads(data.threads || []);
      } else {
        setError('Failed to load conversation threads');
      }
    } catch (err) {
      setError('Network error while loading threads');
    } finally {
      setLoading(false);
    }
  };

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('auth_token');
      const backendURL = getBackendURL();
      
      const response = await fetch(`${backendURL}/api/conversations/analytics`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      } else {
        setError('Failed to load analytics');
      }
    } catch (err) {
      setError('Network error while loading analytics');
    } finally {
      setLoading(false);
    }
  };

  const loadThreadMessages = async (threadId) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('auth_token');
      const backendURL = getBackendURL();
      
      const response = await fetch(`${backendURL}/api/conversations/threads/${threadId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSelectedThread(data.thread);
        setThreadMessages(data.messages || []);
      } else {
        setError('Failed to load thread messages');
      }
    } catch (err) {
      setError('Network error while loading thread');
    } finally {
      setLoading(false);
    }
  };

  const askContextualQuestion = async () => {
    try {
      setLoading(true);
      setError('');
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/questions/ask-contextual`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          category: 'business',
          mentor_ids: [selectedMentor],
          question: demoQuestion,
          include_history: includeHistory
        })
      });

      if (response.ok) {
        const data = await response.json();
        alert(`Contextual question processed successfully!\nThread ID: ${data.thread_ids[0]}\nContext enabled: ${data.context_enabled}`);
        
        if (activeTab === 'threads') {
          loadConversationThreads();
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to ask contextual question');
      }
    } catch (err) {
      setError('Network error while asking question');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-purple-600 to-blue-600 text-white">
          <h2 className="text-2xl font-bold">Enhanced Question Context System</h2>
          <button 
            onClick={onClose}
            className="text-white hover:text-gray-200 text-2xl font-bold"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b">
          {[
            { id: 'explanation', label: 'System Explanation', icon: Info },
            { id: 'demo', label: 'Live Demo', icon: Zap },
            { id: 'threads', label: 'Conversation Threads', icon: MessageSquare },
            { id: 'analytics', label: 'Analytics', icon: BarChart3 }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 flex items-center space-x-2 font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-purple-600 text-purple-600 bg-purple-50'
                  : 'border-transparent text-gray-600 hover:text-gray-800 hover:border-gray-300'
              }`}
            >
              <tab.icon className="w-5 h-5" />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          {error && (
            <Alert className="mb-4 border-red-200 bg-red-50">
              <AlertDescription className="text-red-800">{error}</AlertDescription>
            </Alert>
          )}

          {/* System Explanation Tab */}
          {activeTab === 'explanation' && (
            <div className="space-y-6">
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-4">
                  How OnlyMentors.ai Retains Question Context
                </h3>
                <p className="text-lg text-gray-600">
                  Advanced conversation management system that maintains context across multiple interactions
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <History className="w-5 h-5 mr-2 text-blue-600" />
                      Current System
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">Question Storage</h4>
                      <p className="text-sm text-gray-600">
                        All questions stored in MongoDB with metadata: user_id, mentor_ids, responses, timestamps
                      </p>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">Session Management</h4>
                      <p className="text-sm text-gray-600">
                        Unique session IDs per mentor-question: mentor_{`{mentor_id}`}_{`{hash(question)}`}
                      </p>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">History Access</h4>
                      <p className="text-sm text-gray-600">
                        GET /api/questions/history provides last 50 questions with full context
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Zap className="w-5 h-5 mr-2 text-green-600" />
                      Enhanced Features
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">Conversation Threads</h4>
                      <p className="text-sm text-gray-600">
                        Multi-turn conversations with maintained context across questions
                      </p>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">Contextual Responses</h4>
                      <p className="text-sm text-gray-600">
                        Mentors acknowledge previous exchanges and build upon earlier discussions
                      </p>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">Analytics & Insights</h4>
                      <p className="text-sm text-gray-600">
                        Track conversation patterns, engagement, and context effectiveness
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <ArrowRight className="w-5 h-5 mr-2 text-purple-600" />
                    Technical Implementation
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-3 gap-6">
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">Database Structure</h4>
                      <ul className="text-sm text-gray-600 space-y-1">
                        <li>• conversation_threads</li>
                        <li>• conversation_messages</li>
                        <li>• enhanced_prompts</li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">New API Endpoints</h4>
                      <ul className="text-sm text-gray-600 space-y-1">
                        <li>• /api/questions/ask-contextual</li>
                        <li>• /api/conversations/threads</li>
                        <li>• /api/conversations/analytics</li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">User Benefits</h4>
                      <ul className="text-sm text-gray-600 space-y-1">
                        <li>• Context-aware responses</li>
                        <li>• Conversation continuity</li>
                        <li>• Personalized experience</li>
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Live Demo Tab */}
          {activeTab === 'demo' && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <h3 className="text-xl font-bold text-gray-900 mb-2">Test Enhanced Context System</h3>
                <p className="text-gray-600">Try the new contextual question asking with conversation threads</p>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Contextual Question Demo</CardTitle>
                  <CardDescription>Ask a question with enhanced context awareness</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Question
                    </label>
                    <Textarea
                      value={demoQuestion}
                      onChange={(e) => setDemoQuestion(e.target.value)}
                      placeholder="Enter your question here..."
                      rows={3}
                    />
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Select Mentor
                      </label>
                      <select
                        value={selectedMentor}
                        onChange={(e) => setSelectedMentor(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500"
                      >
                        <option value="steve_jobs">Steve Jobs</option>
                        <option value="bill_gates">Bill Gates</option>
                        <option value="warren_buffett">Warren Buffett</option>
                        <option value="elon_musk">Elon Musk</option>
                      </select>
                    </div>

                    <div className="flex items-center">
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={includeHistory}
                          onChange={(e) => setIncludeHistory(e.target.checked)}
                          className="rounded border-gray-300 mr-2"
                        />
                        <span className="text-sm text-gray-700">Include conversation history</span>
                      </label>
                    </div>
                  </div>

                  <Button
                    onClick={askContextualQuestion}
                    className="w-full bg-purple-600 hover:bg-purple-700"
                    disabled={loading || !demoQuestion.trim()}
                  >
                    {loading ? 'Processing...' : 'Ask Contextual Question'}
                  </Button>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Conversation Threads Tab */}
          {activeTab === 'threads' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold text-gray-900">Conversation Threads</h3>
                <Button
                  onClick={loadConversationThreads}
                  variant="outline"
                  size="sm"
                  disabled={loading}
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Refresh
                </Button>
              </div>

              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                  <span className="ml-3 text-gray-600">Loading threads...</span>
                </div>
              ) : threads.length === 0 ? (
                <Card>
                  <CardContent className="text-center py-8">
                    <MessageSquare className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">No Conversation Threads</h4>
                    <p className="text-gray-600 mb-4">Start asking contextual questions to create conversation threads</p>
                    <Button
                      onClick={() => setActiveTab('demo')}
                      className="bg-purple-600 hover:bg-purple-700"
                    >
                      Try Demo
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {threads.map((thread) => (
                    <Card key={thread.thread_id} className="hover:shadow-lg transition-shadow cursor-pointer">
                      <CardHeader 
                        className="pb-3"
                        onClick={() => loadThreadMessages(thread.thread_id)}
                      >
                        <CardTitle className="text-lg line-clamp-2">{thread.title}</CardTitle>
                        <CardDescription>
                          <div className="flex items-center justify-between text-xs">
                            <span>{thread.category}</span>
                            <Badge variant="secondary">{thread.message_count} messages</Badge>
                          </div>
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="text-sm text-gray-600 space-y-1">
                          <div className="flex items-center">
                            <Clock className="w-4 h-4 mr-1" />
                            {formatDate(thread.updated_at)}
                          </div>
                          <div className="flex items-center">
                            <Hash className="w-4 h-4 mr-1" />
                            {thread.thread_id}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}

              {/* Thread Details Modal */}
              {selectedThread && (
                <Card className="mt-6">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>Thread: {selectedThread.title}</span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedThread(null)}
                      >
                        Close
                      </Button>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4 max-h-96 overflow-y-auto">
                      {threadMessages.map((msg, index) => (
                        <div key={msg.message_id || index} className="flex items-start space-x-3">
                          <div className={`p-2 rounded-full ${
                            msg.message_type === 'question' ? 'bg-blue-100' : 'bg-green-100'
                          }`}>
                            {msg.message_type === 'question' ? 
                              <User className="w-4 h-4 text-blue-600" /> : 
                              <Bot className="w-4 h-4 text-green-600" />
                            }
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-1">
                              <span className="font-medium text-sm">
                                {msg.message_type === 'question' ? 'You' : 'Mentor'}
                              </span>
                              <span className="text-xs text-gray-500">
                                {formatDate(msg.created_at)}
                              </span>
                            </div>
                            <p className="text-sm text-gray-700">{msg.content}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* Analytics Tab */}
          {activeTab === 'analytics' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold text-gray-900">Conversation Analytics</h3>
                <Button
                  onClick={loadAnalytics}
                  variant="outline"
                  size="sm"
                  disabled={loading}
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Refresh
                </Button>
              </div>

              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                  <span className="ml-3 text-gray-600">Loading analytics...</span>
                </div>
              ) : !analytics ? (
                <Card>
                  <CardContent className="text-center py-8">
                    <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">No Analytics Data</h4>
                    <p className="text-gray-600">Start conversations to see analytics</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {/* Basic Stats */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Basic Statistics</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Total Threads:</span>
                        <span className="font-semibold">{analytics.conversation_stats.total_threads}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Total Messages:</span>
                        <span className="font-semibold">{analytics.conversation_stats.total_messages}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Recent Activity (30d):</span>
                        <span className="font-semibold">{analytics.conversation_stats.recent_activity_30d}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Avg Messages/Thread:</span>
                        <span className="font-semibold">{analytics.conversation_stats.avg_messages_per_thread.toFixed(1)}</span>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Context Metrics */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Context Effectiveness</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Multi-turn Conversations:</span>
                        <span className="font-semibold">{analytics.context_metrics.multi_turn_conversations}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Avg Active Thread Length:</span>
                        <span className="font-semibold">{analytics.context_metrics.avg_messages_per_active_thread.toFixed(1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Longest Conversation:</span>
                        <span className="font-semibold">{analytics.context_metrics.longest_conversation} messages</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Active Mentors:</span>
                        <span className="font-semibold">{analytics.context_metrics.mentors_with_ongoing_conversations}</span>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Generated Info */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Report Info</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Generated At:</span>
                        <span className="font-semibold text-xs">{formatDate(analytics.generated_at)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">User ID:</span>
                        <span className="font-mono text-xs">{analytics.user_id.substring(0, 8)}...</span>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EnhancedContextDemo;