import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, X, Send, Minimize2, Maximize2, Bot, Sparkles, Zap } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import { ApiService } from '../../services/apiService';

const AIChat = () => {
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState('dashboard');
  const messagesEndRef = useRef(null);

  // Page-specific context and suggestions
  const pageContexts = {
    '/': {
      name: 'Dashboard',
      welcome: "👋 Welcome to the Dashboard! I can help you understand fleet performance, top drivers, and session insights. What would you like to know?",
      suggestions: [
        "Who's the fastest driver?",
        "Show me fleet consistency trends",
        "What's the session summary?",
        "Compare top 3 performers"
      ],
      quickActions: [
        { label: "Fleet Stats", icon: "📊" },
        { label: "Top Drivers", icon: "🏆" }
      ]
    },
    '/drivers': {
      name: 'Driver Analysis',
      welcome: "🏎️ I'm here to help with driver analysis! Ask me about specific drivers, coaching insights, or performance metrics.",
      suggestions: [
        "Analyze GR86-063-113's performance",
        "What are the coaching recommendations?",
        "Show me DPTAD anomalies",
        "Compare lap consistency"
      ],
      quickActions: [
        { label: "DPTAD Analysis", icon: "🔍" },
        { label: "Coaching Tips", icon: "💡" }
      ]
    },
    '/compare': {
      name: 'Driver Comparison',
      welcome: "⚔️ Ready to compare drivers! I can help you understand head-to-head performance, sector differences, and consistency gaps.",
      suggestions: [
        "Who has better consistency?",
        "Compare sector times",
        "Explain the lap time delta",
        "Which driver is improving?"
      ],
      quickActions: [
        { label: "Sector Analysis", icon: "📈" },
        { label: "Consistency Gap", icon: "🎯" }
      ]
    },
    '/evidence': {
      name: 'Evidence Explorer',
      welcome: "🔬 Let's dive into the telemetry! I can explain graphs, analyze sectors, and help you understand the data.",
      suggestions: [
        "Explain the telemetry trace",
        "Why is sector 2 slower?",
        "Analyze throttle patterns",
        "What do the anomalies mean?"
      ],
      quickActions: [
        { label: "Telemetry Insights", icon: "📡" },
        { label: "Sector Breakdown", icon: "🎯" }
      ]
    },
    '/strategy': {
      name: 'Strategy Center',
      welcome: "🎮 Strategy mode activated! Ask me about pit stops, tire management, or race tactics.",
      suggestions: [
        "When should I pit?",
        "Optimal tire strategy?",
        "Fuel saving tips",
        "Overtaking opportunities"
      ],
      quickActions: [
        { label: "Pit Strategy", icon: "🛠️" },
        { label: "Race Tactics", icon: "🏁" }
      ]
    }
  };

  // Detect current page and update context
  useEffect(() => {
    const path = location.pathname;
    const page = Object.keys(pageContexts).find(p => path === p || path.startsWith(p)) || '/';
    setCurrentPage(page);

    // Set initial welcome message based on page
    if (messages.length === 0) {
      const context = pageContexts[page];
      setMessages([{
        id: 1,
        type: 'ai',
        text: context.welcome,
        suggestions: context.suggestions,
        timestamp: new Date()
      }]);
    }
  }, [location.pathname]);

  // Update welcome message when page changes
  useEffect(() => {
    if (messages.length > 0 && isOpen) {
      const context = pageContexts[currentPage];
      // Add a contextual message when switching pages
      setMessages(prev => [...prev, {
        id: Date.now(),
        type: 'ai',
        text: `📍 You're now on the ${context.name} page. ${context.welcome}`,
        suggestions: context.suggestions,
        timestamp: new Date()
      }]);
    }
  }, [currentPage]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen]);

  const handleSendMessage = async (messageText) => {
    const text = messageText || inputText;
    if (!text.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: text,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      // Build context from current page and URL
      const pathParts = window.location.pathname.split('/');
      const potentialId = pathParts[pathParts.length - 1];
      const contextId = (potentialId.startsWith('Car-') || potentialId.startsWith('GR86-')) ? potentialId : null;

      let context = {
        page: pageContexts[currentPage]?.name || 'Dashboard',
        path: window.location.pathname
      };

      if (contextId) {
        try {
          const contextData = await ApiService.getAIContext(contextId);
          context = { ...context, ...contextData.context };
        } catch (err) {
          console.warn("Failed to fetch context", err);
        }
      }

      const response = await ApiService.postAIChat(text, context);
      
      // Generate dynamic follow-up suggestions based on response
      const dynamicSuggestions = generateFollowUpSuggestions(text, response.message, currentPage);
      
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        text: response.message,
        suggestions: response.suggestions || dynamicSuggestions,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'error',
        text: "🚧 Connection to pit wall lost. Please try again.",
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Generate intelligent follow-up suggestions
  const generateFollowUpSuggestions = (userQuestion, aiResponse, page) => {
    const lowerQuestion = userQuestion.toLowerCase();
    const lowerResponse = aiResponse.toLowerCase();

    // Context-aware follow-ups
    if (lowerQuestion.includes('fastest') || lowerQuestion.includes('best')) {
      return ["How can they improve?", "Compare with others", "Show sector breakdown"];
    }
    if (lowerQuestion.includes('consistency') || lowerQuestion.includes('variance')) {
      return ["What causes inconsistency?", "Show lap progression", "Coaching tips"];
    }
    if (lowerQuestion.includes('sector') || lowerQuestion.includes('s1') || lowerQuestion.includes('s2')) {
      return ["Analyze telemetry", "Compare sectors", "What's optimal?"];
    }
    if (lowerQuestion.includes('compare') || lowerQuestion.includes('vs')) {
      return ["Show detailed stats", "Sector comparison", "Who's improving?"];
    }
    if (lowerResponse.includes('anomaly') || lowerResponse.includes('issue')) {
      return ["How to fix this?", "Show more details", "Impact on lap time"];
    }

    // Page-specific defaults
    return pageContexts[page]?.suggestions.slice(0, 3) || [
      "Tell me more",
      "Show examples",
      "What else?"
    ];
  };

  const handleSuggestionClick = (suggestion) => {
    handleSendMessage(suggestion);
  };

  const handleQuickAction = (action) => {
    const actionQueries = {
      "Fleet Stats": "Give me a summary of fleet statistics",
      "Top Drivers": "Who are the top performing drivers?",
      "DPTAD Analysis": "Explain the DPTAD analysis results",
      "Coaching Tips": "What are the key coaching recommendations?",
      "Sector Analysis": "Break down the sector performance",
      "Consistency Gap": "Explain the consistency differences",
      "Telemetry Insights": "What do the telemetry graphs show?",
      "Sector Breakdown": "Analyze sector-by-sector performance",
      "Pit Strategy": "What's the optimal pit strategy?",
      "Race Tactics": "Suggest race tactics"
    };
    
    handleSendMessage(actionQueries[action.label] || action.label);
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 bg-gradient-to-r from-racing-red to-red-700 hover:from-red-700 hover:to-racing-red text-white p-4 rounded-full shadow-lg transition-all duration-200 z-50 flex items-center gap-2 group animate-pulse hover:animate-none"
      >
        <Bot className="w-6 h-6" />
        <Sparkles className="w-4 h-4 absolute -top-1 -right-1 text-yellow-400" />
        <span className="max-w-0 overflow-hidden group-hover:max-w-xs transition-all duration-300 whitespace-nowrap">
          AI Assistant
        </span>
      </button>
    );
  }

  const currentContext = pageContexts[currentPage];

  return (
    <div className={`fixed bottom-6 right-6 bg-racing-black border border-racing-silver/30 rounded-xl shadow-2xl z-50 transition-all duration-300 flex flex-col ${isMinimized ? 'w-72 h-14' : 'w-80 md:w-96 h-[600px]'}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-racing-silver/20 bg-gradient-to-r from-racing-gray/50 to-racing-gray/30 rounded-t-xl">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <h3 className="font-bold text-white flex items-center gap-2">
            <Bot className="w-4 h-4 text-racing-red" />
            AI Assistant
          </h3>
          <span className="text-xs text-racing-silver/70">• {currentContext.name}</span>
        </div>
        <div className="flex items-center gap-2">
          <button 
            onClick={() => setIsMinimized(!isMinimized)}
            className="text-racing-silver hover:text-white transition-colors"
          >
            {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
          </button>
          <button 
            onClick={() => setIsOpen(false)}
            className="text-racing-silver hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {/* Quick Actions */}
          <div className="p-3 border-b border-racing-silver/10 bg-racing-gray/20">
            <div className="flex gap-2 flex-wrap">
              {currentContext.quickActions.map((action, idx) => (
                <button
                  key={idx}
                  onClick={() => handleQuickAction(action)}
                  className="text-xs bg-racing-red/20 hover:bg-racing-red/40 text-racing-red px-3 py-1.5 rounded-full transition-colors border border-racing-red/30 flex items-center gap-1"
                >
                  <span>{action.icon}</span>
                  <span>{action.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-lg p-3 ${
                    msg.type === 'user'
                      ? 'bg-gradient-to-r from-racing-red to-red-700 text-white'
                      : msg.type === 'error'
                      ? 'bg-red-900/50 text-red-200 border border-red-800'
                      : 'bg-racing-gray text-white border border-racing-silver/20'
                  }`}
                >
                  <p className="text-sm leading-relaxed">{msg.text}</p>
                  {msg.suggestions && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {msg.suggestions.map((suggestion, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSuggestionClick(suggestion)}
                          className="text-xs bg-black/30 hover:bg-black/50 text-racing-red px-2 py-1 rounded-full transition-colors border border-racing-red/30 flex items-center gap-1"
                        >
                          <Zap className="w-3 h-3" />
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  )}
                  <span className="text-[10px] opacity-50 block mt-1 text-right">
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-racing-gray p-3 rounded-lg border border-racing-silver/20">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-racing-red rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-racing-red rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-racing-red rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }} className="p-4 border-t border-racing-silver/20 bg-racing-gray/30 rounded-b-xl">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder={`Ask about ${currentContext.name.toLowerCase()}...`}
                className="flex-1 bg-racing-black border border-racing-silver/30 rounded-lg px-3 py-2 text-sm text-white placeholder-racing-silver/50 focus:outline-none focus:border-racing-red transition-colors"
              />
              <button
                type="submit"
                disabled={isLoading || !inputText.trim()}
                className="bg-gradient-to-r from-racing-red to-red-700 hover:from-red-700 hover:to-racing-red disabled:opacity-50 disabled:cursor-not-allowed text-white p-2 rounded-lg transition-all"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </form>
        </>
      )}
    </div>
  );
};

export default AIChat;
