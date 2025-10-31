import React, { useState, useRef, useEffect } from 'react';
import { useDocuments } from '../context/DocumentContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Send, Bot, User, Trash2 } from 'lucide-react';
import { ScrollArea } from './ui/scroll-area';

interface DocumentChatProps {
  documentId: string | null;
}

export function DocumentChat({ documentId }: DocumentChatProps) {
  const { getDocument, chatMessages, sendMessage, clearChat } = useDocuments();
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const document = documentId ? getDocument(documentId) : null;
  const relevantMessages = chatMessages.filter(msg => msg.documentId === documentId);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
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
          <div>
            <CardTitle>Chat with Document</CardTitle>
            <CardDescription className="mt-1">{document.name}</CardDescription>
          </div>
          {relevantMessages.length > 0 && (
            <Button variant="outline" size="sm" onClick={() => documentId && clearChat(documentId)}>
              <Trash2 className="w-4 h-4 mr-2" />
              Clear Chat
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col min-h-0 p-0">
        <ScrollArea className="flex-1 px-6" ref={scrollRef}>
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
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
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
          </div>
        </ScrollArea>
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
