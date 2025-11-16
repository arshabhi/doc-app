import React, { useState, useRef, useEffect } from 'react';
import { useDocuments } from '../context/DocumentContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Send, Bot, User, Trash2, Download } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { toast } from 'sonner';

interface DocumentChatProps {
  documentId: string | null;
}

export function DocumentChat({ documentId }: DocumentChatProps) {
  const { getDocument, chatMessages, sendMessage, clearChat } = useDocuments();
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const document = documentId ? getDocument(documentId) : null;
  const relevantMessages = documentId ? chatMessages.filter(msg => msg.documentId === documentId) : [];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [relevantMessages]);

  const handleSend = async () => {
    if (!message.trim() || !documentId || sending) return;

    setSending(true);
    try {
      await sendMessage(documentId, message);
      setMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClearChat = async () => {
    if (!documentId) return;
    
    try {
      await clearChat(documentId);
      toast.success('Chat history cleared successfully');
    } catch (error) {
      console.error('Failed to clear chat:', error);
      toast.error('Failed to clear chat history');
    }
  };

  const handleExportChat = () => {
    if (!document || relevantMessages.length === 0) return;

    let content = `Chat Conversation\n\nDocument: ${document.name}\nExported: ${new Date().toLocaleString()}\n\n`;
    content += '─'.repeat(60) + '\n\n';

    relevantMessages.forEach((msg, index) => {
      const role = msg.role === 'user' ? 'You' : 'AI Assistant';
      const timestamp = new Date(msg.timestamp).toLocaleTimeString();
      content += `[${timestamp}] ${role}:\n${msg.content}\n\n`;
    });

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat_${document.name.replace(/\.[^/.]+$/, '')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Chat conversation exported successfully');
  };

  if (!document) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Chat with Document</CardTitle>
          <CardDescription>Select a document to start chatting</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <Bot className="w-16 h-16 text-gray-300 mb-4" />
          <p className="text-gray-500 text-center">
            Choose a document from your library to ask questions and get insights
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="flex flex-col h-[600px]">
      <CardHeader className="flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex-1 min-w-0">
            <CardTitle>Chat with Document</CardTitle>
            <CardDescription className="mt-1 truncate">
              {document.name}
            </CardDescription>
          </div>
          {relevantMessages.length > 0 && (
            <div className="flex gap-2 ml-4">
              <Button variant="outline" size="sm" onClick={handleExportChat}>
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
              <Button variant="outline" size="sm" onClick={handleClearChat}>
                <Trash2 className="w-4 h-4 mr-2" />
                Clear Chat
              </Button>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col min-h-0 p-0">
        <div className="flex-1 overflow-y-auto px-6">
          <div className="space-y-4 py-4">
            {relevantMessages.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Bot className="w-12 h-12 text-gray-300 mb-3" />
                <p className="text-gray-500">
                  Start a conversation about this document
                </p>
                <p className="text-sm text-gray-400 mt-2">
                  Ask questions, request summaries, or explore key topics
                </p>
              </div>
            ) : (
              relevantMessages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex gap-3 ${
                    msg.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
                      <Bot className="w-5 h-5 text-indigo-600" />
                    </div>
                  )}
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      msg.role === 'user'
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    {msg.role === 'assistant' ? (
                      <div className="text-xs text-gray-700 leading-relaxed">
                        <ReactMarkdown 
                          remarkPlugins={[remarkGfm]}
                          components={{
                            p: ({children}) => <p className="mb-2.5 last:mb-0">{children}</p>,
                            h1: ({children}) => <h1 className="text-xs font-semibold mt-3 mb-2 first:mt-0 text-gray-900">{children}</h1>,
                            h2: ({children}) => <h2 className="text-xs font-semibold mt-2.5 mb-1.5 first:mt-0 text-gray-900">{children}</h2>,
                            h3: ({children}) => <h3 className="text-xs font-semibold mt-2 mb-1.5 first:mt-0 text-gray-800">{children}</h3>,
                            ul: ({children}) => <ul className="list-disc list-inside mb-2.5 space-y-1">{children}</ul>,
                            ol: ({children}) => <ol className="list-decimal list-inside mb-2.5 space-y-1">{children}</ol>,
                            li: ({children}) => <li className="ml-2">{children}</li>,
                            strong: ({children}) => <strong className="font-semibold text-gray-900">{children}</strong>,
                            em: ({children}) => <em className="italic">{children}</em>,
                            code: ({children}) => <code className="bg-gray-200 px-1.5 py-0.5 rounded text-[11px] font-mono">{children}</code>,
                            pre: ({children}) => <pre className="bg-gray-200 p-2 rounded text-[11px] font-mono overflow-x-auto mb-2.5">{children}</pre>,
                            blockquote: ({children}) => <blockquote className="border-l-2 border-gray-400 pl-3 italic mb-2.5">{children}</blockquote>,
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      <p className="text-xs whitespace-pre-wrap">{msg.content}</p>
                    )}
                    <p
                      className={`text-xs mt-1 ${
                        msg.role === 'user' ? 'text-indigo-200' : 'text-gray-500'
                      }`}
                    >
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                  {msg.role === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                      <User className="w-5 h-5 text-gray-600" />
                    </div>
                  )}
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
        <div className="border-t p-4 flex-shrink-0">
          <div className="flex gap-2">
            <Input
              placeholder="Ask a question about this document..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={sending}
            />
            <Button onClick={handleSend} disabled={sending || !message.trim()}>
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}